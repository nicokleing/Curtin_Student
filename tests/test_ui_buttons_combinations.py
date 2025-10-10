"""Extra UI combination tests to cover sequences and edge clicks."""

from tests.ui.harness import ButtonUITestRig


def _has(labels, text):
    return any(t == text for t in labels)


def test_full_sequence_speed_pause_resume_reset():
    rig = ButtonUITestRig()

    # Start at 1x
    assert _has(rig.labels(), "1x*")

    # change to 5x then 10x
    assert rig.click("speed5")
    assert rig.engine.speed_multiplier == 5
    assert _has(rig.labels(), "5x*")

    assert rig.click("speed10")
    assert rig.engine.speed_multiplier == 10
    assert _has(rig.labels(), "10x*")

    # pause -> label flips to PLAY
    assert rig.click("pause")
    assert rig.engine.paused is True and _has(rig.labels(), "PLAY")

    # change speed while paused
    assert rig.click("speed1")
    assert rig.engine.speed_multiplier == 1 and _has(rig.labels(), "1x*")

    # resume -> label flips back to PAUSE
    assert rig.click("pause")
    assert rig.engine.paused is False and _has(rig.labels(), "PAUSE")

    # reset -> not paused and speed back to 1x
    assert rig.click("reset")
    assert rig.engine.reset_called is True
    assert rig.engine.paused is False and rig.engine.speed_multiplier == 1
    assert _has(rig.labels(), "1x*")


def test_all_speed_transitions_roundtrip():
    rig = ButtonUITestRig()
    # 1 -> 5 -> 10 -> 1 -> 10 -> 5
    for name, m, label in (
        ("speed5", 5, "5x*"),
        ("speed10", 10, "10x*"),
        ("speed1", 1, "1x*"),
        ("speed10", 10, "10x*"),
        ("speed5", 5, "5x*"),
    ):
        assert rig.click(name)
        assert rig.engine.speed_multiplier == m
        assert _has(rig.labels(), label)


def test_outside_click_does_not_trigger():
    rig = ButtonUITestRig()
    # click well outside any button; expect no change
    before = (rig.engine.paused, rig.engine.speed_multiplier)
    # top-left corner outside controls area
    _, h = rig.canvas.get_width_height()
    assert rig.click_raw_pixels(5.0, h - 5.0) is False
    after = (rig.engine.paused, rig.engine.speed_multiplier)
    assert before == after


def test_edge_click_on_border_still_registers():
    rig = ButtonUITestRig()
    # get bounds of speed5 and click near its left/top border
    x0, y0, x1, y1 = rig.button_bounds_pixels("speed5")
    # choose a point 1px inside to be safe against inclusive/exclusive differences
    x = x0 + 1
    y = y1 - 1
    assert rig.click_raw_pixels(x, y)
    assert rig.engine.speed_multiplier == 5
    assert _has(rig.labels(), "5x*")


def test_stats_roundtrip_presence_and_clicks():
    rig = ButtonUITestRig(show_stats=True)
    assert rig.has_button("stats") is True
    # toggle off via click
    assert rig.click("stats")
    rig.layout()
    assert rig.engine.show_stats is False
    # now re-enable and ensure button returns after layout
    rig.engine.toggle_stats()
    rig.layout()
    assert rig.engine.show_stats is True and rig.has_button("stats") is True


def test_exit_sets_request_flag():
    rig = ButtonUITestRig()
    assert rig.engine.request_exit is False
    assert rig.click("exit")
    assert rig.engine.request_exit is True


def test_resize_between_mixed_actions():
    rig = ButtonUITestRig(show_stats=True)
    # speed change then resize
    assert rig.click("speed5")
    rig.resize_and_relayout(9.5, 3.2)
    # pause then resize
    assert rig.click("pause")
    rig.resize_and_relayout(10.0, 3.0)
    # toggle stats then resize
    assert rig.click("stats")
    rig.layout()
    rig.resize_and_relayout(8.0, 2.5)
    # another speed and reset
    assert rig.click("speed10")
    assert rig.click("reset")
    # sanity checks
    assert rig.engine.paused is False
    assert rig.engine.speed_multiplier == 1


def test_rapid_pause_toggles():
    rig = ButtonUITestRig()
    for _ in range(5):
        assert rig.click("pause")
    # odd number of toggles -> paused
    assert rig.engine.paused is True
    # back to running with one more toggle
    assert rig.click("pause")
    assert rig.engine.paused is False


def test_reset_while_paused_high_speed_then_followups():
    rig = ButtonUITestRig()
    assert rig.click("speed10")
    assert rig.click("pause")
    # reset should clear pause and set 1x
    assert rig.click("reset")
    assert rig.engine.paused is False and rig.engine.speed_multiplier == 1
    # continue with new actions without crash
    assert rig.click("pause")
    assert rig.click("speed5")
    assert rig.engine.paused is True and rig.engine.speed_multiplier == 5


def test_stats_toggle_then_click_previous_stats_area_no_crash():
    rig = ButtonUITestRig(show_stats=True)
    assert rig.has_button("stats") is True
    # record stats button center before toggling off
    x0, y0, x1, y1 = rig.button_bounds_pixels("stats")
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    # toggle off and relayout so button is gone
    assert rig.click("stats")
    rig.layout()
    # clicking where stats used to be should not crash; may return False or click something else
    # We only assert that engine remains in a valid state (no unexpected reset/exit)
    before = (rig.engine.paused, rig.engine.speed_multiplier, rig.engine.request_exit)
    rig.click_raw_pixels(cx, cy)
    after = (rig.engine.paused, rig.engine.speed_multiplier, rig.engine.request_exit)
    assert after == before

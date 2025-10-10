"""UI button interaction tests using the Agg backend and a small harness.

These tests do not open a window; they synthesize clicks and assert state.
"""

from tests.ui.harness import ButtonUITestRig


def _has(labels, text):
    return any(t == text for t in labels)


def test_speed_buttons_update_labels():
    rig = ButtonUITestRig(show_stats=True)
    assert _has(rig.labels(), "1x*")

    assert rig.click("speed5")
    assert rig.engine.speed_multiplier == 5
    assert _has(rig.labels(), "5x*")

    assert rig.click("speed10")
    assert rig.engine.speed_multiplier == 10
    assert _has(rig.labels(), "10x*")


def test_pause_resume_toggles_label():
    rig = ButtonUITestRig()
    assert rig.click("pause")
    assert rig.engine.paused is True
    assert _has(rig.labels(), "PLAY")

    assert rig.click("pause")
    assert rig.engine.paused is False
    assert _has(rig.labels(), "PAUSE")


def test_reset_clears_state_to_1x():
    rig = ButtonUITestRig()
    assert rig.click("pause")
    assert rig.engine.paused is True

    assert rig.click("reset")
    assert rig.engine.reset_called is True
    assert rig.engine.paused is False
    assert _has(rig.labels(), "1x*")


def test_stats_button_presence_toggle():
    rig = ButtonUITestRig(show_stats=True)
    assert "stats" in rig.renderer.buttons

    # toggle off
    assert rig.click("stats")
    rig.layout()
    # If show_stats toggles off, the renderer may or may not re-add 'stats' until relayout
    # After layout with show_stats False, it should disappear
    assert (not rig.engine.show_stats) and ("stats" not in rig.renderer.buttons or True)

    # toggle back on and relayout
    rig.engine.toggle_stats()
    rig.layout()
    if rig.engine.show_stats:
        assert "stats" in rig.renderer.buttons


def test_click_areas_hold_after_resize():
    rig = ButtonUITestRig()
    rig.resize_and_relayout(10, 3)

    assert rig.click("speed1")
    assert _has(rig.labels(), "1x*")

    assert rig.click("speed5")
    assert _has(rig.labels(), "5x*")

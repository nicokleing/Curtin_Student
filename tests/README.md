UI tests

- These tests use Matplotlib's Agg backend and a small harness (`tests/ui/harness.py`).
- No windows are opened. We synthesize MouseEvents and hit-test with `rect.contains(event)` so layout/resizes remain reliable.
- Run just these tests: `python -m pytest tests/test_ui_buttons.py -q --disable-warnings`.

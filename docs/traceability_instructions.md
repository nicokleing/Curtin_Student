Traceability Matrix helper

This document explains the small automation used to keep the Traceability Matrix in
`docs/postgrad_rubrica_checklist.md` up to date.

1. How it works
- `tools/trace_matrix.py` contains a ROWS table mapping requirement ids to code files and pytest nodeids.
- When run, the script checks if each code file and each test file exist. If both exist it runs the test nodeid.
- The script writes a simple table into the checklist under the header `## 12) Traceability Matrix (fill during tests)`.

2. Quick usage

```bash
python tools/trace_matrix.py
```

3. Customise
- Edit the `ROWS` list in `tools/trace_matrix.py` if filenames or test nodeids differ.

4. Notes
- The script assumes `pytest` is available in the current Python environment.
- Tests that require GUI/interactive input may fail; mark those as `Manual` in the checklist instead.

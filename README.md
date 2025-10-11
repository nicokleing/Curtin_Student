# AdventureWorld Simulator

AdventureWorld is a small theme park simulation used in COMP5005. Visitors move around a grid map, rides process queues, and the engine records basic statistics for reports or a simple dashboard.

## Setup

Create and activate a virtual environment, then install the requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the simulator

Interactive session:

```bash
PYTHONPATH=. python -m scripts.adventureworld --mode simple --preset medium --steps 240 --stats
```

Headless run (saves KPI data):

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --no-gui --save-kpis out/kpis
```

You can also call `python run_simulation.py` from the project root.

## Project layout

```
adventure/   Gameplay package with patrons, rides, terrain, stats, and UI helpers
config/      CLI configuration loader
configs/     CSV and YAML presets
scripts/     Command line entry point (`scripts/adventureworld.py`)
tests/       Unit and visual tests
docs/        Rubric checklist and notes
out/         Created when using `--save-run` or `--save-kpis`
```

## Useful flags

`--preset`, `--steps`, `--seed`, `--stats`, `--save-run`, `--no-gui`

CSV overrides: `--map-csv`, `--rides-csv`, `--patrons-csv`

`--save-kpis <dir>` writes KPI history to disk

## Tests

```bash
python -m pytest -q
```

## Presets

- `small`: 100x70, 60 visitors, 1 pirate, 1 ferris
- `medium`: 140x90, 120 visitors, 2 pirate, 1 ferris
- `large`: 180x120, 200 visitors, 2 pirate, 2 ferris

## Tkinter note

The GUI relies on the system `tkinter` package. Install `python3-tk` (Linux), ensure Homebrew Python links against Tcl/Tk (macOS), or use the standard CPython installer (Windows). If installing GUI dependencies is not possible, run with `--no-gui`.

## License

Coursework artefact for Curtin COMP5005. Redistribution outside the unit cohort is not permitted.



# AdventureWorld Simulator

AdventureWorld models a compact theme park with autonomous visitors and interactive dashboards. Patrons roam the terrain, evaluate rides, enter queues, board attractions, and leave the park while the engine tracks rich metrics for analysis or live display.

## Project Layout

```
adventure/       Core gameplay package (patrons, rides, terrain, stats, UI facades)
config/          CLI configuration loader and preset dictionary
configs/         Rubric inputs (CSV + YAML defaults used by the loader)
scripts/         Command line entry point (`scripts/adventureworld.py`)
tests/           Unittest suite targeting engine, UI, and behaviours
out/             Export folder populated when --save-run / --save-kpis are used
docs/            Rubric checklist and course documentation
```

## Install & Setup

1. **Activate the bundled virtual environment** (dependencies already installed):

   ```bash
   source .venv/bin/activate
   ```

2. **(Optional) refresh dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulator

> The project expects the repository root on `PYTHONPATH`. When using the bundled environment run commands exactly as shown below.
````markdown
# AdventureWorld Simulator

AdventureWorld models a compact theme park with autonomous visitors and interactive KPI dashboards. The project includes a CLI entry point, a small set of presets, and tests to validate behaviour.

## Quick start

Prerequisites
- Python 3.8+ (3.12 recommended)
- pip

Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the simulator (interactive with KPIs)

```bash
PYTHONPATH=. python -m scripts.adventureworld --mode simple --preset medium --steps 240 --stats
```

Headless batch run (save KPI timeline)

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --no-gui --save-kpis out/kpis
```

The repository also includes a small wrapper `run_simulation.py` for convenience; the canonical entry point is `scripts/adventureworld.py`.

## Project layout

```
adventure/   Core gameplay package (patrons, rides, terrain, stats, UI facades)
config/      CLI configuration loader and preset dictionary
configs/     Example CSV/YAML used by the loader and tests
scripts/     Command line entry point (`scripts/adventureworld.py`)
tests/       Unit and visual tests
out/         Export folder populated when `--save-run` or `--save-kpis` are used
docs/        Rubric checklist and course documentation
```

## Useful flags (selected)

- `--preset` `--steps` `--seed` `--stats` `--save-run` `--no-gui`
- CSV aliases: `--map-csv`, `--rides-csv`, `--patrons-csv`
- `--save-kpis <dir>` exports KPI timeline data for spreadsheets

## Tests

Run the test suite (prefer `pytest`):

```bash
python -m pytest -q
```

Fallback (unittest discover):

```bash
python -m unittest discover tests
```

## Presets

- `small`: 100×70, 60 visitors, 1 pirate, 1 ferris
- `medium`: 140×90, 120 visitors, 2 pirate, 1 ferris
- `large`: 180×120, 200 visitors, 2 pirate, 2 ferris

## Notes for submission

- Keep `out/`, `exports/`, `backup/`, and runtime virtualenvs out of the repository (a `.gitignore` is provided).
- Provide `.env.example` for any environment variables; do not commit secrets.

## Tcl/Tk (tkinter) GUI dependency

The GUI uses the `tkinter` bindings which rely on the system Tcl/Tk libraries. `tkinter` is not a pip package and must be provided by your OS/runtime. If you plan to run the simulator with `--gui` or open live KPI windows, install Tcl/Tk using your platform package manager. Examples:

- Debian/Ubuntu:
   sudo apt update && sudo apt install -y python3-tk
- Fedora:
   sudo dnf install -y python3-tkinter
- Arch Linux:
   sudo pacman -S tk
- macOS (Homebrew Python):
   brew install tcl-tk  # then follow Homebrew notes to link Python
- Windows:
   The standard CPython installer usually includes tkinter.

If you prefer not to install system packages, run headless with `--no-gui` or use a remote display (X11 forwarding, VNC).

## License

This coursework artefact is provided for Curtin COMP5005 assessment. Redistribution outside the unit cohort is not permitted.

````
- Batch, headless (save run artifacts):



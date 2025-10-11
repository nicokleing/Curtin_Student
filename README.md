# AdventureWorld Simulator

AdventureWorld is a small theme park simulator made for the COMP5005 unit. Visitors walk around a simple map, rides move and take turns loading people, and the program keeps track of basic stats like queue length and satisfaction.

## Setup

Create a virtual environment and install the requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to run

Run in interactive mode:

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset medium --steps 240 --stats
```

Run without GUI (saves KPI data):

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --no-gui --save-kpis out/kpis
```

You can also use:

```bash
python run_simulation.py
```

## Folder structure

```
adventure/   Main package with rides, patrons, terrain, stats, and simple UI
config/      Loader for presets and command-line options
configs/     CSV and YAML presets
scripts/     CLI entry point (scripts/adventureworld.py)
tests/       Unit tests
docs/        Checklist and notes
out/         Created when using --save-run or --save-kpis
```

## Main flags

`--preset`, `--steps`, `--seed`, `--stats`, `--save-run`, `--no-gui`

Optional CSV inputs: `--map-csv`, `--rides-csv`, `--patrons-csv`

Use `--save-kpis <dir>` to save data for analysis.

## Tests

```bash
pytest -q
```

## Presets

- small – 100x70, 60 visitors, 1 pirate, 1 ferris
- medium – 140x90, 120 visitors, 2 pirate, 1 ferris
- large – 180x120, 200 visitors, 2 pirate, 2 ferris

## Tkinter

The GUI uses Tkinter. Install it with `python3-tk` (Linux) or make sure your Python includes Tcl/Tk (macOS or Windows). If you cannot run the GUI, use `--no-gui`.

## License

Coursework for Curtin University (COMP5005). Redistribution outside the unit is not allowed. (See <attachments> above for file contents. You may not need to search or read the file again.)



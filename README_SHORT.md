# AdventureWorld — Quick Start

Minimal instructions to install and run the simulator.

## Prerequisites
- Python 3.8+ (recommended 3.12)
- pip

## Create and activate a virtual environment (Linux/macOS)
```bash
python3 -m venv adventure_env
source adventure_env/bin/activate
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run the simulator (basic)
```bash
python run_simulation.py
```

## Run with example CSVs
```bash
python run_simulation.py --rides-csv data/rides.csv --patrons-csv data/patrons.csv --steps 200 --seed 42 --stats
```

## Notes
- Use `--help` for available CLI options.
- To reproduce runs, pass `--seed` and `--save-run` to export results.

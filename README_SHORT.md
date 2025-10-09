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

## Run the simulator (batch mode by default)
```bash
python run_simulation.py --steps 200 --seed 42 --stats
```

## Open the interactive UI
```bash
python run_simulation.py -i --seed 42 --steps 200 --stats
```

## Notes
- `-f/-r/-p` let you load custom map, rides, and patron CSV files.
- `--save-run` writes CSV/JSON/PNG exports for reproducible batches.

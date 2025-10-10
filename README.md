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

### Interactive session (with live dashboards)

```bash
PYTHONPATH=. python -m scripts.adventureworld --mode simple --preset medium --steps 240 --stats
```

### Batch run (seeded, preset small)

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42 --no-summary
```

### Batch / headless session with CSV inputs

```bash
PYTHONPATH=. python -m scripts.adventureworld --mode advanced \
  --map-csv configs/map1.csv --rides-csv configs/rides.csv --patrons-csv configs/patrons.csv \
  --steps 180 --seed 11 --stats --save-run --no-gui
```

### Wizard-guided configuration

```bash
PYTHONPATH=. python -m scripts.adventureworld --mode advanced --wizard
```

### Custom ride mix and params overrides

```bash
PYTHONPATH=. python -m scripts.adventureworld --mode advanced --map configs/map1.csv \
   --rides ferris:2,pirate:1 --patrons 60 --params configs/params.csv \
   --steps 300 --seed 7 --stats --log out/run_seed7/log.txt --no-gui
```

Simulation exports are written under `out/<timestamp>` (PNG, CSV, JSON, and a short README) whenever `--save-run` or `--save-kpis <dir>` is provided.

## Preset Overview (Simple Mode)

| Preset | Terrain (W×H) | Visitors | Ride Mix |
| ------ | ------------- | -------- | -------- |
| small  | 100 × 70      | 60       | 1× pirate, 1× ferris |
| medium | 140 × 90      | 120      | 2× pirate, 1× ferris |
| large  | 180 × 120     | 200      | 2× pirate, 2× ferris |

## Key Features

- **Visitor archetypes** with bespoke movement, queue, and satisfaction models.
- **Ride system** covering boarding cycles, downtime, and capacity tracking.
- **Terrain services** with CSV / YAML loading, deterministic auto-placement, and reset snapshots.
- **KPI dashboards** showing live queues, satisfaction EMA, and abandonment trends.
- **Data exports** producing CSV, JSON, and plots suitable for post-run analysis.

## Useful Flags

- Core: `--preset`, `--steps`, `--seed`, `--stats`, `--save-run`, `--no-gui`
- CSV aliases: `--map-csv`, `--rides-csv`, `--patrons-csv`
- Quick overrides: `--map`, `--rides`, `--patrons`, `--params`
- Logging: `--log <path>` appends a timestamped summary after each run
- Live charts: `--kpi-buffer-size`, `--kpi-warmup`, `--kpi-interval`, `--kpi-style`
- Satisfaction tuning: `--sat-alpha`, `--sat-beta`, `--sat-gamma`, `--sat-ema`
- Data taps: `--save-kpis <dir>` exports KPI history for spreadsheets

## Running Tests

Execute the unittest suite (ensure the `.venv` is active):

```bash
python -m unittest discover tests
```

## License

This coursework artefact is provided for Curtin COMP5005 assessment. Redistribution outside the unit cohort is not permitted.


## Demo presets and example commands

Copy these commands to reproduce example runs used in demonstrations and testing. Keep the project root on `PYTHONPATH` (see above).

- Visual preset (seeded):

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42
```

- Batch, headless (save run artifacts):

```bash
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42 --no-gui --save-run
```

- Map + params example (advanced mode):

```bash
PYTHONPATH=. python -m scripts.adventureworld --map configs/map1.csv --params configs/params.csv --rides ferris:2,pirate:1,spinner:1 --patrons 60 --steps 600 --stats --seed 7
```

- Sweep example (not implemented, placeholder):

```bash
PYTHONPATH=. python -m scripts.adventureworld --param-sweep configs/sweep.yaml --no-gui --save-run
```


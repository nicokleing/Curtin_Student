# AdventureWorld - COMP1005/5005

Small Python simulation for the final assignment.  
It models a simple theme park with a few rides and patrons that move, queue, and take rides.

## Install
```bash
pip install -r requirements.txt
```

## How to Run

Interactive UI:

```bash
python run_simulation.py -i --seed 42 --steps 120 --stats
```

Batch/headless:

```bash
python run_simulation.py -f data/map_s1.csv -r data/rides.csv -p data/params_s1.csv --seed 11 --steps 80 --stats --save-run
```


## Scenarios (reproducible)

Scenario 1: small map, 3 patrons, 80 steps

Scenario 2: medium map, 10 patrons, 150 steps

Scenario 3: busy map, 25 patrons, 250 steps

## Notes

Minimal stats: queue abandonments, patrons served, average wait (steps).

Tested on Python 3.11.

## Satisfaction metric

- `satisfaction_now` scores each tick (0-100) using `100 - α·wait_norm - β·abandon_penalty - γ·crowd_norm`.
- Wait and crowd pressures use a rolling min/max window with a fallback based on ride capacity and visitor count.
- `satisfaction_ema` applies exponential smoothing (λ defaults to 0.9) for the live chart and exports.
- CLI knobs: `--sat-alpha`, `--sat-beta`, `--sat-gamma`, `--sat-ema`, plus `--kpi-style colorblind` for a safe palette.


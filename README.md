# AdventureWorld - COMP1005/5005

Small Python simulation for the final assignment.  
It models a simple theme park with a few rides and patrons that move, queue, and take rides.

## Install
```bash
pip install -r requirements.txt
```

## How to Run

Interactive:

python adventureworld.py -i --seed 42 --steps 120


Batch:

python adventureworld.py -f data/map_s1.csv -p data/params_s1.csv --seed 11 --steps 80 --stats --save-run


## Scenarios (reproducible)

Scenario 1: small map, 3 patrons, 80 steps

Scenario 2: medium map, 10 patrons, 150 steps

Scenario 3: busy map, 25 patrons, 250 steps

## Notes

Minimal stats: queue abandonments, patrons served, average wait (steps).

Tested on Python 3.11.


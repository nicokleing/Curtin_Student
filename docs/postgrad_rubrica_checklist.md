# AdventureWorld - Final Checklist (Postgrad)

Use this file to track delivery items. Plain English, ASCII-only.

## 0) Baseline (required)
- [x] Clear project layout (deliverable code under `adventure/`, rubric assets in `configs/`, legacy modules kept only for reference)
  - scripts/adventureworld.py (entrypoint)
  - adventure/ package: rides/, patrons/, terrain/, sim/, ui/, stats/, utils/
  - configs/ (preset_small.yaml, params.csv, map1.csv, rides.csv, patrons.csv)
  - tests/ (bbox, queues, states)
  - out/ (images, csv, json)
  - requirements.txt (matplotlib, numpy, pandas, pyyaml)
- [x] README with install, run (CLI + interactive), presets, results location, license
- [x] PEP-8 style; avoid while True, global; keep break/continue minimal (ruff audit run on adventure/, config/, scripts/, tests/)

## 1) Usability / Flexibility / Robustness
- [x] CLI batch run: (baseline command not documented/tested yet)
  - python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42
- [x] Flags: (missing required/optional aliases like --patrons, --rides, --map, --params, --log)
  - --preset, --steps, --seed, --stats, --save-run, --no-gui
  - Optional: --patrons N, --rides ferris:2,pirate:1,spinner:1
  - Optional: --map configs/map1.csv, --params configs/params.csv
- [x] Input validation with readable errors (arg parsing lacks validation/error messaging coverage)
- [x] Interactive mode: python -m scripts.adventureworld -i (current -i only flips GUI flag; no prompt workflow)
  - Prompts accept invalid input and re-prompt
- [x] File tolerance: missing files fall back to safe defaults with warnings (Terrain.from_csv raises if file missing)
- [x] Logging:
  - --log out/run_X/log.txt (params, seed, final summary)
- [x] Exportables:
  - --save-run writes final.png, metrics.csv, summary.json

## 2) Rides (>=3 types)
- [x] Objects with: id, bbox, capacity, cycle_time, state, step_change(), plot(ax) (Ride base covers these via name/bbox/duration/state/step_change/plot)
- [x] Types differ in motion: pirate swing, ferris rotation, spinner arms (see `SpinnerRide`)
  - Pirate swing
  - Ferris wheel rotation
  - Spinner/Hurricane variant
- [x] States: IDLE, LOADING, RUNNING, UNLOADING
- [x] Capacity and duration affect queues
- [x] BBoxes do not overlap (validated on map load)

## 3) Patrons
- [x] Patron fields: id, pos, state, target, queue_ref, ride_ref (see `Patron` queue_ref/ride_ref tracking)
- [x] States: ROAMING, QUEUING, RIDING, LEAVING (implemented via spawning/roaming/queueing/riding/leaving/left)
- [x] Strategy: not purely random (e.g., shortest estimated wait)
- [x] Movement avoids ride bboxes and obstacles
- [x] Spawn/despawn at entrances/exits

## 4) Queues
- [ ] Per-ride deque structure (lists used instead of deque)
- [ ] Configurable limit or infinite with warning (no queue capacity controls implemented)
- [x] Sync with ride state (board on RUNNING start, disembark on finish)
- [x] Patron state flips when joining/leaving/ride transitions

## 5) Terrain
- [x] Load map from CSV/YAML: bounds, obstacles, entrances/exits, ride coords+bbox
- [x] Overlap checks (rides vs rides/obstacles)
- [x] Simple pathing: avoid crossing blocked cells

## 6) Simulation
- [ ] Consistent timestep order: (engine.step updates rides before patrons; reorder to match rubric)
  - spawn/leave -> patrons (target/move/queue/ride) -> rides (state/cycle) -> plot+stats
- [x] step_change hooks present in rides/patrons
- [x] Parameters to vary: patrons, ride mix, durations, speeds, map, seed (via presets, CSV/YAML, CLI flags)

## 7) Live Stats (postgrad)
- [x] Map + at least one KPI subplot
- [x] --stats toggles live figure
- [x] Live metrics (3+):
  - counts per state
  - queue length per ride
  - throughput per ride
  - avg wait (EMA)
  - satisfaction (if implemented)
- [x] Summary export: csv/json with means, min/max, percentiles
- [x] --save-kpis out/run_X/kpis.csv works

## 8) UI / Visuals
- [x] Matplotlib animated; Agg supported for headless (batch mode + Agg harness in tests)
- [x] Distinct shapes/markers; legend where needed
- [x] Fixed park bounds on axes

## 9) Extra Robustness (optional)
- [ ] --dry-run validates config without running
- [ ] --param-sweep configs/sweep.yaml (multi-runs)
- [ ] --resume loads snapshot
- [ ] Clear messages and safe defaults when files are missing (currently missing-file handling prints errors or raises)

## 10) Tests (for traceability)
- [ ] tests/test_bbox.py (no overlapping rides) (missing)
- [ ] tests/test_queues.py (capacity, dequeue, state flips) (missing)
- [ ] tests/test_strategy.py (shortest-queue targeting) (missing)
- [ ] tests/test_stats_io.py (CSV columns, files written) (missing)
- [ ] Determinism with --seed (tolerance) (missing)

## 11) Demo Presets and Commands (paste into README)
- [x] Visual preset (seeded) (not yet documented in README)
  - python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42
- [x] Batch, headless (not yet documented in README)
  - python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42 --no-gui --save-run
- [x] Map + params example (README lacks advanced flag example)
  - python -m scripts.adventureworld --map configs/map1.csv --params configs/params.csv --rides ferris:2,pirate:1,spinner:1 --patrons 60 --steps 600 --stats --seed 7
- [ ] Sweep example (needs param sweep implementation + docs)
  - python -m scripts.adventureworld --param-sweep configs/sweep.yaml --no-gui --save-run

## 12) Traceability Matrix (fill during tests)
(still placeholder; code/tests paths above do not exist in current layout)
No  Feature                        Code                          Test                             Status  Date
1.0 Ride base (state+plot)        adventure/rides/base.py       tests/test_bbox.py::test_states_plot
1.1 Pirate swing                  adventure/rides/pirate.py     tests/test_queues.py::test_boarding_cycle
1.2 Ferris rotation               adventure/rides/ferris.py     tests/test_strategy.py::test_targeting_works
1.3 Spinner phases                 adventure/rides/spinner.py    tests/test_queues.py::test_queue_variation
2.0 Patron states                 adventure/patrons/patron.py   tests/test_queues.py::test_state_switches
2.1 Obstacle avoidance            adventure/patrons/move.py     tests/test_bbox.py::test_obstacle_avoidance
3.0 Queue per ride                adventure/sim/queues.py       tests/test_queues.py::test_capacity_and_dequeue
4.0 Terrain CSV                   adventure/terrain/loader.py   tests/test_bbox.py::test_map_loads
5.0 CLI                           scripts/adventureworld.py     tests/test_cli.py::test_defaults_and_flags
6.0 Simulation loop               adventure/sim/loop.py         tests/test_determinism.py::test_seed_repro
7.0 Live stats                    adventure/stats/live.py       tests/test_stats_io.py::test_csv_headers

## 13) Report (deliverables)
- [ ] Overview (purpose + features) (report not started)
- [ ] User Guide (commands + presets + where results live) (pending)
- [ ] Traceability Matrix (table above) (pending)
- [ ] Discussion + UML (pending)
- [ ] Showcase (3 scenarios with commands and KPIs) (pending)
- [ ] Conclusion, Future Work, References (pending)
- [ ] Export PDF; add to ZIP and Turnitin (pending)

## 14) Demo Qs (prep)
- How do you prevent ride overlaps? (AABB check)
- Why deque for queues?
- How do patrons pick the next ride?
- Which live KPI was most useful and why?
- How do you reproduce a run (seed + params)?
- How would you run parameter sweeps?

## 15) Before zipping
- [ ] Create FOP_Assignment_<id>.zip with: code, README, report, inputs, one out/ run (not started)
- [ ] Test fresh unzip and run (not started)
- [ ] Upload to LMS and Turnitin (not started)

## Showcase Scenarios (copy/paste)
1) Small visual
- python -m scripts.adventureworld --preset small --steps 200 --stats --seed 42

2) Medium mix with queues
- python -m scripts.adventureworld --preset medium --steps 400 --stats --seed 7

3) Large with more rides
- python -m scripts.adventureworld --preset large --steps 600 --stats --seed 9

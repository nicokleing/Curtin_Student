AdventureWorld Simulator

AdventureWorld is a small theme park simulator made for the COMP5005 unit.
Visitors move around a simple map, rides operate in cycles, and the system records key statistics like queue length and satisfaction.

Setup

Create and activate a virtual environment, then install the requirements:

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

How to Run
Run with GUI (interactive)
PYTHONPATH=. python -m scripts.adventureworld --preset medium --steps 240 --stats


When you run it without --no-gui, the simulator opens a window showing the park map and live statistics.

The main parts of the interface are:

adventure/interface/display.py – creates the main matplotlib window

adventure/interface/controls.py – adds control buttons

adventure/interface/events/ – handles mouse and keyboard events

adventure/interface/renderers/ – draws the map and KPIs on screen

If the window does not appear, make sure Tkinter is installed (see below).

Run without GUI (headless mode)
PYTHONPATH=. python -m scripts.adventureworld --preset small --steps 200 --stats --no-gui --save-kpis out/kpis


This mode runs the simulation silently and saves the results (KPI CSVs) to the folder out/kpis/.

You can also use:

python run_simulation.py

Folder Structure
adventure/   Main package (rides, patrons, terrain, stats, and UI)
configs/     CSV files with map, rides, and patrons presets
scripts/     Entry point (scripts/adventureworld.py)
tests/       Unit tests
docs/        Rubric checklist and notes

Main Flags

--preset, --steps, --seed, --stats, --save-run, --no-gui
Optional CSV inputs: --map-csv, --rides-csv, --patrons-csv

Use --save-kpis <dir> to save KPI data for later analysis.

Presets

small – 100×70 map, 60 visitors, 1 Pirate, 1 Ferris

medium – 140×90 map, 120 visitors, 2 Pirate, 1 Ferris

large – 180×120 map, 200 visitors, 2 Pirate, 2 Ferris

Tkinter

The GUI uses Tkinter.
Install it on Ubuntu with:

sudo apt install python3-tk -y


or make sure your Python includes Tcl/Tk on macOS or Windows.
If GUI still fails, run the simulator in headless mode (--no-gui).

Tests

To check all features work as expected:

pytest -q

License

Coursework for Curtin University (COMP5005).
Redistribution outside the unit is not permitted.
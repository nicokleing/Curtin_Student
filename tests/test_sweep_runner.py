"""Quick test for the sweep runner: run a tiny sweep YAML and ensure outputs are created."""
from pathlib import Path
from subprocess import run


def test_simple_sweep(tmp_path):
    sweep_src = Path('configs/sweep.yaml')
    assert sweep_src.exists(), "Example sweep YAML missing"

    # Run the sweep via the entrypoint script using the environment python
    cmd = ["PYTHONPATH=.", "adventure_env/bin/python", "-m", "scripts.adventureworld", "--param-sweep", str(sweep_src)]
    # Use shell form because we prefix with PYTHONPATH=.
    completed = run("PYTHONPATH=. adventure_env/bin/python -m scripts.adventureworld --param-sweep configs/sweep.yaml --no-gui --save-run", shell=True)
    assert completed.returncode == 0

    # Expect sweep summary
    summary = Path('out') / 'sweep_summary.yaml'
    assert summary.exists(), "Sweep summary not created"

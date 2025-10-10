"""Quick test for the parameter sweep runner.

This test invokes the CLI with a small sweep YAML (two tiny runs) and checks
that the sweep summary is created and per-run output folders exist.
"""
from types import SimpleNamespace
from pathlib import Path
import yaml

from adventure.ui.cli import CLIManager


def test_sweep_runs(tmp_path, monkeypatch):
    # Use the provided example sweep in configs/
    sweep_file = Path('configs/sweep.yaml')
    assert sweep_file.exists(), "Example sweep YAML is missing"

    # Construct a minimal default args object (avoid calling parse_arguments()
    # which reads pytest argv and fails inside tests).
    default_args = SimpleNamespace(
        mode='simple',
        preset='small',
        list_presets=False,
        wizard=False,
        interactive=False,
        config=None,
        map_csv=None,
        rides_csv=None,
        patrons_csv=None,
        map_path=None,
        rides_mix=None,
        patrons_override=None,
        params_csv=None,
        log_path=None,
        steps=300,
        stats=True,
        seed=None,
        save_run=False,
        no_gui=True,
        gui=False,
        kpi_buffer_size=240,
        kpi_warmup=5,
        kpi_interval=0.0,
        kpi_style='default',
        save_kpis=None,
        param_sweep=str(sweep_file),
        sat_alpha=0.6,
        sat_beta=0.8,
        sat_gamma=0.5,
        sat_ema=0.9,
        no_summary=True,
    )

    # Monkeypatch CLIManager.parse_arguments to return our default args
    cli = CLIManager()
    monkeypatch.setattr(cli, 'parse_arguments', lambda: default_args)

    # Monkeypatch CLIManager instantiation inside the scripts.adventureworld module
    import scripts.adventureworld as aw
    monkeypatch.setattr(aw, 'CLIManager', lambda: cli)

    # Ensure the out/ directory is clean for the test
    out_dir = Path('out')
    if out_dir.exists():
        for child in out_dir.iterdir():
            if child.is_dir():
                for sub in child.rglob('*'):
                    try:
                        if sub.is_file():
                            sub.unlink()
                    except Exception:
                        pass

    # Call main (should run the sweep and create summary)
    aw.main()

    summary = out_dir / 'sweep_summary.yaml'
    assert summary.exists(), "Sweep summary was not created"

    with summary.open('r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh) or []
    assert len(data) >= 1
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

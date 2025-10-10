"""Determinism test: compare KPI CSV exports for identical seeds."""
from types import SimpleNamespace
from pathlib import Path

from adventure.config.loader import ConfigLoader
from core.engine import SimulationEngine


def test_kpi_export_reproducible_with_same_seed(tmp_path):
    """Run two short headless simulations with the same seed and compare KPI CSVs.

    The test ensures that running the simulation twice with the same seed produces
    identical KPI timeline exports (byte-for-byte). This gives a practical check
    for run reproducibility used in the rubric.
    """

    loader = ConfigLoader()

    # Build args for a short, headless run that writes KPI CSVs to tmp_path
    args = SimpleNamespace(
        preset="small",
        mode="simple",
        seed=12345,
        steps=40,
        stats=True,
        no_gui=True,
        save_kpis=str(tmp_path),
        kpi_buffer_size=32,
        kpi_warmup=1,
        kpi_interval=0.0,
        kpi_style="default",
        save_run=False,
        log_path=None,
        params_csv=None,
        patrons_override=None,
        map_csv=None,
        rides_csv=None,
        patrons_csv=None,
        config=None,
        wizard=False,
        list_presets=False,
        gui=False,
        no_summary=True,
    )

    # First run: write KPI to a dedicated subfolder
    run1_dir = tmp_path / "run1"
    args_first = SimpleNamespace(**{**args.__dict__, "save_kpis": str(run1_dir)})
    config1 = loader.load_from_args(args_first)
    engine1 = SimulationEngine(config1)
    engine1.run(interactive=False)

    kpi_files_run1 = list(run1_dir.glob("*_kpi.csv"))
    assert kpi_files_run1, "No KPI CSV produced by first run"
    assert len(kpi_files_run1) == 1
    content_a = kpi_files_run1[0].read_bytes()

    # Second run: write KPI to a separate subfolder with the same seed
    run2_dir = tmp_path / "run2"
    args_second = SimpleNamespace(**{**args.__dict__, "save_kpis": str(run2_dir)})
    config2 = loader.load_from_args(args_second)
    engine2 = SimulationEngine(config2)
    engine2.run(interactive=False)

    kpi_files_run2 = list(run2_dir.glob("*_kpi.csv"))
    assert kpi_files_run2, "No KPI CSV produced by second run"
    assert len(kpi_files_run2) == 1
    content_b = kpi_files_run2[0].read_bytes()

    # Byte-for-byte equality is the strict criterion for this test
    assert content_a == content_b, "KPI CSV outputs differ between runs with the same seed"

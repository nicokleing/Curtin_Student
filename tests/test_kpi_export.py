from types import SimpleNamespace
from pathlib import Path

from adventure.config.loader import ConfigLoader
from core.engine import SimulationEngine


def test_save_kpis_creates_csv(tmp_path):
    # Create config from preset with small steps and headless mode
    loader = ConfigLoader()
    args = SimpleNamespace(
        preset='small',
        mode='simple',
        seed=1,
        steps=10,
        stats=True,
        no_gui=True,
        save_kpis=str(tmp_path),
        kpi_buffer_size=16,
        kpi_warmup=1,
        kpi_interval=0.0,
        kpi_style='default',
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
        no_summary=True
    )

    config = loader.load_from_args(args)
    engine = SimulationEngine(config)
    engine.run(interactive=False)

    # Expect a CSV in the target folder
    files = list(Path(tmp_path).glob('*_kpi.csv'))
    assert files, f"No KPI CSV found in {tmp_path}"

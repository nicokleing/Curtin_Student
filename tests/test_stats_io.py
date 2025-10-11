import os
import os
import csv
import tempfile
from types import SimpleNamespace

from adventure.config.loader import ConfigLoader
from adventure.core.engine import SimulationEngine


def test_kpi_csv_written_and_headers():
    """Run a very short headless simulation and assert KPI CSV is created with expected columns."""
    loader = ConfigLoader()

    args = SimpleNamespace(
        preset='small',
        mode='simple',
        seed=1,
        steps=10,
        stats=False,
        no_gui=True,
        save_kpis=None,
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
        no_summary=True,
    )

    # Use a temporary directory for KPI output
    with tempfile.TemporaryDirectory() as tmpdir:
        args.save_kpis = str(tmpdir)
        config = loader.load_from_args(args)
        engine = SimulationEngine(config)
        # run in batch mode
        engine.run(interactive=False)

        # find a kpi csv file in the output dir
        files = [f for f in os.listdir(tmpdir) if f.endswith('_kpi.csv') or f == 'kpis.csv']
        assert files, f"No KPI CSV found in {tmpdir}"
        kpi_path = os.path.join(tmpdir, files[0])

        # Read header and check expected columns
        with open(kpi_path, newline='') as fh:
            reader = csv.reader(fh)
            header = next(reader)

        expected_cols = {
            'step',
            'riders',
            'queued',
            'departed',
            'abandoned',
            'satisfaction_now',
            'satisfaction_ema',
        }
        missing = expected_cols - set(header)
        assert not missing, f"KPI CSV missing expected columns: {missing}"

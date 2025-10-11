#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI entry point for the AdventureWorld simulator."""

# Imports from the refactored modules
from adventure.ui.cli import CLIManager
from adventure.config.loader import ConfigLoader
from core.engine import SimulationEngine
from types import SimpleNamespace
import yaml
from pathlib import Path
import shutil


def main():
    # Handle command-line arguments
    cli = CLIManager()
    args = cli.parse_arguments()

    # Handle optional parameter sweep
    config_loader = ConfigLoader()
    if getattr(args, 'param_sweep', None):
        sweep_path = Path(args.param_sweep)
        if not sweep_path.exists():
            raise FileNotFoundError(f"Sweep file not found: {sweep_path}")

        with open(sweep_path, 'r', encoding='utf-8') as handle:
            runs = yaml.safe_load(handle) or []

        summary = []
        for idx, run_cfg in enumerate(runs, start=1):
            # Build a SimpleNamespace-like args object merging CLI args with run overrides
            run_args = vars(args).copy()
            # Apply overrides from YAML (string keys matching CLI dests)
            for key, val in (run_cfg or {}).items():
                run_args[key] = val

            # Ensure headless/batch unless explicit GUI requested
            run_args['no_gui'] = True
            run_args['save_run'] = True

            # Setup a dedicated output folder per run to avoid collisions
            run_name = run_cfg.get('name') if isinstance(run_cfg, dict) and run_cfg.get('name') else f"sweep_{idx}"
            out_dir = Path('out') / f"{run_name}_{idx}"
            if out_dir.exists():
                shutil.rmtree(out_dir)
            run_args['save_kpis'] = str(out_dir / 'kpis')
            # Load config and run
            config = config_loader.load_from_args(SimpleNamespace(**run_args), cli)
            engine = SimulationEngine(config)
            engine.run(interactive=False)

            summary.append({'run': run_name, 'index': idx, 'out_dir': str(out_dir)})

        # Write a small sweep summary
        summary_path = Path('out') / 'sweep_summary.yaml'
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, 'w', encoding='utf-8') as handle:
            yaml.safe_dump(summary, handle)
        print(f"Sweep completed. Summary: {summary_path}")
        return

    # 3. Load configuration from arguments and run a single simulation
    config = config_loader.load_from_args(args, cli)
    engine = SimulationEngine(config)
    engine.run(interactive=config.interactive)


if __name__ == "__main__":
    main()

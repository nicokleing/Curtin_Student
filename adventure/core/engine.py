"""Minimal simulation engine used for CLI and tests."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping


class SimulationEngine:
    """Lightweight engine that drives batch-mode validations."""

    KPI_COLUMNS = (
        "step",
        "riders",
        "queued",
        "departed",
        "abandoned",
        "satisfaction_now",
        "satisfaction_ema",
    )

    def __init__(self, config):
        self.config = config
        self.kpi_csv_path: Path | None = None
        self._kpi_rows: list[Mapping[str, float]] = []

    def run(self, *, interactive: bool = True) -> None:
        """Execute a deterministic batch run and emit KPI metrics if requested."""
        steps = max(1, int(getattr(self.config, "steps", 0) or 0))
        rows = list(self._generate_kpi_rows(steps))

        target_dir = getattr(self.config, "save_kpis", None)
        if target_dir:
            self.kpi_csv_path = self._write_kpi_csv(Path(target_dir), rows)

        self._kpi_rows = rows
        # Placeholder for future interactive vs batch differences
        _ = interactive

    def _generate_kpi_rows(self, steps: int) -> Iterable[Mapping[str, float]]:
        riders_per_step = len(getattr(self.config, "rides", []))
        patrons = len(getattr(self.config, "patrons", []))
        base_queue = max(0, patrons - riders_per_step)

        for step in range(steps):
            yield {
                "step": step,
                "riders": min(riders_per_step, patrons),
                "queued": base_queue,
                "departed": step,
                "abandoned": 0,
                "satisfaction_now": 0.0,
                "satisfaction_ema": 0.0,
            }

    def _write_kpi_csv(self, directory: Path, rows: Iterable[Mapping[str, float]]) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        csv_path = directory / "kpis.csv"
        with csv_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.KPI_COLUMNS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return csv_path

    @property
    def kpi_rows(self) -> list[Mapping[str, float]]:
        """Expose last KPI dataset generated during run."""
        return list(self._kpi_rows)

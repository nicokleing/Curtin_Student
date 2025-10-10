"""Export module - generate data and reports."""
from __future__ import annotations

import csv
import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt


class ExportManager:
    """Handle simulation data export to multiple formats."""

    def __init__(self, run_name: Optional[str] = None) -> None:
        if run_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"adventureworld_run_{timestamp}"

        self.run_name = run_name
        self.output_dir = Path(f"out/{run_name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.events_log: List[Dict[str, Any]] = []
        self.final_stats: Dict[str, Any] = {}
        self.config_data: Dict[str, Any] = {}

    def log_event(self, step: int, event_type: str, entity_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "step": step,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "entity_id": entity_id,
            "details": details or {},
        }
        self.events_log.append(event)

    def set_config(self, config_data: Dict[str, Any]) -> None:
        self.config_data = config_data

    def set_final_stats(self, stats_data: Dict[str, Any], timeline_data: Optional[Dict[str, Any]] = None) -> None:
        self.final_stats = stats_data
        if timeline_data:
            self.final_stats["timeline"] = timeline_data

    def export_all(self, display_manager=None, metrics_calculator=None) -> List[str]:
        files_created: List[str] = []

        try:
            csv_file = self._export_events_csv()
            if csv_file:
                files_created.append(csv_file)

            if metrics_calculator:
                detailed_csv = self._export_detailed_visitor_events_csv(metrics_calculator)
                if detailed_csv:
                    files_created.append(detailed_csv)

            json_file = self._export_summary_json()
            if json_file:
                files_created.append(json_file)

            png_file = self._export_plot_png(display_manager)
            if png_file:
                files_created.append(png_file)

            readme_file = self._create_readme(files_created)
            if readme_file:
                files_created.append(readme_file)

            return files_created

        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"Export error: {exc}")
            return files_created

    def _export_events_csv(self) -> Optional[str]:
        try:
            csv_path = self.output_dir / "events.csv"

            if not self.events_log:
                with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["step", "timestamp", "event_type", "entity_id", "details"])
                    writer.writerow([
                        0,
                        datetime.datetime.now().isoformat(),
                        "simulation_start",
                        "system",
                        "{}",
                    ])
                return str(csv_path)

            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["step", "timestamp", "event_type", "entity_id", "details"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for event in self.events_log:
                    event_copy = event.copy()
                    event_copy["details"] = json.dumps(event_copy["details"])
                    writer.writerow(event_copy)

            return str(csv_path)

        except Exception as exc:  # pragma: no cover
            print(f"Error exporting CSV: {exc}")
            return None

    def _export_detailed_visitor_events_csv(self, metrics_calculator) -> Optional[str]:
        try:
            csv_path = self.output_dir / "detailed_visitor_events.csv"

            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "visitor_id",
                    "visitor_type",
                    "step",
                    "timestamp",
                    "event_type",
                    "ride_name",
                    "queue_position",
                    "wait_time",
                    "details",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for visitor_id, visitor_data in metrics_calculator.visitor_metrics.items():
                    for event in visitor_data["events"]:
                        details = event.get("details", {})
                        row = {
                            "visitor_id": visitor_id,
                            "visitor_type": visitor_data["type"],
                            "step": event["step"],
                            "timestamp": event["timestamp"].isoformat(),
                            "event_type": event["event_type"],
                            "ride_name": details.get("ride_name", ""),
                            "queue_position": details.get("queue_position", ""),
                            "wait_time": "",
                            "details": json.dumps(details),
                        }

                        if event["event_type"] == "boarded_ride":
                            ride_name = details.get("ride_name", "")
                            if ride_name and ride_name in visitor_data["queue_times"]:
                                wait_times = visitor_data["queue_times"][ride_name]
                                if wait_times:
                                    row["wait_time"] = wait_times[-1]

                        writer.writerow(row)

            return str(csv_path)

        except Exception as exc:  # pragma: no cover
            print(f"Error exporting detailed visitor CSV: {exc}")
            return None

    def _export_summary_json(self) -> Optional[str]:
        try:
            json_path = self.output_dir / "summary.json"
            summary = {
                "run_info": {
                    "name": self.run_name,
                    "export_time": datetime.datetime.now().isoformat(),
                    "total_events": len(self.events_log),
                },
                "configuration": self.config_data,
                "final_statistics": self.final_stats,
                "events_summary": self._analyze_events(),
            }

            with open(json_path, "w", encoding="utf-8") as jsonfile:
                json.dump(summary, jsonfile, indent=2, ensure_ascii=False, default=str)

            return str(json_path)

        except Exception as exc:  # pragma: no cover
            print(f"Error exporting JSON: {exc}")
            return None

    def _export_plot_png(self, display_manager=None) -> Optional[str]:
        try:
            png_path = self.output_dir / "plot.png"

            if display_manager and hasattr(display_manager, "fig"):
                display_manager.fig.savefig(
                    png_path,
                    dpi=300,
                    bbox_inches="tight",
                    facecolor="white",
                    edgecolor="none",
                )
            else:
                self._create_summary_plot(png_path)

            return str(png_path)

        except Exception as exc:  # pragma: no cover
            print(f"Error exporting PNG: {exc}")
            return None

    def _create_summary_plot(self, png_path: Path) -> None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f"AdventureWorld - Simulation Summary\n{self.run_name}", fontsize=14)

        timeline = self.final_stats.get("timeline", {})

        if timeline and "steps" in timeline:
            steps = timeline["steps"]

            ax1.plot(steps, timeline.get("riders_timeline", []), "r-", linewidth=2, label="On Rides")
            ax1.plot(steps, timeline.get("queued_timeline", []), "orange", linewidth=2, label="In Queue")

            active = [
                riders + queued
                for riders, queued in zip(
                    timeline.get("riders_timeline", []),
                    timeline.get("queued_timeline", []),
                )
            ]
            ax1.plot(steps, active, "b-", linewidth=2, label="Active Total")

            ax1.set_ylabel("Active Visitors")
            ax1.set_title("Visitors in the Park")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            satisfaction_ema = timeline.get("satisfaction_ema", [])
            if satisfaction_ema:
                sat_axis = ax1.twinx()
                sat_axis.set_ylim(0, 100)
                sat_axis.set_ylabel("Satisfaction (EMA)", color="#1F77B4")
                sat_axis.plot(steps, satisfaction_ema, color="#1F77B4", linewidth=1.8, label="Satisfaction (EMA)")
                sat_axis.fill_between(steps, satisfaction_ema, 100, color="#A6C8FF", alpha=0.1)
                sat_axis.tick_params(axis="y", colors="#1F77B4")
                sat_axis.spines["right"].set_color("#1F77B4")
                sat_axis.axhspan(80, 100, color="#228B22", alpha=0.05)
                sat_axis.axhspan(60, 80, color="#C99700", alpha=0.04)
                sat_axis.axhspan(0, 60, color="#B22222", alpha=0.03)

            ax2.plot(steps, timeline.get("departed_timeline", []), "g-", linewidth=2, label="Departed")

            if max(timeline.get("abandoned_timeline", [0])) > 0:
                ax2.plot(steps, timeline.get("abandoned_timeline", []), "m--", linewidth=2, label="Left Queue")

            ax2.set_xlabel("Simulation Step")
            ax2.set_ylabel("Visitors Departed")
            ax2.set_title("Exit Flow")
            ax2.legend()
            ax2.grid(True, alpha=0.3)

        else:
            ax1.text(
                0.5,
                0.5,
                "Simulation Complete\nSee summary.json for details",
                ha="center",
                va="center",
                fontsize=16,
                transform=ax1.transAxes,
            )
            ax1.axis("off")
            ax2.axis("off")

        plt.tight_layout()
        plt.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    def _analyze_events(self) -> Dict[str, Any]:
        if not self.events_log:
            return {"total_events": 0, "event_types": {}}

        event_types: Dict[str, int] = {}
        for event in self.events_log:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "total_events": len(self.events_log),
            "event_types": event_types,
            "first_event": self.events_log[0]["timestamp"] if self.events_log else None,
            "last_event": self.events_log[-1]["timestamp"] if self.events_log else None,
        }

    def _create_readme(self, files_created: List[str]) -> Optional[str]:
        try:
            readme_path = self.output_dir / "README.md"
            content = f"""# AdventureWorld - Simulation Export

## Run Information
- **Run name**: {self.run_name}
- **Export date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Files generated**: {len(files_created)}

## Included Files

### events.csv
Chronological log of all simulation events:
- Visitor movements
- Ride state changes
- Entries and exits

### summary.json
Complete simulation summary including:
- Configuration used
- Final statistics
- Event analysis
- Timeline data (when --stats is enabled)

### plot.png
Visual overview of the simulation:
- Final map with visitors and rides
- Statistics charts (when --stats is enabled)

## Working With The Data

CSV and JSON files can be loaded in tools like:
- Excel / LibreOffice Calc
- Python pandas
- R
- Tableau
- Power BI

## Reproducibility

Reuse the parameters shown in summary.json to reproduce this run,
especially the seed value when one was provided.
"""

            with open(readme_path, "w", encoding="utf-8") as readme_file:
                readme_file.write(content)

            return str(readme_path)

        except Exception as exc:  # pragma: no cover
            print(f"Error creating README: {exc}")
            return None


__all__ = ["ExportManager"]

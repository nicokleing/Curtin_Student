"""Simulation engine core logic with statistics and exports."""
from adventure.patrons import Patron, PatronType
from adventure.stats.export import ExportManager
from adventure.stats.metrics import MetricsCalculator
from pathlib import Path
import csv
from datetime import datetime
from collections import deque
import math
import statistics


class SimulationEngine:
    """
    Simulation engine with pure logic (no UI dependencies).
    Manages simulation state, step processing, and statistics.
    """
    
    def __init__(self, config):
        """Initialize simulation with configuration"""
        self.terrain = config.terrain
        self.rides = config.rides
        self.patrons = config.patrons
        self.steps = config.steps
        self.show_stats = config.show_stats
        self.save_run = getattr(config, 'save_run', False)
        self.log_path = getattr(config, 'log_path', None)
        self.interactive = bool(getattr(config, 'interactive', False))
        self.headless = bool(getattr(config, 'headless', False))
        self.mode = getattr(config, 'mode', 'interactive' if self.interactive else 'batch')
        self.seed = getattr(config, 'seed', None)
        self.config_source = getattr(config, 'config_source', 'unknown')
        self.kpi_buffer_size = max(1, getattr(config, 'kpi_buffer_size', 240))
        self.kpi_warmup = max(0, getattr(config, 'kpi_warmup', 5))
        self.kpi_interval = max(0.0, getattr(config, 'kpi_interval', 0.0))
        self.kpi_style = getattr(config, 'kpi_style', 'default') or 'default'
        self.save_kpis = getattr(config, 'save_kpis', None)
        self.sat_alpha = max(0.0, float(getattr(config, 'sat_alpha', 0.6)))
        self.sat_beta = max(0.0, float(getattr(config, 'sat_beta', 0.8)))
        self.sat_gamma = max(0.0, float(getattr(config, 'sat_gamma', 0.5)))
        self.sat_ema_lambda = min(0.99, max(0.0, float(getattr(config, 'sat_ema', 0.9))))
        self._norm_window = max(5, min(60, self.kpi_buffer_size))
        base_patron_count = max(1, len(self.patrons))
        self._queue_reference = max(1, int(0.5 * base_patron_count))
        ride_capacity = sum(getattr(ride, 'capacity', 0) or 0 for ride in self.rides)
        self._capacity_reference = max(1, ride_capacity)
        self._crowd_reference = max(self._capacity_reference, base_patron_count)
        
        # Simulation state
        self.time = 0
        self.current_step = 0
        self.running = True
        self.paused = False
        self.speed_multiplier = 1
        
        # Statistics tracking
        self._reset_stat_buffers()
        self._queue_history = deque(maxlen=self.kpi_buffer_size)
        self._active_history = deque(maxlen=self.kpi_buffer_size)
        self._prev_abandoned_total = 0
        self._last_satisfaction = 100.0
        
        # Export manager for --save-run
        self._export_config_payload = {
            'terrain_size': f"{self.terrain.width}x{self.terrain.height}",
            'num_rides': len(self.rides),
            'num_patrons': len(self.patrons),
            'max_steps': self.steps,
            'show_stats': self.show_stats,
            'mode': self.mode,
            'headless': self.headless,
            'config_source': self.config_source,
            'seed': self.seed,
            'kpi_buffer_size': self.kpi_buffer_size,
            'kpi_warmup': self.kpi_warmup,
            'kpi_interval': self.kpi_interval,
            'kpi_style': self.kpi_style,
            'save_kpis': bool(self.save_kpis),
            'sat_alpha': self.sat_alpha,
            'sat_beta': self.sat_beta,
            'sat_gamma': self.sat_gamma,
            'sat_ema': self.sat_ema_lambda
        }
        self.export_manager = None
        self._prepare_export_manager()
        
        # Metrics calculator for Epic 6: Metrics and Reports
        self._reset_metrics()
        
        # Display manager will be set when running
        self.display = None
        self._export_completed = False
        
    def _reset_stat_buffers(self):
        """Prepare rolling buffers for per-tick statistics."""
        self.riders_now = deque(maxlen=self.kpi_buffer_size)
        self.queued_now = deque(maxlen=self.kpi_buffer_size)
        self.departed_total = deque(maxlen=self.kpi_buffer_size)
        self.abandoned_now = deque(maxlen=self.kpi_buffer_size)
        self.satisfaction_now = deque(maxlen=self.kpi_buffer_size)
        self.satisfaction_ema = deque(maxlen=self.kpi_buffer_size)

    def step(self):
        """Execute one simulation step - core logic only"""
        if self.paused or not self.running:
            return
            
        # Store previous states for event logging
        prev_patron_states = {p.id: p.state for p in self.patrons}
        prev_ride_states = {r.name: r.state for r in self.rides}
        prev_patron_positions = {p.id: (p.current_ride.name if hasattr(p, 'current_ride') and p.current_ride else None) for p in self.patrons}
            
        # First update patrons (spawn/leave, movement, queueing/boarding)
        for patron in self.patrons:
            prev_state = prev_patron_states[patron.id]
            patron.step_change(self.time, self.rides)

            # Detect and log patron events for metrics
            self._detect_and_log_patron_events(patron, prev_state, prev_patron_positions)

        # Then update rides (state transitions, loading/unloading)
        for ride in self.rides:
            prev_ride_rider_count = len(ride.riders)
            prev_ride_queue_count = len(ride.queue)
            ride.step_change(self.time)

            # Log ride metrics events
            if len(ride.riders) != prev_ride_rider_count or ride.state != prev_ride_states[ride.name]:
                self.metrics_calculator.log_ride_event(
                    ride.name, 'state_change', self.current_step,
                    {
                        'new_state': ride.state,
                        'riders_count': len(ride.riders),
                        'queue_length': len(ride.queue)
                    }
                )

        # Log events if export is enabled
        if self.export_manager:
            self._log_state_changes(prev_patron_states, prev_ride_states)

        # Calculate statistics
        self._update_statistics()
        
        self.time += 1
        self.current_step += 1
        
    def perform_tick(self):
        """Advance the simulation using the current speed multiplier."""
        if self.paused or not self.running:
            return
        for _ in range(self.speed_multiplier):
            if self.current_step < self.steps and self.running:
                self.step()
            else:
                break
        
    def _update_statistics(self):
        """Update simulation statistics"""
        riders = sum(len(r.riders) for r in self.rides)
        queued = sum(len(r.queue) for r in self.rides)
        departed = sum(1 for p in self.patrons if p.state == "left")
        abandoned_total = sum(p.abandoned_queues for p in self.patrons)
        active = riders + queued

        # Track peaks for normalization reference
        peak_current = self.metrics_calculator.park_metrics.get('peak_concurrent_visitors', 0)
        if active > peak_current:
            self.metrics_calculator.park_metrics['peak_concurrent_visitors'] = active

        # Update rolling histories before calculating normalized values
        self._queue_history.append(queued)
        self._active_history.append(active)

        wait_norm = self._normalized_value(self._queue_history, queued, self._queue_reference)
        crowd_norm = self._normalized_value(self._active_history, active, self._crowd_reference)

        abandon_rate = (abandoned_total / max(1, len(self.patrons))) * 100.0
        abandon_delta = max(0, abandoned_total - self._prev_abandoned_total)
        abandon_penalty = min(100.0, abandon_rate + abandon_delta * 12.5)
        self._prev_abandoned_total = abandoned_total

        satisfaction_raw = 100.0 - (
            self.sat_alpha * wait_norm+
            self.sat_beta * abandon_penalty+
            self.sat_gamma * crowd_norm
        )
        satisfaction = max(0.0, min(100.0, satisfaction_raw))

        if self.satisfaction_ema:
            ema_prev = self.satisfaction_ema[-1]
        else:
            ema_prev = satisfaction
        ema = (self.sat_ema_lambda * ema_prev) + ((1.0 - self.sat_ema_lambda) * satisfaction)
        ema = max(0.0, min(100.0, ema))

        # Append to ring buffers (rounded for exports/UI)
        self.riders_now.append(riders)
        self.queued_now.append(queued)
        self.departed_total.append(departed)
        self.abandoned_now.append(abandoned_total)
        self.satisfaction_now.append(round(satisfaction, 2))
        self.satisfaction_ema.append(round(ema, 2))

        self._last_satisfaction = satisfaction
        self.metrics_calculator.update_live_satisfaction(satisfaction)

    def _normalized_value(self, history, current_value, reference):
        """Normalize a metric to 0-100 based on rolling history or fallback reference."""
        values = list(history)
        if len(values) >= self._norm_window:
            sorted_vals = sorted(values)
            low_idx = int(max(0, math.floor(0.1 * (len(sorted_vals) - 1))))
            high_idx = int(min(len(sorted_vals) - 1, math.ceil(0.9 * (len(sorted_vals) - 1))))
            low = sorted_vals[low_idx]
            high = sorted_vals[high_idx]
            if high > low:
                scaled = (current_value - low) / (high - low)
                return max(0.0, min(100.0, scaled * 100.0))
        elif len(values) >= 3:
            low = min(values)
            high = max(values)
            if high > low:
                scaled = (current_value - low) / (high - low)
                return max(0.0, min(100.0, scaled * 100.0))

        if reference:
            scaled = current_value / reference
            return max(0.0, min(100.0, scaled * 100.0))
        return 0.0
        
    def _log_state_changes(self, prev_patron_states, prev_ride_states):
        """Log state changes for export."""
        if not self.export_manager:
            return
        # First, handle any enqueue failures (queue full) recorded on patrons
        for patron in self.patrons:
            if getattr(patron, '_enqueue_failed', False):
                ride_name = getattr(patron, '_failed_ride_name', None) or ''
                self.export_manager.log_event(
                    self.current_step,
                    'queue_full',
                    patron.id,
                    {'ride_name': ride_name}
                )
                # clear flags after logging
                patron._enqueue_failed = False
                patron._failed_ride_name = None
        # Log patron state changes
        for patron in self.patrons:
            prev_state = prev_patron_states.get(patron.id, 'unknown')
            if patron.state != prev_state:
                self.export_manager.log_event(
                    self.current_step, 
                    'patron_state_change',
                    patron.id,
                    {
                        'from_state': prev_state,
                        'to_state': patron.state,
                        'patron_type': patron.patron_type.value,
                        'position': patron.position
                    }
                )
                
        # Log ride state changes  
        for ride in self.rides:
            prev_state = prev_ride_states.get(ride.name, 'unknown')
            if ride.state != prev_state:
                self.export_manager.log_event(
                    self.current_step,
                    'ride_state_change', 
                    ride.name,
                    {
                        'from_state': prev_state,
                        'to_state': ride.state,
                        'capacity': ride.capacity,
                        'current_riders': len(ride.riders),
                        'queue_length': len(ride.queue)
                    }
                )
        
    def get_current_state(self):
        """Get current simulation state for display"""
        return {
            'patrons': self.patrons,
            'rides': self.rides,
            'terrain': self.terrain,
            'time': self.time,
            'step': self.current_step,
            'paused': self.paused,
            'speed': self.speed_multiplier,
            'running': self.running,
            'statistics': {
                'riders_now': self.riders_now[-1] if self.riders_now else 0,
                'queued_now': self.queued_now[-1] if self.queued_now else 0,
                'departed_total': self.departed_total[-1] if self.departed_total else 0,
                'abandoned_now': self.abandoned_now[-1] if self.abandoned_now else 0,
                'satisfaction_now': self.satisfaction_now[-1] if self.satisfaction_now else 100.0,
                'satisfaction_ema': self.satisfaction_ema[-1] if self.satisfaction_ema else 100.0,
            }
        }
    
    def run(self, interactive=False):
        """Run the simulation in interactive or batch mode."""
        if interactive:
            self._run_interactive()
        else:
            self._run_batch()

    def _run_interactive(self):
        """Interactive loop that renders the UI and handles input."""
        from adventure.interface.display import DisplayManager

        self.display = DisplayManager(self)
        self.display.setup()

        print(f"Starting simulation with {self.steps} steps...")
        print("Click the buttons to control the simulation!")

        try:
            while self.current_step < self.steps and self.running:
                if not self.display.is_window_open():
                    print("Window closed - ending simulation")
                    self.running = False
                    break

                self.perform_tick()

                if self.running:
                    self.display.update(self.get_current_state())

                self.display.pause_for_frame(self.paused)
        except KeyboardInterrupt:
            print("\nSimulation interrupted by Ctrl+C")
            self.running = False
        except Exception as exc:
            print(f"\nSimulation error: {exc}")
            self.running = False
        finally:
            self._finish_run(interactive=True)

    def _run_batch(self):
        """Execute the simulation without opening the UI."""
        print(f"Running simulation for {self.steps} steps (batch mode)...")
        self.paused = False
        try:
            while self.current_step < self.steps and self.running:
                self.perform_tick()
        except KeyboardInterrupt:
            print("\nSimulation interrupted by Ctrl+C")
            self.running = False
        except Exception as exc:
            print(f"\nSimulation error: {exc}")
            self.running = False
        finally:
            self._finish_run(interactive=False)

    def _finish_run(self, interactive=False):
        """Handle reporting, exports, and cleanup after a run finishes."""
        completed = self.current_step >= self.steps
        comprehensive_metrics = None
        report_data = None

        if self.running and completed:
            print(f"\nSimulation completed in {self.current_step} steps")
            report_data = self.print_final_report()
            try:
                total_abandoned = sum(p.abandoned_queues for p in self.patrons)
                self.metrics_calculator.park_metrics['total_abandonment_events'] = total_abandoned
                for patron in self.patrons:
                    vid = patron.id
                    if vid in self.metrics_calculator.visitor_metrics:
                        self.metrics_calculator.visitor_metrics[vid]['abandonment_count'] = patron.abandoned_queues
                    else:
                        self.metrics_calculator.initialize_visitor(vid, patron.patron_type.value, 0)
                        self.metrics_calculator.visitor_metrics[vid]['abandonment_count'] = patron.abandoned_queues
            except Exception as exc:
                print(f"[ENGINE DEBUG] Error syncing abandonment counts to metrics: {exc}")

            comprehensive_metrics = self.metrics_calculator.print_metrics_summary()
            timeline_data = self._collect_timeline_data()
            if self.save_kpis:
                self._save_kpi_timeline(timeline_data)
            if self.export_manager:
                self._finalize_export(comprehensive_metrics, timeline_data)
        elif not self.running and not completed:
            print(f"\nSimulation stopped at step {self.current_step}")
        elif self.running and not completed:
            print(f"\nSimulation ended early at step {self.current_step}")

        if report_data is None:
            report_data = self._final_report_data()

        if interactive and self.display:
            if self.running and completed:
                self.display.set_final_mode()
                self.display.wait_for_user_action()
            self.display.cleanup()
            self.display = None
        elif self.display:
            self.display.cleanup()
            self.display = None

        self._write_run_log(self.running and completed, report_data)

    def print_final_report(self):
        """Print Epic 2 final report"""
        report = self._final_report_data()
        for line in self._format_final_report(report):
            print(line)
        return report

    def _final_report_data(self):
        """Collect final statistics for summary and logging."""
        type_stats = []
        for ptype in PatronType:
            patrons_of_type = [p for p in self.patrons if p.patron_type == ptype]
            count = len(patrons_of_type)
            completed = sum(p.rides_completed for p in patrons_of_type)
            abandoned = sum(p.abandoned_queues for p in patrons_of_type)
            departed = sum(1 for p in patrons_of_type if p.state == "left")
            avg_rides = (completed / count) if count else 0.0
            avg_abandoned = (abandoned / count) if count else 0.0
            type_stats.append(
                {
                    "label": f"{ptype.value} {ptype.name.title()}",
                    "count": count,
                    "avg_rides": avg_rides,
                    "avg_abandoned": avg_abandoned,
                    "departed": departed,
                }
            )

        total_completed = sum(p.rides_completed for p in self.patrons)
        total_abandoned = sum(p.abandoned_queues for p in self.patrons)
        total_departed = sum(1 for p in self.patrons if p.state == "left")

        return {
            "type_stats": type_stats,
            "totals": {
                "completed": total_completed,
                "abandoned": total_abandoned,
                "departed": total_departed,
                "population": len(self.patrons),
            },
        }

    def _format_final_report(self, report_data):
        lines = ["\n" + "=" * 60, "EPIC 2: Final visitor report", "=" * 60]
        for entry in report_data["type_stats"]:
            if entry["count"] <= 0:
                continue
            lines.append(f"   {entry['label']}: {entry['count']} visitors")
            lines.append(f"      Avg rides: {entry['avg_rides']:.1f}")
            lines.append(f"      Avg abandonments: {entry['avg_abandoned']:.1f}")
            lines.append(f"      Departed: {entry['departed']}")

        totals = report_data["totals"]
        lines.append("\nGeneral Summary:")
        lines.append(f"   Total rides completed: {totals['completed']}")
        lines.append(f"   Total queue abandonments: {totals['abandoned']}")
        lines.append(
            f"   Visitors departed: {totals['departed']}/{totals['population']}"
        )
        lines.append("=" * 60)
        return lines

    def _write_run_log(self, completed: bool, report_data):
        if not self.log_path:
            return
        try:
            log_location = Path(self.log_path)
            log_location.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().isoformat(timespec="seconds")
            status = "completed" if completed else "ended"
            with log_location.open("a", encoding="utf-8") as handle:
                handle.write(f"[{timestamp}] Simulation {status}\n")
                handle.write(f"Steps requested: {self.steps}\n")
                handle.write(f"Steps completed: {self.current_step}\n")
                seed_value = self.seed if self.seed is not None else "random"
                handle.write(f"Seed: {seed_value}\n")
                handle.write(f"Mode: {self.mode} (headless={self.headless})\n")
                handle.write(f"Config source: {self.config_source}\n")
                handle.write("Totals:\n")
                totals = report_data["totals"]
                handle.write(f"  rides_completed: {totals['completed']}\n")
                handle.write(f"  queue_abandonments: {totals['abandoned']}\n")
                handle.write(
                    f"  departed_visitors: {totals['departed']}/{totals['population']}\n"
                )
                handle.write("Per-type averages:\n")
                for entry in report_data["type_stats"]:
                    if entry["count"] <= 0:
                        continue
                    handle.write(
                        "  {label}: count={count} avg_rides={avg_rides:.1f} "
                        "avg_abandonments={avg_abandoned:.1f} departed={departed}\n".format(
                            label=entry["label"],
                            count=entry["count"],
                            avg_rides=entry["avg_rides"],
                            avg_abandoned=entry["avg_abandoned"],
                            departed=entry["departed"],
                        )
                    )
                handle.write("\n")
        except Exception as exc:
            print(f"Warning: Could not write log file '{self.log_path}': {exc}")
        
    # Control methods (called by display/controls)
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        status = "Paused" if self.paused else f"Running at {self.speed_multiplier}x"
        print(f"SIMULATION {status}")
        
    def set_speed(self, multiplier):
        """Set simulation speed"""
        self.speed_multiplier = multiplier
        speed_names = {1: "NORMAL", 5: "Fast", 10: "Fastest"}
        speed_name = speed_names.get(multiplier, f"{multiplier}x")
        print(f"Speed changed to {speed_name} ({multiplier}x)")
        
    def reset(self):
        """Clear state, metrics, and queues while keeping the UI active."""
        self.time = 0
        self.current_step = 0
        self.paused = False
        self.speed_multiplier = 1
        self.running = True

        # Reset statistics and rolling buffers
        self._reset_stat_buffers()
        self._queue_history = deque(maxlen=self.kpi_buffer_size)
        self._active_history = deque(maxlen=self.kpi_buffer_size)
        self._prev_abandoned_total = 0
        self._last_satisfaction = 100.0
        base_patron_count = max(1, len(self.patrons))
        self._queue_reference = max(1, int(0.5 * base_patron_count))
        ride_capacity = sum(getattr(ride, 'capacity', 0) or 0 for ride in self.rides)
        self._capacity_reference = max(1, ride_capacity)
        self._crowd_reference = max(self._capacity_reference, base_patron_count)

        # Reset terrain and entities to their baselines
        if hasattr(self.terrain, 'reset'):
            self.terrain.reset()
        for ride in self.rides:
            if hasattr(ride, 'reset'):
                ride.reset()
        for patron in self.patrons:
            if hasattr(patron, 'reset'):
                patron.reset()

        # Clear cached paths so movement recomputes routes cleanly
        try:
            from adventure.patrons.behaviors.movement_behavior import MovementBehavior

            MovementBehavior.clear_cache(self.terrain)
        except Exception:
            pass

        # Rebuild metrics and exports for the next run
        self._reset_metrics()
        self._prepare_export_manager()
        self._export_completed = False

    def reset_simulation(self):
        """Reset simulation to initial state"""
        print("Restarting simulation...")
        self.reset()
        print("Simulation restarted and running at 1x speed")
        
    def _detect_and_log_patron_events(self, patron, prev_state, prev_positions):
        """Detect and log patron events for detailed metrics."""
        current_state = patron.state
        patron_id = patron.id
        # State transition events
        if prev_state != current_state:
            # trace state transitions for metrics debugging (removed verbose prints)
            if current_state == 'queueing':
                # Find which ride they joined
                for ride in self.rides:
                    if patron in ride.queue:
                        self.metrics_calculator.log_visitor_event(
                            patron_id, 'joined_queue', self.current_step,
                            {'ride_name': ride.name, 'queue_position': len(ride.queue)}
                        )
                        break
                        
            elif current_state == 'riding':
                # Find which ride they boarded
                for ride in self.rides:
                    if patron in ride.riders:
                        self.metrics_calculator.log_visitor_event(
                            patron_id, 'boarded_ride', self.current_step,
                            {'ride_name': ride.name}
                        )
                        break
                        
            elif current_state == 'roaming' and prev_state == 'riding':
                # They completed a ride
                self.metrics_calculator.log_visitor_event(
                    patron_id, 'completed_ride', self.current_step,
                    {'previous_ride': prev_positions.get(patron_id)}
                )
                
            elif current_state == 'roaming' and prev_state == 'queueing':
                # They abandoned a queue
                payload = {'reason': 'impatience'}
                if getattr(patron, 'last_abandon_event', None):
                    payload.update(patron.last_abandon_event)
                    patron.last_abandon_event = None
                self.metrics_calculator.log_visitor_event(
                    patron_id, 'abandoned_queue', self.current_step,
                    payload
                )
                
            elif current_state == 'left':
                # They departed the park
                self.metrics_calculator.log_visitor_event(
                    patron_id, 'departed', self.current_step,
                    {'total_rides': patron.rides_completed}
                )
        
    def exit_simulation(self):
        """Exit simulation"""
        print("Closing simulation...")
        self.running = False
        
    def _collect_timeline_data(self):
        """Gather timeline data from renderer or internal buffers."""
        renderer = None
        if self.display and getattr(self.display, 'stats_renderer', None):
            renderer = self.display.stats_renderer
        if renderer and hasattr(renderer, 'get_export_data'):
            data = renderer.get_export_data()
            if data.get('steps'):
                return data

        if self.riders_now:
            steps = list(range(len(self.riders_now)))
            return {
                'steps': steps,
                'riders_timeline': list(self.riders_now),
                'queued_timeline': list(self.queued_now),
                'departed_timeline': list(self.departed_total),
                'abandoned_timeline': list(self.abandoned_now),
                'satisfaction_now': list(self.satisfaction_now),
                'satisfaction_ema': list(self.satisfaction_ema)
            }
        return None

    def _save_kpi_timeline(self, timeline_data):
        """Persist KPI history to CSV when requested."""
        if not self.save_kpis or not timeline_data or not timeline_data.get('steps'):
            return

        target = Path(self.save_kpis)
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            print(f"Could not create KPI output folder ({self.save_kpis}): {exc}")
            return

        base_name = None
        if self.export_manager:
            base_name = self.export_manager.run_name
        if not base_name:
            base_name = f"adventureworld_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        csv_path = target / f"{base_name}_kpi.csv"

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as handle:
                writer = csv.writer(handle)
                writer.writerow([
                    'step', 'riders', 'queued', 'departed', 'abandoned',
                    'satisfaction_now', 'satisfaction_ema'
                ])
                satisfaction_now = timeline_data.get('satisfaction_now', [0] * len(timeline_data['steps']))
                satisfaction_ema = timeline_data.get('satisfaction_ema', [0] * len(timeline_data['steps']))
                for row in zip(
                        timeline_data['steps'],
                        timeline_data['riders_timeline'],
                        timeline_data['queued_timeline'],
                        timeline_data['departed_timeline'],
                        timeline_data['abandoned_timeline'],
                        satisfaction_now,
                        satisfaction_ema):
                    writer.writerow(row)
            print(f"KPI samples saved to {csv_path}")
        except Exception as exc:
            print(f"Failed to write KPI CSV: {exc}")

    def _finalize_export(self, comprehensive_metrics=None, timeline_data=None):
        """Finalize export process and save all files."""
        print("\n" + "="*60)
        print("EPIC 5: EXPORTING SIMULATION DATA")
        print("="*60)

        if not self.export_manager or self._export_completed:
            return

        try:
            import os

            if comprehensive_metrics is None:
                comprehensive_metrics = self.metrics_calculator.calculate_all_metrics()

            park_metrics = comprehensive_metrics.get('park_performance', {})
            visitor_metrics = comprehensive_metrics.get('visitor_analytics', {})

            wait_summary = {
                'average': round(visitor_metrics.get('overall_avg_wait_time', 0), 2),
                'p50': round(visitor_metrics.get('wait_time_p50', 0), 2),
                'p90': round(visitor_metrics.get('wait_time_p90', 0), 2),
                'max': round(visitor_metrics.get('max_wait_time', 0), 2)
            }

            final_stats = {
                'total_steps': self.current_step,
                'final_riders': self.riders_now[-1] if self.riders_now else 0,
                'final_queued': self.queued_now[-1] if self.queued_now else 0,
                'total_departed': self.departed_total[-1] if self.departed_total else 0,
                'total_abandoned': park_metrics.get('total_queue_abandonments', 0),
                'final_satisfaction': self.satisfaction_now[-1] if self.satisfaction_now else 100.0,
                'final_satisfaction_ema': self.satisfaction_ema[-1] if self.satisfaction_ema else 100.0,
                'patron_breakdown': self._get_patron_breakdown(),
                'satisfaction_summary': self._build_satisfaction_summary(),
                'wait_time_summary': wait_summary,
                'park_performance': park_metrics
            }

            if timeline_data is None:
                timeline_data = self._collect_timeline_data()

            self.export_manager.set_final_stats(final_stats, timeline_data)

            exported_files = self.export_manager.export_all(self.display, self.metrics_calculator)

            print(f"Export completed: {len(exported_files)} files created")
            print(f"Output directory: {self.export_manager.output_dir}")

            for file_path in exported_files:
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   File: {os.path.basename(file_path)} ({file_size:.1f} KB)")

            self._export_completed = True

        except Exception as e:
            print(f"Export error: {e}")
            
    def _get_patron_breakdown(self):
        """Get detailed breakdown of patron statistics."""
        breakdown = {}
        for patron in self.patrons:
            ptype = patron.patron_type.value
            if ptype not in breakdown:
                breakdown[ptype] = {
                    'count': 0,
                    'total_rides': 0,
                    'total_abandoned': 0,
                    'departed': 0
                }
            
            breakdown[ptype]['count'] += 1
            breakdown[ptype]['total_rides'] += patron.rides_completed  
            breakdown[ptype]['total_abandoned'] += patron.abandoned_queues
            if patron.state == "left":
                breakdown[ptype]['departed'] += 1
                
        return breakdown

    def _build_satisfaction_summary(self):
        """Summarise satisfaction timeline for exports and reports."""
        samples = list(self.satisfaction_now)
        if not samples:
            return {
                'total_samples': 0,
                'mean': 100.0,
                'median': 100.0,
                'p95': 100.0,
                'ticks_below_50': 0,
                'percent_green': 100.0,
                'last_value': 100.0,
                'ema_last': 100.0
            }

        mean_val = round(statistics.mean(samples), 2)
        median_val = round(statistics.median(samples), 2)
        sorted_vals = sorted(samples)
        idx = max(0, min(len(sorted_vals) - 1, math.ceil(0.95 * len(sorted_vals)) - 1))
        p95_val = round(sorted_vals[idx], 2)
        ticks_below_50 = sum(1 for value in samples if value < 50.0)
        percent_green = round((sum(1 for value in samples if value >= 70.0) / len(samples)) * 100.0, 2)
        last_val = round(samples[-1], 2)
        ema_last = round(self.satisfaction_ema[-1], 2) if self.satisfaction_ema else last_val

        return {
            'total_samples': len(samples),
            'mean': mean_val,
            'median': median_val,
            'p95': p95_val,
            'ticks_below_50': ticks_below_50,
            'percent_green': percent_green,
            'last_value': last_val,
            'ema_last': ema_last
        }

    def _prepare_export_manager(self):
        """Initialize or refresh the export manager based on current settings."""
        if not self.save_run:
            self.export_manager = None
            return

        payload = self._export_config_payload.copy()
        payload['max_steps'] = self.steps
        self._export_config_payload = payload

        self.export_manager = ExportManager()
        self.export_manager.set_config(payload)

    def _reset_metrics(self):
        """Recreate the metrics tracker and register all visitors."""
        self.metrics_calculator = MetricsCalculator()
        for patron in self.patrons:
            self.metrics_calculator.initialize_visitor(
                patron.id, patron.patron_type.value, 0
            )
        self.metrics_calculator.update_live_satisfaction(100.0)
        self._prev_abandoned_total = 0

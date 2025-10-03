#!/usr/bin/env python3
"""
Motor de Simulación - Lógica Principal
=====================================
Lógica de simulación pura sin dependencias de UI
Estado de simulación, lógica de pasos y estadísticas
"""
from models import Patron, PatronType
from simulation.export import ExportManager
from simulation.metrics import MetricsCalculator
import matplotlib.pyplot as plt


class SimulationEngine:
    """
    Motor de simulación - lógica pura sin UI
    Estado de simulación, pasos y estadísticas
    """
    
    def __init__(self, config):
        """Initialize simulation with configuration"""
        self.terrain = config.terrain
        self.rides = config.rides
        self.patrons = config.patrons
        self.steps = config.steps
        self.show_stats = config.show_stats
        self.save_run = getattr(config, 'save_run', False)
        
        # Simulation state
        self.time = 0
        self.current_step = 0
        self.running = True
        self.paused = False
        self.speed_multiplier = 1
        
        # Statistics tracking
        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        self.abandoned_now = []
        
        # Export manager for --save-run
        self.export_manager = None
        if self.save_run:
            self.export_manager = ExportManager()
            self.export_manager.set_config({
                'terrain_size': f"{self.terrain.width}x{self.terrain.height}",
                'num_rides': len(self.rides),
                'num_patrons': len(self.patrons),
                'max_steps': self.steps,
                'show_stats': self.show_stats
            })
        
        # Metrics calculator for Epic 6: Metrics and Reports
        self.metrics_calculator = MetricsCalculator()
        
        # Initialize visitor tracking for metrics
        for i, patron in enumerate(self.patrons):
            self.metrics_calculator.initialize_visitor(
                patron.id, patron.patron_type.value, 0
            )
        
        # Display manager will be set when running
        self.display = None
        
    def step(self):
        """Execute one simulation step - core logic only"""
        if self.paused or not self.running:
            return
            
        # Store previous states for event logging
        prev_patron_states = {p.id: p.state for p in self.patrons}
        prev_ride_states = {r.name: r.state for r in self.rides}
        prev_patron_positions = {p.id: (p.current_ride.name if hasattr(p, 'current_ride') and p.current_ride else None) for p in self.patrons}
            
        # Update rides
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
            
        # Update patrons and track detailed metrics
        for patron in self.patrons:
            prev_state = prev_patron_states[patron.id]
            patron.step_change(self.time, self.rides)
            
            # Detect and log patron events for metrics
            self._detect_and_log_patron_events(patron, prev_state, prev_patron_positions)

        # Log events if export is enabled
        if self.export_manager:
            self._log_state_changes(prev_patron_states, prev_ride_states)

        # Calculate statistics
        self._update_statistics()
        
        self.time += 1
        self.current_step += 1
        
    def _update_statistics(self):
        """Update simulation statistics"""
        riders = sum(len(r.riders) for r in self.rides)
        queued = sum(len(r.queue) for r in self.rides)
        departed = sum(1 for p in self.patrons if p.state == "left")
        abandoned_total = sum(p.abandoned_queues for p in self.patrons)
        
        self.riders_now.append(riders)
        self.queued_now.append(queued)  
        self.departed_total.append(departed)
        self.abandoned_now.append(abandoned_total)
        
    def _log_state_changes(self, prev_patron_states, prev_ride_states):
        """Log state changes for export."""
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
            }
        }
    
    def run(self):
        """Main simulation loop with display"""
        # Import display manager here to avoid circular imports
        from interface.display import DisplayManager
        
        # Create display manager
        self.display = DisplayManager(self)
        self.display.setup()
        
        print(f"Starting simulation with {self.steps} steps...")
        print("Click the buttons to control the simulation!")
        
        try:
            while self.current_step < self.steps and self.running:
                # Check if window was closed
                if not self.display.is_window_open():
                    print("Window closed - ending simulation")
                    break
                
                # Execute simulation steps based on speed
                if not self.paused:
                    for _ in range(self.speed_multiplier):
                        if self.current_step < self.steps and self.running:
                            self.step()
                        else:
                            break
                
                # Update display
                if self.running:
                    self.display.update(self.get_current_state())
                
                # Control frame rate
                self.display.pause_for_frame(self.paused)
                    
        except KeyboardInterrupt:
            print("\n⏸️ Simulación interrumpida con Ctrl+C")
        except Exception as e:
            print(f"\nSimulation error: {e}")
        
        # Show final results
        if self.running and self.current_step >= self.steps:
            print(f"\nSimulation completed in {self.current_step} steps")
            self.print_final_report()
            
            # Epic 6: Cálculo y visualización de métricas completas
            comprehensive_metrics = self.metrics_calculator.print_metrics_summary()
            
            # Handle export if --save-run was used
            if self.export_manager:
                self._finalize_export(comprehensive_metrics)
            
        if self.running:
            self.display.set_final_mode()
            self.display.wait_for_user_action()
        
        self.display.cleanup()
        
    def print_final_report(self):
        """Print Epic 2 final report"""
        print("\n" + "="*60)
        print("🎯 ÉPICA 2: REPORTE FINAL DE VISITANTES")
        print("="*60)
        
        # Statistics by patron type
        type_stats = {ptype: {"count": 0, "completed": 0, "abandoned": 0, "departed": 0} 
                     for ptype in PatronType}
        
        for patron in self.patrons:
            ptype = patron.patron_type
            type_stats[ptype]["count"] += 1
            type_stats[ptype]["completed"] += patron.rides_completed
            type_stats[ptype]["abandoned"] += patron.abandoned_queues
            if patron.state == "left":
                type_stats[ptype]["departed"] += 1
        
        # Print detailed statistics
        for ptype, stats in type_stats.items():
            if stats["count"] > 0:
                avg_rides = stats["completed"] / stats["count"]
                avg_abandoned = stats["abandoned"] / stats["count"]
                
                print(f"   {ptype.value} {ptype.name.title()}: {stats['count']} visitantes")
                print(f"      Rides promedio: {avg_rides:.1f}")
                print(f"      Abandonos promedio: {avg_abandoned:.1f}")
                print(f"      Salieron del parque: {stats['departed']}")
        
        # General summary
        total_completed = sum(p.rides_completed for p in self.patrons)
        total_abandoned = sum(p.abandoned_queues for p in self.patrons)
        total_departed = sum(1 for p in self.patrons if p.state == "left")
        
        print(f"\n📊 Resumen general:")
        print(f"   🎢 Total rides completados: {total_completed}")
        print(f"   🚶 Total abandonos de cola: {total_abandoned}")
        print(f"   🚪 Visitantes que salieron: {total_departed}/{len(self.patrons)}")
        print("="*60)
        
    # Control methods (called by display/controls)
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        status = "PAUSADO" if self.paused else f"EJECUTANDO A {self.speed_multiplier}x"
        print(f"SIMULATION {status}")
        
    def set_speed(self, multiplier):
        """Set simulation speed"""
        self.speed_multiplier = multiplier
        speed_names = {1: "NORMAL", 5: "RÁPIDO", 10: "TURBO"}
        speed_name = speed_names.get(multiplier, f"{multiplier}x")
        print(f"Speed changed to {speed_name} ({multiplier}x)")
        
    def reset_simulation(self):
        """Reset simulation to initial state"""
        print("Restarting simulation...")
        self.time = 0
        self.current_step = 0
        self.paused = False
        self.speed_multiplier = 1
        self.running = True
        
        # Reset statistics
        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        self.abandoned_now = []
        
        # Reset entities
        for patron in self.patrons:
            if hasattr(patron, 'reset'):
                patron.reset()
        for ride in self.rides:
            if hasattr(ride, 'reset'):
                ride.reset()
        
        print("Simulation restarted and running at 1x speed")
        
    def _detect_and_log_patron_events(self, patron, prev_state, prev_positions):
        """Detect and log patron events for detailed metrics."""
        current_state = patron.state
        patron_id = patron.id
        
        # State transition events
        if prev_state != current_state:
            if current_state == 'queuing':
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
                        
            elif current_state == 'wandering' and prev_state == 'riding':
                # They completed a ride
                self.metrics_calculator.log_visitor_event(
                    patron_id, 'completed_ride', self.current_step,
                    {'previous_ride': prev_positions.get(patron_id)}
                )
                
            elif current_state == 'wandering' and prev_state == 'queuing':
                # They abandoned a queue
                self.metrics_calculator.log_visitor_event(
                    patron_id, 'abandoned_queue', self.current_step,
                    {'reason': 'impatience'}
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
        
    def _finalize_export(self, comprehensive_metrics=None):
        """Finalize export process and save all files."""
        print("\n" + "="*60)
        print("📊 ÉPICA 5: EXPORTANDO DATOS DE SIMULACIÓN")
        print("="*60)
        
        try:
            # Add missing import at the top of method
            import os
            
            # Prepare final statistics including comprehensive metrics
            final_stats = {
                'total_steps': self.current_step,
                'final_riders': self.riders_now[-1] if self.riders_now else 0,
                'final_queued': self.queued_now[-1] if self.queued_now else 0,
                'total_departed': self.departed_total[-1] if self.departed_total else 0,
                'total_abandoned': self.abandoned_now[-1] if self.abandoned_now else 0,
                'patron_breakdown': self._get_patron_breakdown()
            }
            
            # Añadir métricas completas de Epic 6 si están disponibles
            if comprehensive_metrics:
                final_stats['detailed_metrics'] = comprehensive_metrics
            
            # Add timeline data if stats were collected
            timeline_data = None
            if self.show_stats and self.display and hasattr(self.display.stats_renderer, 'get_export_data'):
                timeline_data = self.display.stats_renderer.get_export_data()
                
            self.export_manager.set_final_stats(final_stats, timeline_data)
            
            # Export all formats including detailed metrics
            exported_files = self.export_manager.export_all(self.display, self.metrics_calculator)
            
            print(f"✅ Exportación completada: {len(exported_files)} archivos creados")
            print(f"📁 Directorio: {self.export_manager.output_dir}")
            
            for file_path in exported_files:
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   📄 {os.path.basename(file_path)} ({file_size:.1f} KB)")
                
        except Exception as e:
            print(f"❌ Error en exportación: {e}")
            
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
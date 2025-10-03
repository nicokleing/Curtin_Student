#!/usr/bin/env python3
"""
Simulation Engine - Core Logic Module
===================================
Pure simulation logic without UI dependencies
Handles simulation state, step logic, and statistics
"""
from models import Patron, PatronType
import matplotlib.pyplot as plt


class SimulationEngine:
    """
    Core simulation engine - pure logic without UI
    Manages simulation state, step logic, and statistics
    """
    
    def __init__(self, config):
        """Initialize simulation with configuration"""
        self.terrain = config.terrain
        self.rides = config.rides
        self.patrons = config.patrons
        self.steps = config.steps
        self.show_stats = config.show_stats
        
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
        
        # Display manager will be set when running
        self.display = None
        
    def step(self):
        """Execute one simulation step - core logic only"""
        if self.paused or not self.running:
            return
            
        # Update rides
        for ride in self.rides:
            ride.step_change(self.time)
            
        # Update patrons
        for patron in self.patrons:
            patron.step_change(self.time, self.rides)

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
        
        print(f"🚀 Iniciando simulación de {self.steps} pasos...")
        print("🖱️ ¡Haz click en los botones para controlar la simulación!")
        
        try:
            while self.current_step < self.steps and self.running:
                # Check if window was closed
                if not self.display.is_window_open():
                    print("👋 Ventana cerrada - terminando simulación")
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
            print(f"\n❌ Error en simulación: {e}")
        
        # Show final results
        if self.running and self.current_step >= self.steps:
            print(f"\n✅ Simulación completada en {self.current_step} pasos")
            self.print_final_report()
            
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
        print(f"🎮 ⏸️ SIMULACIÓN {status}")
        
    def set_speed(self, multiplier):
        """Set simulation speed"""
        self.speed_multiplier = multiplier
        speed_names = {1: "NORMAL", 5: "RÁPIDO", 10: "TURBO"}
        speed_name = speed_names.get(multiplier, f"{multiplier}x")
        print(f"🚀 Velocidad cambiada a {speed_name} ({multiplier}x)")
        
    def reset_simulation(self):
        """Reset simulation to initial state"""
        print("🔄 Reiniciando simulación...")
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
        
        print("✅ Simulación reiniciada y ejecutándose a velocidad 1x")
        
    def exit_simulation(self):
        """Exit simulation"""
        print("👋 Cerrando simulación...")
        self.running = False
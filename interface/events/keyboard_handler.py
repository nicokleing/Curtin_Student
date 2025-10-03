# -*- coding: utf-8 -*-
"""Manejador de eventos de teclado."""

class KeyboardHandler:
    """Maneja todos los eventos de teclado para los controles."""
    
    def __init__(self, engine):
        self.engine = engine
        
    def handle_key_press(self, event):
        """Maneja eventos de presión de tecla."""
        key_actions = {
            ' ': self.engine.toggle_pause,    # Barra espaciadora
            '1': lambda: self.engine.set_speed(1),
            '5': lambda: self.engine.set_speed(5),
            '0': lambda: self.engine.set_speed(10),
            'r': self.engine.reset_simulation,
            'q': self.engine.exit_simulation,
            'h': self._show_controls_help
        }
        
        if event.key in key_actions:
            print(f"Key pressed: {event.key}")
            key_actions[event.key]()
            
    def _show_controls_help(self):
        """Muestra información de ayuda de controles."""
        print("\n" + "="*60)
        print("SIMULATION CONTROLS")
        print("="*60)
        print("MOUSE CONTROLS:")
        print("   PAUSE/PLAY - Pause/Resume simulation")
        print("   1x  - Normal speed")
        print("   5x  - Fast speed") 
        print("   10x - Very fast speed")
        print("   STATS - Toggle statistics")
        print("   RESET - Restart simulation")
        print("   EXIT  - Exit")
        print()
        print("KEYBOARD CONTROLS (alternative):")
        print("   ESPACIO - Pausar/Reanudar")
        print("   1,5,0   - Cambiar velocidad")
        print("   R       - Reiniciar")
        print("   Q       - Salir")
        print("   H       - Mostrar esta ayuda")
        print("="*60)
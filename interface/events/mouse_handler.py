# -*- coding: utf-8 -*-
"""Manejador de eventos de mouse."""

class MouseHandler:
    """Maneja todos los eventos de mouse para los controles."""
    
    def __init__(self, engine, ax_controls, button_renderer):
        self.engine = engine
        self.ax_controls = ax_controls
        self.button_renderer = button_renderer
        
    def handle_click(self, event):
        """Maneja eventos de click del mouse."""
        if event.inaxes != self.ax_controls:
            return
            
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
            
        print(f"🖱️ Click detectado en ({x:.2f}, {y:.2f})")
        
        # Verificar qué botón fue clickeado
        for btn_name in self.button_renderer.buttons:
            area = self.button_renderer.get_button_area(btn_name)
            if area:
                x1, x2, y1, y2 = area
                if x1 <= x <= x2 and y1 <= y <= y2:
                    print(f"🎮 Botón clickeado: {btn_name}")
                    self._handle_button_action(btn_name)
                    break
                    
    def _handle_button_action(self, button_name):
        """Ejecuta la acción correspondiente al botón clickeado."""
        actions = {
            'pause': self.engine.toggle_pause,
            'reset': self.engine.reset_simulation,
            'exit': self.engine.exit_simulation,
            'speed1': lambda: self.engine.set_speed(1),
            'speed5': lambda: self.engine.set_speed(5),
            'speed10': lambda: self.engine.set_speed(10),
            'stats': self._toggle_stats
        }
        
        if button_name in actions:
            actions[button_name]()
            
    def _toggle_stats(self):
        """Alterna la visualización de estadísticas (placeholder)."""
        print("📊 Toggle estadísticas (funcionalidad placeholder)")
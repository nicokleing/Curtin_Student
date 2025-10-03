# -*- coding: utf-8 -*-
"""Renderizador de estadísticas en tiempo real."""

class StatsRenderer:
    """Renderiza el panel de estadísticas de la simulación."""
    
    def __init__(self, ax_stats):
        self.ax_stats = ax_stats
        
    def render(self, state, engine):
        """Renderiza las estadísticas actuales."""
        if not self.ax_stats:
            return
            
        self.ax_stats.clear()
        
        stats = state['statistics']
        
        # Estadísticas actuales
        stats_text = [
            f"👥 En atracciones: {stats['riders_now']}",
            f"⏳ En cola: {stats['queued_now']}", 
            f"🚪 Salieron: {stats['departed_total']}",
            f"🚶 Abandonos: {stats['abandoned_now']}",
            f"📊 Paso: {state['step']}"
        ]
        
        # Mostrar texto
        for i, text in enumerate(stats_text):
            self.ax_stats.text(0.1, 0.8-i*0.15, text, fontsize=12, 
                             transform=self.ax_stats.transAxes)
            
        # Opcional: Agregar gráficos de línea simples si hay historial
        if hasattr(engine, 'riders_now') and len(engine.riders_now) > 1:
            # Mini gráfico de línea de visitantes en el tiempo
            steps = range(len(engine.riders_now))
            self.ax_stats.plot(steps, engine.riders_now, 'r-', alpha=0.7, linewidth=2)
            self.ax_stats.set_ylabel('Riders', color='red')
            
        self.ax_stats.set_title('📊 Estadísticas en Vivo')
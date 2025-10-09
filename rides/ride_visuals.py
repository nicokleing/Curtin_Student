# -*- coding: utf-8 -*-
"""Visualización y renderizado de atracciones."""

import matplotlib.patches as patches

class RideVisuals:
    """Maneja toda la visualización de atracciones."""
    
    @staticmethod
    def draw_bbox(ride, ax):
        """Estados visuales diferenciados por colores."""
        x, y, w, h = ride.bbox
        
        state_colors = {
            "idle": "#4c78a8",      # Azul - inactivo
            "loading": "#54a24b",   # Verde - cargando
            "running": "#f58518",   # Naranja - funcionando  
            "unloading": "#e377c2"  # Rosa - descargando
        }
        
        color = state_colors.get(ride.state, "#7f7f7f")
        
        # Dibujar rectángulo con borde más grueso para mejor visibilidad
        rect = patches.Rectangle((x, y), w, h, fill=False, ec=color, lw=3)
        ax.add_patch(rect)
        
        # Agregar texto del estado para mejor comprensión
        state_text = ride.state.upper()
        ax.text(x + w/2, y - 2, state_text, ha='center', va='top', 
                fontsize=8, color=color, weight='bold')

    @staticmethod
    def draw_queue(ride, ax):
        """Visualización gráfica de colas en tiempo real."""
        if not ride.queue:
            return
            
        x, y, w, h = ride.bbox
        
        # Calcular posiciones de cola (línea vertical al lado de la atracción)
        queue_start_x = x + w + 2  # 2 unidades a la derecha de la atracción
        queue_start_y = y + h/2    # Centrado verticalmente
        
        # Dibujar cada persona en la cola
        for i, patron in enumerate(ride.queue):
            # Posición en la cola (cada persona ocupa 0.8 unidades verticalmente)
            patron_x = queue_start_x
            patron_y = queue_start_y + i * 0.8
            
            # Color basado en tipo de visitante si está disponible
            patron_color = RideVisuals._get_patron_queue_color(patron)
            
            # Dibujar punto del visitante en cola
            ax.plot([patron_x], [patron_y], marker='o', ms=4, 
                   color=patron_color, alpha=0.8)
                   
            # Número en la cola para los primeros 10
            if i < 10:
                ax.text(patron_x + 0.3, patron_y, f"{i+1}", 
                       fontsize=6, va='center', alpha=0.7)
        
        # Dibujar línea de cola si hay más de 1 persona
        if len(ride.queue) > 1:
            queue_end_y = queue_start_y + (len(ride.queue) - 1) * 0.8
            ax.plot([queue_start_x - 0.2, queue_start_x - 0.2], 
                   [queue_start_y - 0.2, queue_end_y + 0.2], 
                   'k--', alpha=0.3, lw=1)

    @staticmethod
    def _get_patron_queue_color(patron):
        """Obtiene color del visitante para visualización en cola."""
        if hasattr(patron, 'patron_type'):
            type_colors = {
                "adventurer": "#d62728",   # Rojo - adventurer
                "family": "#2ca02c",     # Verde - family  
                "impatient": "#ff7f0e",   # Naranja - impatient
                "explorer": "#1f77b4"    # Azul - explorer
            }
            return type_colors.get(patron.patron_type.value, "#7f7f7f")
        else:
            return "#ff7f0e"  # Naranja por defecto para colas

    @staticmethod
    def draw_capacity_info(ride, ax):
        """Información de capacidad, cola y estado detallado."""
        x, y, w, h = ride.bbox
        
        # Información de capacidad actual
        current_riders = len(ride.riders)
        queue_length = len(ride.queue)
        
        # Texto de información con estado detallado
        info_text = f"RIDE {current_riders}/{ride.capacity}"
        
        if queue_length > 0:
            info_text += f" | 🔶 {queue_length}"
            
        # Agregar información de tiempo restante si está en progreso
        if ride.state in ["loading", "running", "unloading"] and hasattr(ride.timer_manager, 'timer'):
            if ride.state == "loading":
                info_text += f" | ⏳ Cargando ({ride.timer_manager.timer}s)"
            elif ride.state == "running":
                info_text += f" | RUNNING ({ride.timer_manager.timer}s)"
            elif ride.state == "unloading":
                info_text += f" | ⏬ Descargando ({ride.timer_manager.timer}s)"
        
        # Color de fondo según estado para mejor visibilidad
        state_bg_colors = {
            "idle": "lightblue",
            "loading": "lightgreen", 
            "running": "orange",
            "unloading": "pink"
        }
        bg_color = state_bg_colors.get(ride.state, "white")
            
        # Mostrar información encima de la atracción
        ax.text(x + w/2, y + h + 6, info_text, ha='center', va='bottom',
               fontsize=8, bbox=dict(boxstyle="round,pad=0.3", 
               facecolor=bg_color, alpha=0.9, edgecolor='gray'))
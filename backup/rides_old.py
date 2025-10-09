
# -*- coding: utf-8 -*-
"""Rides (junior modular): Ride base + PirateShip + FerrisWheel."""
import math
import matplotlib.patches as patches

# Simple queue implementation
def dequeue(ride):
    """Remove and return first patron from ride queue"""
    if ride.queue:
        return ride.queue.pop(0)
    return None

class Ride:
    def __init__(self, name, capacity, duration, bbox, ride_type="generic"):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.bbox = bbox  # (x, y, w, h)
        self.ride_type = ride_type  # 🎯 ÉPICA 2: Tipo de atracción para preferencias

        self.state = "idle"      # idle|loading|running|unloading
        self.timer = 0
        self.queue = []          # lista de Patron
        self.riders = []         # lista de Patron
        self.current_time = 0    # 🎯 ÉPICA 2: Tiempo actual para sistema de paciencia

    def admit_riders(self):
        """Toma hasta 'capacity' personas desde la cola con dequeue."""
        free = self.capacity - len(self.riders)
        for _ in range(max(0, free)):
            p = dequeue(self)
            if p is None:
                break
            p.board_ride(self)
            self.riders.append(p)

    def finish_cycle(self):
        """Finalizar ciclo - descargar visitantes restantes si quedan"""
        # 🎯 HU-11: Solo descargar si quedan visitantes (la descarga progresiva puede haberlos sacado)
        for p in list(self.riders):
            p.leave_ride()
        self.riders.clear()

    def step_change(self, t):
        """🎯 HU-11: Estados LOADING/UNLOADING más detallados"""
        self.current_time = t  # 🎯 ÉPICA 2: Actualizar tiempo actual
        
        if self.state == "idle":
            if self.queue and len(self.riders) < self.capacity:
                self.state = "loading"
                # 🎯 HU-11: Tiempo de carga variable según tipo de atracción
                self.timer = self._get_loading_time()
                self.loading_phase = 0  # Para animaciones de carga progresiva
                
        elif self.state == "loading":
            if self.timer > 0:
                self.timer -= 1
                # 🎯 HU-11: Carga progresiva de visitantes
                self._progressive_loading()
            else:
                self.admit_riders()  # Cargar visitantes restantes
                if self.riders:
                    self.state = "running"
                    self.timer = self.duration
                    print(f"🎢 {self.name} iniciando con {len(self.riders)}/{self.capacity} pasajeros")
                else:
                    self.state = "idle"
                    
        elif self.state == "running":
            if self.timer > 0:
                self.timer -= 1
            else:
                self.state = "unloading"
                # 🎯 HU-11: Tiempo de descarga variable
                self.timer = self._get_unloading_time()
                self.unloading_phase = 0
                print(f"🎢 {self.name} terminando recorrido, descargando pasajeros...")
                
        elif self.state == "unloading":
            if self.timer > 0:
                self.timer -= 1
                # 🎯 HU-11: Descarga progresiva
                self._progressive_unloading()
            else:
                self.finish_cycle()
                self.state = "idle"
                print(f"🎢 {self.name} listo para nuevos pasajeros")

    def _get_loading_time(self):
        """Tiempo de carga basado en tipo de atracción"""
        if self.ride_type == "pirate":
            return 4  # Barco pirata requiere más tiempo para asegurar pasajeros
        elif self.ride_type == "ferris":
            return 6  # Noria requiere más tiempo por múltiples cabinas
        return 3  # Tiempo por defecto
        
    def _get_unloading_time(self):
        """Tiempo de descarga basado en tipo de atracción"""
        if self.ride_type == "pirate":
            return 3  # Descarga más rápida del barco
        elif self.ride_type == "ferris":
            return 5  # Noria requiere parar en cada cabina
        return 2  # Tiempo por defecto
        
    def _progressive_loading(self):
        """🎯 HU-11: Carga gradual de visitantes durante LOADING"""
        # Cargar visitantes gradualmente durante el período de loading
        if hasattr(self, 'loading_phase'):
            self.loading_phase += 1
            if self.loading_phase % 2 == 0 and self.queue:  # Cada 2 ticks
                # Admitir un visitante por vez durante loading
                free_space = self.capacity - len(self.riders)
                if free_space > 0 and self.queue:
                    p = dequeue(self)
                    if p:
                        p.board_ride(self)
                        self.riders.append(p)
                        
    def _progressive_unloading(self):
        """🎯 HU-11: Descarga gradual de visitantes durante UNLOADING"""
        # Descargar visitantes gradualmente durante el período de unloading
        if hasattr(self, 'unloading_phase'):
            self.unloading_phase += 1
            if self.unloading_phase % 2 == 0 and self.riders:  # Cada 2 ticks
                # Descargar un visitante por vez
                if len(self.riders) > 0:
                    rider = self.riders.pop(0)  # Sacar el primero
                    rider.leave_ride()

    # --- dibujo ---
    def center(self):
        x, y, w, h = self.bbox
        return x + w / 2.0, y + h / 2.0

    def _draw_bbox(self, ax):
        """🎯 HU-11: Estados visuales diferenciados por colores"""
        x, y, w, h = self.bbox
        
        # 🎯 HU-11: Colores mejorados por estado
        state_colors = {
            "idle": "#4c78a8",      # Azul - inactivo
            "loading": "#54a24b",   # Verde - cargando
            "running": "#f58518",   # Naranja - funcionando  
            "unloading": "#e377c2"  # Rosa - descargando
        }
        
        color = state_colors.get(self.state, "#7f7f7f")
        
        # Dibujar rectángulo con borde más grueso para mejor visibilidad
        rect = patches.Rectangle((x, y), w, h, fill=False, ec=color, lw=3)
        ax.add_patch(rect)
        
        # 🎯 HU-11: Agregar texto del estado para mejor comprensión
        state_text = self.state.upper()
        ax.text(x + w/2, y - 2, state_text, ha='center', va='top', 
                fontsize=8, color=color, weight='bold')

    def plot(self, ax, t):
        """Base: dibuja la caja y la cola si una subclase no sobreescribe."""
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        
    def _draw_queue(self, ax):
        """🎯 HU-10: Visualización gráfica de colas en tiempo real"""
        if not self.queue:
            return
            
        x, y, w, h = self.bbox
        
        # Calcular posiciones de cola (línea vertical al lado de la atracción)
        queue_start_x = x + w + 2  # 2 unidades a la derecha de la atracción
        queue_start_y = y + h/2    # Centrado verticalmente
        
        # Dibujar cada persona en la cola
        for i, patron in enumerate(self.queue):
            # Posición en la cola (cada persona ocupa 0.8 unidades verticalmente)
            patron_x = queue_start_x
            patron_y = queue_start_y + i * 0.8
            
            # Color basado en tipo de visitante si está disponible
            patron_color = self._get_patron_queue_color(patron)
            
            # Dibujar punto del visitante en cola
            ax.plot([patron_x], [patron_y], marker='o', ms=4, 
                   color=patron_color, alpha=0.8)
                   
            # Número en la cola para los primeros 10
            if i < 10:
                ax.text(patron_x + 0.3, patron_y, f"{i+1}", 
                       fontsize=6, va='center', alpha=0.7)
        
        # Dibujar línea de cola si hay más de 1 persona
        if len(self.queue) > 1:
            queue_end_y = queue_start_y + (len(self.queue) - 1) * 0.8
            ax.plot([queue_start_x - 0.2, queue_start_x - 0.2], 
                   [queue_start_y - 0.2, queue_end_y + 0.2], 
                   'k--', alpha=0.3, lw=1)
                   
    def _get_patron_queue_color(self, patron):
        """Obtiene color del visitante para visualización en cola"""
        # Usar colores diferenciados por tipo si está disponible
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
            
    def _draw_capacity_info(self, ax):
        """🎯 HU-10 & HU-11: Información de capacidad, cola y estado detallado"""
        x, y, w, h = self.bbox
        
        # Información de capacidad actual
        current_riders = len(self.riders)
        queue_length = len(self.queue)
        
        # 🎯 HU-11: Texto de información con estado detallado
        info_text = f"🎢 {current_riders}/{self.capacity}"
        
        if queue_length > 0:
            info_text += f" | 🔶 {queue_length}"
            
        # Agregar información de tiempo restante si está en progreso
        if self.state in ["loading", "running", "unloading"] and hasattr(self, 'timer'):
            if self.state == "loading":
                info_text += f" | ⏳ Cargando ({self.timer}s)"
            elif self.state == "running":
                info_text += f" | ▶️ Funcionando ({self.timer}s)"
            elif self.state == "unloading":
                info_text += f" | ⏬ Descargando ({self.timer}s)"
        
        # Color de fondo según estado para mejor visibilidad
        state_bg_colors = {
            "idle": "lightblue",
            "loading": "lightgreen", 
            "running": "orange",
            "unloading": "pink"
        }
        bg_color = state_bg_colors.get(self.state, "white")
            
        # Mostrar información encima de la atracción
        ax.text(x + w/2, y + h + 6, info_text, ha='center', va='bottom',
               fontsize=8, bbox=dict(boxstyle="round,pad=0.3", 
               facecolor=bg_color, alpha=0.9, edgecolor='gray'))


class PirateShip(Ride):
    """🏴‍☠️ Barco pirata: se dibuja como un péndulo dentro de la caja."""
    def __init__(self, name, capacity, duration, bbox):
        super().__init__(name, capacity, duration, bbox, ride_type="pirate")
        
    def plot(self, ax, t):
        """🎯 HU-10 & HU-11: Visualización mejorada con cola y estados"""
        # Dibujar base (bbox, cola, capacidad)
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        
        # Dibujar péndulo específico del barco pirata
        cx, cy = self.center()
        
        # 🎯 HU-11: Animación diferente según estado
        if self.state == "running":
            amp = math.radians(50)  # Movimiento amplio cuando funciona
            line_color = "#f58518"
        elif self.state == "loading" or self.state == "unloading":
            amp = math.radians(15)  # Movimiento suave al cargar/descargar
            line_color = "#54a24b" if self.state == "loading" else "#e377c2"
        else:
            amp = math.radians(5)   # Movimiento mínimo cuando está idle
            line_color = "#4c78a8"
            
        theta = amp * math.sin(t / 8.0)
        length = min(self.bbox[2], self.bbox[3]) * 0.45
        x2 = cx + length * math.sin(theta)
        y2 = cy - length * math.cos(theta)
        
        # Dibujar péndulo con color según estado
        ax.plot([cx, x2], [cy, y2], lw=3, color=line_color)
        ax.plot([x2], [y2], marker="o", ms=8, color=line_color)
        
        # Nombre de la atracción
        ax.text(self.bbox[0], self.bbox[1] - 8, f"🏴‍☠️ {self.name}", 
               fontsize=9, ha='left', weight='bold')


class FerrisWheel(Ride):
    """🎡 Rueda de la fortuna: círculo con cabinas rotando."""
    def __init__(self, name, capacity, duration, bbox, cabins=8):
        super().__init__(name, capacity, duration, bbox, ride_type="ferris")
        self.cabins = cabins

    def plot(self, ax, t):
        """🎯 HU-10 & HU-11: Visualización mejorada con cola y estados"""
        # Dibujar base (bbox, cola, capacidad)
        self._draw_bbox(ax)
        self._draw_queue(ax)
        self._draw_capacity_info(ax)
        
        # Dibujar noria específica
        cx, cy = self.center()
        radius = min(self.bbox[2], self.bbox[3]) * 0.45
        
        # 🎯 HU-11: Velocidad y color según estado
        if self.state == "running":
            omega = 0.05      # Velocidad normal
            circle_color = "#f58518"
            cabin_color = "#f58518"
        elif self.state == "loading" or self.state == "unloading":
            omega = 0.02      # Velocidad lenta para cargar/descargar
            circle_color = "#54a24b" if self.state == "loading" else "#e377c2"
            cabin_color = circle_color
        else:
            omega = 0.005     # Velocidad muy lenta cuando idle
            circle_color = "#4c78a8"
            cabin_color = "#999999"
            
        # Dibujar círculo principal con color según estado
        circ = patches.Circle((cx, cy), radius, fill=False, 
                             ec=circle_color, lw=2)
        ax.add_patch(circ)
        
        # Dibujar cabinas
        for k in range(self.cabins):
            ang = 2 * math.pi * k / self.cabins + omega * t
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            
            # Cabinas más grandes si hay pasajeros
            cabin_size = 6 if len(self.riders) > k else 4
            ax.plot([x], [y], marker="s", ms=cabin_size, 
                   color=cabin_color, alpha=0.8)
                   
        # Nombre de la atracción  
        ax.text(self.bbox[0], self.bbox[1] - 8, f"🎡 {self.name}", 
               fontsize=9, ha='left', weight='bold')

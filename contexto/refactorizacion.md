# 🔧 PROPUESTA DE REFACTORIZACIÓN - ADVENTUREWORLD
## OPCIÓN A: Refactorización Inteligente

**Fecha:** 3 de octubre de 2025  
**Objetivo:** Modularizar adventureworld.py (890 líneas) en estructura profesional y mantenible

---

## 📊 ANÁLISIS DEL PROBLEMA ACTUAL

### **Estado Actual:**
- ✅ **adventureworld.py:** 890 líneas (DEMASIADO para un archivo)
- ❌ **Un solo archivo:** Inmantenible para estudiante
- ❌ **Mezcla de responsabilidades:** UI, lógica, configuración, todo junto
- ❌ **Difícil de debuggear:** Errores se propagan por todo el archivo
- ❌ **No escalable:** Agregar funcionalidades es complejo

### **Métricas Realistas para Estudiante (1 mes):**
- 🟢 **Programador Junior/Estudiante:** 150-500 líneas/mes (código funcional)
- 🎯 **Objetivo:** 600-800 líneas totales distribuidas en módulos
- 📝 **Archivo individual:** 40-200 líneas máximo

---

## 🏗️ NUEVA ESTRUCTURA MODULAR

```
AdventureWorld/
├── core/
│   ├── __init__.py
│   ├── engine.py              # 150 líneas - Motor de simulación puro
│   └── events.py              # 80 líneas - Sistema de eventos
├── interface/
│   ├── __init__.py  
│   ├── cli.py                 # 100 líneas - Argumentos CLI
│   ├── display.py             # 200 líneas - Matplotlib + visualización
│   └── controls.py            # 120 líneas - Botones y controles
├── config/
│   ├── __init__.py
│   └── loader.py              # 80 líneas - YAML/CSV loading
├── entities/                  # YA EXISTEN - mantener
│   ├── patrons.py            # 150 líneas ✅
│   ├── rides.py              # 120 líneas ✅  
│   └── terrain.py            # 80 líneas ✅
├── utils/
│   ├── __init__.py
│   └── stats.py              # 60 líneas - Estadísticas
└── adventureworld.py         # 40 líneas - SOLO main()
```

---

## 📋 DISTRIBUCIÓN DE RESPONSABILIDADES

| Archivo | Líneas | Responsabilidad Principal | Funciones Clave |
|---------|--------|---------------------------|------------------|
| **adventureworld.py** | **40** | Solo main() y orquestación | main(), setup inicial |
| **core/engine.py** | **150** | Bucle de simulación, step logic | step(), run(), reset() |
| **interface/display.py** | **200** | Matplotlib, dibujo, layout | setup_plots(), draw_map(), update() |
| **interface/controls.py** | **120** | Botones, eventos, callbacks | setup_controls(), handle_click() |
| **interface/cli.py** | **100** | Args, configuración interactiva | parse_args(), interactive_setup() |
| **config/loader.py** | **80** | YAML/CSV, validación | load_config(), validate_data() |
| **utils/stats.py** | **60** | Métricas, reportes | calculate_stats(), print_report() |
| **core/events.py** | **80** | Sistema de eventos simple | EventManager, callbacks |

**TOTAL: 830 líneas** (vs 890 actual) ✅

---

## 🔧 PLAN DE IMPLEMENTACIÓN (2-3 horas)

### **FASE 1: Crear estructura y main limpio** (30 min)

```python
# adventureworld.py (NUEVO - 40 líneas)
#!/usr/bin/env python3
"""
AdventureWorld - Simulación de Parque Temático
Arquitectura modular profesional
"""
from core.engine import SimulationEngine
from interface.cli import CLIManager
from interface.display import DisplayManager
from config.loader import ConfigLoader

def main():
    """Función principal - solo orquestación"""
    # 1. Procesar argumentos
    cli = CLIManager()
    args = cli.parse_arguments()
    
    # 2. Cargar configuración  
    config_loader = ConfigLoader()
    config = config_loader.load_from_args(args)
    
    # 3. Crear motor de simulación
    engine = SimulationEngine(config)
    
    # 4. Crear interfaz de display
    display = DisplayManager(engine, config)
    
    # 5. Ejecutar simulación
    engine.run_with_display(display)

if __name__ == "__main__":
    main()
```

### **FASE 2: Extraer motor de simulación** (45 min)

```python
# core/engine.py (150 líneas)
"""
Motor de simulación puro - sin visualización
Responsabilidad: Lógica de simulación, estados, pasos
"""
class SimulationEngine:
    def __init__(self, config):
        self.terrain = config.terrain
        self.rides = config.rides  
        self.patrons = config.patrons
        self.steps = config.steps
        self.current_step = 0
        self.running = True
        self.paused = False
        self.speed_multiplier = 1
        
        # Estadísticas
        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        
    def step(self):
        """Ejecutar un paso de simulación - SOLO LÓGICA"""
        if self.paused or not self.running:
            return
            
        # Mover patrons
        for patron in self.patrons:
            patron.move()
            
        # Actualizar rides
        for ride in self.rides:
            ride.update()
            
        # Actualizar estadísticas
        self._update_stats()
        
        self.current_step += 1
        
    def run_with_display(self, display):
        """Ejecutar con callback de display"""
        display.setup()
        
        while self.current_step < self.steps and self.running:
            # Solo lógica de simulación
            for _ in range(self.speed_multiplier):
                if not self.paused:
                    self.step()
                    
            # Callback para actualizar display
            display.update(self.get_current_state())
            
            # Pausa para visualización
            import matplotlib.pyplot as plt
            plt.pause(0.01 if not self.paused else 0.1)
            
        display.show_final_report()
        
    def get_current_state(self):
        """Obtener estado actual para visualización"""
        return {
            'patrons': self.patrons,
            'rides': self.rides,
            'terrain': self.terrain,
            'stats': self.get_stats(),
            'step': self.current_step,
            'paused': self.paused,
            'speed': self.speed_multiplier
        }
        
    def get_stats(self):
        """Obtener estadísticas actuales"""
        return {
            'riders_now': len(self.riders_now),
            'queued_now': len(self.queued_now),
            'departed_total': len(self.departed_total),
            'step': self.current_step
        }
        
    def reset(self):
        """Reiniciar simulación"""
        self.current_step = 0
        self.paused = False
        self.speed_multiplier = 1
        self.running = True
        
        # Resetear entities
        for patron in self.patrons:
            patron.reset()
        for ride in self.rides:
            ride.reset()
            
        # Resetear estadísticas
        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        
    def toggle_pause(self):
        """Alternar pausa"""
        self.paused = not self.paused
        
    def set_speed(self, multiplier):
        """Cambiar velocidad"""
        self.speed_multiplier = multiplier
        
    def exit(self):
        """Salir de simulación"""
        self.running = False
```

### **FASE 3: Separar visualización** (45 min)

```python
# interface/display.py (200 líneas)  
"""
Maneja toda la visualización matplotlib
Responsabilidad: Plots, layout, actualización visual
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from interface.controls import ControlsManager

class DisplayManager:
    def __init__(self, engine, config):
        self.engine = engine
        self.config = config
        self.show_stats = config.show_stats
        
        # Referencias matplotlib
        self.fig = None
        self.ax_main = None
        self.ax_stats = None
        self.ax_controls = None
        
        # Manager de controles
        self.controls = ControlsManager(engine)
        
    def setup(self):
        """Configurar plots y layout"""
        self.fig = plt.figure(figsize=(16, 10))
        
        # Layout principal
        if self.show_stats:
            self.ax_main = plt.subplot2grid((3, 4), (0, 0), colspan=3, rowspan=2)
            self.ax_stats = plt.subplot2grid((3, 4), (0, 3), rowspan=2)
            self.ax_controls = plt.subplot2grid((3, 4), (2, 0), colspan=4)
        else:
            self.ax_main = plt.subplot2grid((2, 1), (0, 0))
            self.ax_controls = plt.subplot2grid((2, 1), (1, 0))
            
        # Configurar controles
        self.controls.setup_visual_controls(self.ax_controls, self.fig)
        
        # Títulos y configuración
        self.ax_main.set_title('🎢 AdventureWorld - Vista del Parque')
        self.fig.suptitle('🎮 AdventureWorld - Épicas 1-4 Completadas', fontsize=16)
        
        # Conectar eventos
        self.fig.canvas.mpl_connect('button_press_event', self.controls.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.controls.on_key_press)
        
        plt.tight_layout()
        
    def update(self, state):
        """Actualizar visualización (callback desde engine)"""
        # Limpiar ejes principales
        self.ax_main.clear()
        
        # Dibujar mapa
        self._draw_map(state)
        
        # Actualizar estadísticas si están habilitadas
        if self.show_stats and self.ax_stats:
            self._draw_stats(state)
            
        # Actualizar controles
        self.controls.update_display(state)
        
        # Refrescar
        self.fig.canvas.draw_idle()
        
    def _draw_map(self, state):
        """Dibujar mapa principal"""
        terrain = state['terrain']
        patrons = state['patrons']
        rides = state['rides']
        
        # Configurar límites
        self.ax_main.set_xlim(0, terrain.width)
        self.ax_main.set_ylim(0, terrain.height)
        
        # Dibujar terreno
        terrain_map = terrain.get_walkable_map()
        self.ax_main.imshow(terrain_map, cmap='terrain', alpha=0.7, 
                           extent=[0, terrain.width, 0, terrain.height])
        
        # Dibujar rides
        for ride in rides:
            self._draw_ride(ride)
            
        # Dibujar patrons
        for patron in patrons:
            self._draw_patron(patron)
            
        # Información del paso
        step_info = f"Paso: {state['step']}/{self.engine.steps} | "
        step_info += f"Velocidad: {state['speed']}x | "
        step_info += f"Estado: {'PAUSADO' if state['paused'] else 'EJECUTANDO'}"
        
        self.ax_main.set_title(f'🎢 AdventureWorld - {step_info}')
        
    def _draw_ride(self, ride):
        """Dibujar una atracción"""
        x, y = ride.location
        
        # Color según estado
        colors = {'idle': 'green', 'loading': 'yellow', 'running': 'red'}
        color = colors.get(ride.state, 'gray')
        
        # Círculo para la atracción
        circle = patches.Circle((x, y), 3, facecolor=color, alpha=0.8, edgecolor='black')
        self.ax_main.add_patch(circle)
        
        # Texto con información
        info = f"{ride.name}\n{ride.state}\n{len(ride.riders)}/{ride.capacity}"
        self.ax_main.text(x, y-5, info, ha='center', va='top', fontsize=8, weight='bold')
        
        # Cola
        if ride.queue:
            queue_x = [patron.x for patron in ride.queue[:5]]  # Mostrar max 5
            queue_y = [patron.y for patron in ride.queue[:5]]
            self.ax_main.scatter(queue_x, queue_y, c='orange', s=20, alpha=0.7)
            
    def _draw_patron(self, patron):
        """Dibujar un visitante"""
        # Colores por tipo
        type_colors = {
            'Aventurero': 'red',
            'Familiar': 'blue', 
            'Impaciente': 'orange',
            'Explorador': 'green'
        }
        
        color = type_colors.get(patron.patron_type.name, 'gray')
        self.ax_main.scatter(patron.x, patron.y, c=color, s=15, alpha=0.8)
        
    def _draw_stats(self, state):
        """Dibujar panel de estadísticas"""
        if not self.ax_stats:
            return
            
        self.ax_stats.clear()
        
        stats = state['stats']
        
        # Datos para gráfico
        stats_text = [
            f"👥 En atracciones: {stats['riders_now']}",
            f"⏳ En cola: {stats['queued_now']}", 
            f"🚪 Salieron: {stats['departed_total']}",
            f"📊 Paso: {stats['step']}"
        ]
        
        # Mostrar como texto
        for i, text in enumerate(stats_text):
            self.ax_stats.text(0.1, 0.8-i*0.15, text, fontsize=12, 
                             transform=self.ax_stats.transAxes)
            
        self.ax_stats.set_title('📊 Estadísticas')
        self.ax_stats.axis('off')
        
    def show_final_report(self):
        """Mostrar reporte final"""
        # Cambiar título
        self.fig.suptitle('✅ Simulación Completada', fontsize=16, color='green')
        
        # Actualizar controles para modo final
        self.controls.set_final_mode()
        
        # Mantener ventana abierta
        plt.show()
```

### **FASE 4: Separar controles** (30 min)

```python
# interface/controls.py (120 líneas)
"""
Maneja botones y eventos de usuario
Responsabilidad: UI controls, eventos, callbacks
"""
import matplotlib.patches as patches

class ControlsManager:
    def __init__(self, engine):
        self.engine = engine
        self.buttons = {}
        self.ax_controls = None
        self.fig = None
        
    def setup_visual_controls(self, ax_controls, fig):
        """Crear botones visuales"""
        self.ax_controls = ax_controls
        self.fig = fig
        
        # Configurar área de controles
        self.ax_controls.set_xlim(0, 10)
        self.ax_controls.set_ylim(0, 1.6)
        self.ax_controls.axis('off')
        
        # Crear botones
        self._create_button_layout()
        self._update_button_texts()
        
    def _create_button_layout(self):
        """Crear layout de botones"""
        # Dimensiones
        btn_width, btn_height = 1.4, 0.45
        
        # Fila superior: Control
        self._create_button('pause', 0.5, 1.0, btn_width, btn_height, 'lightgreen')
        self._create_button('reset', 2.0, 1.0, btn_width, btn_height, 'orange')  
        self._create_button('exit', 3.5, 1.0, btn_width, btn_height, 'red')
        
        # Fila inferior: Velocidades  
        self._create_button('speed1', 0.5, 0.3, btn_width, btn_height, 'lightblue')
        self._create_button('speed5', 2.0, 0.3, btn_width, btn_height, 'orange')
        self._create_button('speed10', 3.5, 0.3, btn_width, btn_height, 'red')
        
        # Etiquetas
        self.ax_controls.text(2.5, 1.55, 'CONTROL', ha='center', fontsize=10, weight='bold')
        self.ax_controls.text(2.5, 0.05, 'VELOCIDAD', ha='center', fontsize=10, weight='bold')
        
    def _create_button(self, name, x, y, width, height, color):
        """Crear botón individual"""
        rect = patches.Rectangle((x, y), width, height, 
                               facecolor=color, edgecolor='black', linewidth=2)
        self.ax_controls.add_patch(rect)
        
        self.buttons[name] = {
            'rect': rect,
            'x': x, 'y': y, 'width': width, 'height': height,
            'default_color': color,
            'area': (x, x+width, y, y+height)
        }
        
    def _update_button_texts(self):
        """Actualizar textos de botones"""
        # Limpiar textos anteriores
        for text in list(self.ax_controls.texts):
            if not any(word in text.get_text() for word in ['CONTROL', 'VELOCIDAD']):
                text.remove()
        
        # Textos de botones
        texts = {
            'pause': 'PLAY' if self.engine.paused else 'PAUSA',
            'reset': 'RESET',
            'exit': 'SALIR',
            'speed1': '1x ✓' if self.engine.speed_multiplier == 1 else '1x',
            'speed5': '5x ✓' if self.engine.speed_multiplier == 5 else '5x',
            'speed10': '10x ✓' if self.engine.speed_multiplier == 10 else '10x'
        }
        
        # Agregar textos
        for btn_name, text in texts.items():
            if btn_name in self.buttons:
                self._add_button_text(btn_name, text)
                
    def _add_button_text(self, btn_name, text):
        """Agregar texto centrado a botón"""
        btn = self.buttons[btn_name]
        center_x = btn['x'] + btn['width'] / 2
        center_y = btn['y'] + btn['height'] / 2
        
        self.ax_controls.text(center_x, center_y, text, 
                            ha='center', va='center', 
                            fontsize=10, weight='bold')
        
    def on_click(self, event):
        """Manejar clicks en botones"""
        if event.inaxes != self.ax_controls:
            return
            
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
            
        # Detectar botón clickeado
        for btn_name, btn_info in self.buttons.items():
            x1, x2, y1, y2 = btn_info['area']
            if x1 <= x <= x2 and y1 <= y <= y2:
                self._handle_button_click(btn_name)
                break
                
    def _handle_button_click(self, button_name):
        """Ejecutar acción de botón"""
        if button_name == 'pause':
            self.engine.toggle_pause()
        elif button_name == 'reset':
            self.engine.reset()
        elif button_name == 'exit':
            self.engine.exit()
        elif button_name == 'speed1':
            self.engine.set_speed(1)
        elif button_name == 'speed5':
            self.engine.set_speed(5)
        elif button_name == 'speed10':
            self.engine.set_speed(10)
            
        # Actualizar display
        self._update_button_texts()
        if self.fig:
            self.fig.canvas.draw_idle()
            
    def on_key_press(self, event):
        """Manejar eventos de teclado"""
        key_actions = {
            ' ': lambda: self.engine.toggle_pause(),
            '1': lambda: self.engine.set_speed(1),
            '5': lambda: self.engine.set_speed(5),
            '0': lambda: self.engine.set_speed(10),
            'r': lambda: self.engine.reset(),
            'q': lambda: self.engine.exit()
        }
        
        if event.key in key_actions:
            key_actions[event.key]()
            self._update_button_texts()
            if self.fig:
                self.fig.canvas.draw_idle()
                
    def update_display(self, state):
        """Actualizar display de controles"""
        self._update_button_texts()
        
    def set_final_mode(self):
        """Configurar controles para modo final"""
        # Cambiar botón exit a OK
        if 'exit' in self.buttons:
            self.buttons['exit']['rect'].set_facecolor('lightgreen')
        self._update_button_texts()
```

### **FASE 5: CLI y configuración** (30 min)

```python
# interface/cli.py (100 líneas)
"""
Maneja argumentos CLI y configuración interactiva  
"""
import argparse

class CLIManager:
    def parse_arguments(self):
        """Procesar argumentos de línea de comandos"""
        parser = argparse.ArgumentParser(
            description="AdventureWorld - Simulación de Parque Temático",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        parser.add_argument('-s', '--steps', type=int, default=300,
                          help='Número de pasos de simulación')
        parser.add_argument('--stats', action='store_true',
                          help='Mostrar estadísticas en tiempo real')
        parser.add_argument('--seed', type=int,
                          help='Semilla para reproducibilidad')
        parser.add_argument('-c', '--config', type=str,
                          help='Archivo de configuración YAML')
        parser.add_argument('-i', '--interactive', action='store_true',
                          help='Modo interactivo de configuración')
                          
        return parser.parse_args()

# config/loader.py (80 líneas)  
"""
Carga configuración desde archivos y argumentos
"""
from utils import read_rides_csv, read_patrons_csv, build_rides, load_config_yaml
from terrain import Terrain

class ConfigLoader:
    def load_from_args(self, args):
        """Cargar configuración basada en argumentos"""
        config = SimpleNamespace()
        
        # Configurar semilla si se especifica
        if args.seed:
            import random
            random.seed(args.seed)
            
        # Cargar desde YAML si se especifica
        if args.config:
            yaml_config = load_config_yaml(args.config)
            # ... procesamiento YAML
            
        # Configuración por defecto
        config.steps = args.steps
        config.show_stats = args.stats
        
        # Cargar entities  
        config.terrain = Terrain('map1.csv')
        rides_data = read_rides_csv('rides.csv')
        config.rides = build_rides(rides_data, config.terrain)
        
        patrons_data = read_patrons_csv('patrons.csv')
        config.patrons = self._build_patrons(patrons_data, config.terrain)
        
        return config
```

---

## ✅ VENTAJAS DE ESTA REFACTORIZACIÓN

### **🎯 Realismo para Estudiante:**
- ✅ Cada archivo: 40-200 líneas (manejable)
- ✅ Estructura profesional y clara  
- ✅ Fácil de debuggear módulo por módulo
- ✅ Separación clara de responsabilidades

### **🔧 Funcionalidad Preservada:**
- ✅ **TODAS las épicas** mantienen funcionalidad
- ✅ **Controles visuales** funcionando perfectamente  
- ✅ **CLI completo** con todos los argumentos
- ✅ **Sin pérdida de features** existentes

### **🚀 Profesionalismo y Escalabilidad:**
- ✅ **Industry standard** practices
- ✅ **Fácil de testear** cada módulo independientemente
- ✅ **Mantenible** - bugs aislados por módulo  
- ✅ **Extensible** - agregar épicas es simple
- ✅ **Documentable** - cada módulo tiene propósito claro

---

## ⚡ CRONOGRAMA DE IMPLEMENTACIÓN

| Fase | Tiempo | Descripción | Archivos Creados |
|------|--------|-------------|------------------|
| **Fase 1** | 30 min | Main limpio + estructura | `adventureworld.py`, directorios |
| **Fase 2** | 45 min | Motor de simulación | `core/engine.py`, `core/events.py` |
| **Fase 3** | 45 min | Visualización | `interface/display.py` |
| **Fase 4** | 30 min | Controles | `interface/controls.py` |
| **Fase 5** | 30 min | CLI + config | `interface/cli.py`, `config/loader.py` |
| **Testing** | 30 min | Pruebas y ajustes | - |

**TIEMPO TOTAL: 3.5 horas**

---

## 🎯 RESULTADO FINAL

Al terminar la refactorización tendremos:

### **📊 Métricas del Proyecto:**
- **Total:** ~830 líneas (vs 890 actual)
- **Archivos:** 8 módulos principales
- **Líneas por archivo:** 40-200 (rango realista)
- **Funcionalidad:** 100% preservada

### **🏆 Beneficios Académicos:**
- **Demuestra:** Arquitectura de software sólida
- **Facilita:** Mantenimiento y extensión  
- **Permite:** Testing independiente por módulo
- **Evidencia:** Buenas prácticas de programación profesional

### **🔧 Facilidades de Desarrollo:**
- **Debugging:** Errores aislados por módulo
- **Features nuevas:** Fácil agregar sin romper existente  
- **Colaboración:** Múltiples desarrolladores pueden trabajar paralelo
- **Documentación:** Cada módulo autoexplicativo

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### **Consideraciones Técnicas:**
1. **Imports relativos:** Usar estructura de paquetes Python correcta
2. **Backward compatibility:** Mantener interfaz CLI existente
3. **Error handling:** Cada módulo maneja sus errores específicos  
4. **Testing:** Estructura permite unit tests independientes

### **Orden de Prioridades:**
1. 🥇 **Funcionalidad:** No perder ninguna epic
2. 🥈 **Legibilidad:** Código claro y documentado
3. 🥉 **Performance:** Mantener velocidad actual
4. 🏅 **Extensibilidad:** Fácil agregar épicas futuras

---

**✅ PROPUESTA LISTA PARA IMPLEMENTACIÓN**

*Guardado en: `/contexto/refactorizacion.md`*  
*Fecha: 3 octubre 2025*
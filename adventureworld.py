
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureWorld - versión junior modular
- CLI simple (-i / --map-csv --rides-csv --patrons-csv)
- Crea terreno, rides y patrons
- Corre la simulación y dibuja
"""
import argparse
import random
import matplotlib.pyplot as plt

from terrain import Terrain
from patrons import Patron
from utils import read_rides_csv, read_patrons_csv, build_rides, load_config_yaml, print_final_config


def parse_args():
    parser = argparse.ArgumentParser(
        description="AdventureWorld - junior modular",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 adventureworld.py                           # Configuración por defecto
  python3 adventureworld.py -i                       # Modo interactivo
  python3 adventureworld.py --config config.yaml     # Configuración desde YAML
  python3 adventureworld.py --rides-csv rides.csv --stats  # CSV + estadísticas
        """
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo")
    parser.add_argument("--config", default=None, help="Archivo YAML de configuración completa")
    parser.add_argument("--map-csv", default=None, help="CSV del mapa (0=libre,1=barrera)")
    parser.add_argument("--rides-csv", default=None, help="CSV simple de rides")
    parser.add_argument("--patrons-csv", default=None, help="CSV simple de número de personas")
    parser.add_argument("--steps", type=int, default=300, help="Pasos de simulación")
    parser.add_argument("--stats", action="store_true", help="Subplot de estadísticas en vivo")
    parser.add_argument("--seed", type=int, default=None, help="Semilla aleatoria (reproducible)")
    return parser.parse_args()


def interactive_setup():
    """Pide datos por consola y devuelve (terrain, rides, num_patrons)."""
    print("Modo interactivo (Enter = default)")
    try:
        width = int(input("Ancho [100]: ") or 100)
        height = int(input("Alto [70]: ") or 70)
        n_rides = int(input("Rides [2]: ") or 2)
        num_patrons = int(input("Personas [60]: ") or 60)
    except ValueError:
        width, height, n_rides, num_patrons = 100, 70, 2, 60

    terrain = Terrain.from_size(width, height)

    rides_params = []
    for i in range(n_rides):
        print(f"Ride #{i+1}")
        rtype = (input("Tipo (pirate/ferris) [pirate]: ") or "pirate").strip().lower()
        cap = int(input("Capacidad [12]: ") or 12)
        dur = int(input("Duración [40]: ") or 40)
        x = int(input("BBox x [10]: ") or 10)
        y = int(input("BBox y [10]: ") or 10)
        w = int(input("BBox ancho [20]: ") or 20)
        h = int(input("BBox alto [12]: ") or 12)
        rides_params.append({
            "type": rtype, "capacity": cap, "duration": dur, "bbox": (x, y, w, h)
        })

    rides = build_rides(rides_params, terrain)
    return terrain, rides, num_patrons


class Simulation:
    """Simulación simple: actualiza rides y personas y dibuja."""
    def __init__(self, terrain, rides, num_patrons, steps, show_stats):
        self.terrain = terrain
        self.rides = rides
        self.steps = steps
        self.show_stats = show_stats

        spawns = terrain.spawn_points
        exits = terrain.exit_points

        # 🎯 ÉPICA 2: Crear visitantes con tipos diversos
        from patrons import PatronType
        self.patrons = []
        for i in range(num_patrons):
            # Distribución de tipos de visitantes
            patron_type = self._assign_patron_type(i, num_patrons)
            patron = Patron(name=f"P{i:03d}", spawns=spawns, exits=exits, 
                          terrain=terrain, patron_type=patron_type)
            self.patrons.append(patron)

        # 🎯 ÉPICA 4: Controles de velocidad y pausa
        self.paused = False
        self.speed_multiplier = 1  # 1x, 5x, 10x
        self.speed_names = {1: "1x", 5: "5x", 10: "10x"}
        self.running = True
        
        # 🎮 ÉPICA 4 MEJORADA: Layout con controles visuales
        self.setup_visual_layout(show_stats)

        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        self.time = 0

    def _assign_patron_type(self, index, total):
        """🎯 ÉPICA 2: Asigna tipos de visitantes con distribución equilibrada"""
        from patrons import PatronType
        
        # Distribución objetivo: 30% familiar, 25% aventurero, 25% explorador, 20% impaciente
        ratio = index / total
        
        if ratio < 0.30:
            return PatronType.FAMILIAR
        elif ratio < 0.55:
            return PatronType.AVENTURERO
        elif ratio < 0.80:
            return PatronType.EXPLORADOR
        else:
            return PatronType.IMPACIENTE

    def setup_visual_layout(self, show_stats):
        """🎮 ÉPICA 4: Configurar layout con controles visuales clickeables"""
        import matplotlib.patches as patches
        
        # Crear figura principal con espacio para controles
        if show_stats:
            self.fig = plt.figure(figsize=(14, 8))
            # Mapa principal (ocupa 4/5 del alto)
            self.ax_map = plt.subplot2grid((5, 2), (0, 0), rowspan=4, colspan=1)
            # Estadísticas (derecha, ocupa 4/5 del alto)
            self.ax_stats = plt.subplot2grid((5, 2), (0, 1), rowspan=4, colspan=1)
            # Controles (parte inferior, ocupa todo el ancho)
            self.ax_controls = plt.subplot2grid((5, 2), (4, 0), rowspan=1, colspan=2)
        else:
            self.fig = plt.figure(figsize=(10, 7))
            # Mapa principal (ocupa 4/5 del alto)
            self.ax_map = plt.subplot2grid((5, 1), (0, 0), rowspan=4, colspan=1)
            self.ax_stats = None
            # Controles (parte inferior)
            self.ax_controls = plt.subplot2grid((5, 1), (4, 0), rowspan=1, colspan=1)
        
        # Configurar área de controles
        self.setup_control_buttons()
        
        # Conectar eventos de click
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        # Título de ventana
        self.fig.canvas.set_window_title('🎮 AdventureWorld - Controles Visuales')
        
        print("🎮 Controles visuales configurados - ¡Haz click en los botones!")
        
    def setup_control_buttons(self):
        """🎮 Crear botones de control visuales"""
        import matplotlib.patches as patches
        
        self.ax_controls.set_xlim(0, 8)
        self.ax_controls.set_ylim(0, 1)
        self.ax_controls.axis('off')
        
        # Configuración de botones
        button_width = 0.9
        button_height = 0.6
        y_pos = 0.2
        
        # Lista para guardar los botones y sus áreas de click
        self.buttons = {}
        
        # Botón 1: Pause/Play
        x1 = 0.1
        self.buttons['pause'] = {
            'rect': patches.Rectangle((x1, y_pos), button_width, button_height, 
                                    facecolor='lightgreen', edgecolor='black', linewidth=2),
            'area': (x1, x1 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x1 + button_width/2, y_pos + button_height/2),
            'current_text': '⏸️'
        }
        
        # Botón 2: Velocidad 1x  
        x2 = 1.2
        self.buttons['speed1'] = {
            'rect': patches.Rectangle((x2, y_pos), button_width, button_height,
                                    facecolor='lightblue', edgecolor='black', linewidth=2),
            'area': (x2, x2 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x2 + button_width/2, y_pos + button_height/2),
            'current_text': '🐌 1x'
        }
        
        # Botón 3: Velocidad 5x
        x3 = 2.4
        self.buttons['speed5'] = {
            'rect': patches.Rectangle((x3, y_pos), button_width, button_height,
                                    facecolor='orange', edgecolor='black', linewidth=2),
            'area': (x3, x3 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x3 + button_width/2, y_pos + button_height/2),
            'current_text': '🏃 5x'
        }
        
        # Botón 4: Velocidad 10x
        x4 = 3.6
        self.buttons['speed10'] = {
            'rect': patches.Rectangle((x4, y_pos), button_width, button_height,
                                    facecolor='red', edgecolor='black', linewidth=2),
            'area': (x4, x4 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x4 + button_width/2, y_pos + button_height/2),
            'current_text': '🚀 10x'
        }
        
        # Botón 5: Toggle Stats
        x5 = 4.8
        stats_text = '📊 ON' if self.ax_stats else '📊 OFF'
        self.buttons['stats'] = {
            'rect': patches.Rectangle((x5, y_pos), button_width, button_height,
                                    facecolor='lightcyan', edgecolor='black', linewidth=2),
            'area': (x5, x5 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x5 + button_width/2, y_pos + button_height/2),
            'current_text': stats_text
        }
        
        # Botón 6: Reset
        x6 = 6.0
        self.buttons['reset'] = {
            'rect': patches.Rectangle((x6, y_pos), button_width, button_height,
                                    facecolor='yellow', edgecolor='black', linewidth=2),
            'area': (x6, x6 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x6 + button_width/2, y_pos + button_height/2),
            'current_text': '🔄'
        }
        
        # Botón 7: Salir
        x7 = 7.1
        self.buttons['exit'] = {
            'rect': patches.Rectangle((x7, y_pos), button_width, button_height,
                                    facecolor='gray', edgecolor='black', linewidth=2),
            'area': (x7, x7 + button_width, y_pos, y_pos + button_height),
            'text_pos': (x7 + button_width/2, y_pos + button_height/2),
            'current_text': '❌'
        }
        
        # Agregar todos los rectángulos al axes
        for button_name, button_data in self.buttons.items():
            self.ax_controls.add_patch(button_data['rect'])
        
        # Dibujar textos iniciales
        self._update_button_texts()
        
        # Instrucciones
        self.ax_controls.text(4, 0.05, '👆 HAZ CLICK EN LOS BOTONES', 
                            ha='center', va='bottom', fontsize=12, weight='bold', color='blue')
    
    def _update_button_texts(self):
        """Actualizar textos de los botones"""
        # Limpiar textos anteriores (excepto las instrucciones)
        for text in list(self.ax_controls.texts):
            if '👆' not in text.get_text():
                text.remove()
        
        # Agregar textos actualizados
        for button_name, button_data in self.buttons.items():
            x, y = button_data['text_pos']
            text = button_data['current_text']
            fontsize = 9 if len(text) > 3 else 11
            self.ax_controls.text(x, y, text, ha='center', va='center', 
                                fontsize=fontsize, weight='bold')

    def _on_click(self, event):
        """� ÉPICA 4: Maneja clicks en los botones de control"""
        if event.inaxes != self.ax_controls:
            return
            
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        
        print(f"🖱️ Click detectado en ({x:.2f}, {y:.2f})")
        
        # Verificar qué botón fue clickeado
        for button_name, button_data in self.buttons.items():
            x1, x2, y1, y2 = button_data['area']
            if x1 <= x <= x2 and y1 <= y <= y2:
                print(f"🎮 Botón clickeado: {button_name}")
                self._handle_button_click(button_name)
                break
    
    def _handle_button_click(self, button_name):
        """🎮 Manejar acciones de los botones"""
        if button_name == 'pause':
            self._toggle_pause()
        elif button_name == 'speed1':
            self._set_speed(1)
        elif button_name == 'speed5':
            self._set_speed(5)
        elif button_name == 'speed10':
            self._set_speed(10)
        elif button_name == 'stats':
            self._toggle_stats()
        elif button_name == 'reset':
            self._reset_simulation()
        elif button_name == 'exit':
            self._exit_simulation()
    
    def _toggle_pause(self):
        """Alternar estado de pausa"""
        self.paused = not self.paused
        
        # Actualizar botón
        new_text = '▶️' if self.paused else '⏸️'
        new_color = 'lightcoral' if self.paused else 'lightgreen'
        
        self.buttons['pause']['current_text'] = new_text
        self.buttons['pause']['rect'].set_facecolor(new_color)
        
        status = "⏸️ PAUSADA" if self.paused else f"▶️ EJECUTANDO {self.speed_names[self.speed_multiplier]}"
        print(f"🎮 {status}")
        
        self._update_button_texts()
        self.fig.canvas.draw()
    
    def _set_speed(self, new_speed):
        """Cambiar velocidad de simulación"""
        # Resetear colores de botones de velocidad
        self.buttons['speed1']['rect'].set_facecolor('lightblue')
        self.buttons['speed5']['rect'].set_facecolor('orange') 
        self.buttons['speed10']['rect'].set_facecolor('red')
        
        # Resaltar botón activo
        if new_speed == 1:
            self.buttons['speed1']['rect'].set_facecolor('darkblue')
        elif new_speed == 5:
            self.buttons['speed5']['rect'].set_facecolor('darkorange')
        elif new_speed == 10:
            self.buttons['speed10']['rect'].set_facecolor('darkred')
        
        self.speed_multiplier = new_speed
        print(f"🚀 Velocidad cambiada a {self.speed_names[new_speed]}")
        
        self.fig.canvas.draw()
    
    def _toggle_stats(self):
        """Toggle de estadísticas (simulado - requeriría reconfigurar layout)"""
        current_text = self.buttons['stats']['current_text']
        new_text = '📊 OFF' if '📊 ON' in current_text else '📊 ON'
        self.buttons['stats']['current_text'] = new_text
        
        print(f"📊 Estadísticas: {'Activadas' if 'ON' in new_text else 'Desactivadas'}")
        print("   (Reinicia la simulación para aplicar cambios)")
        
        self._update_button_texts()
        self.fig.canvas.draw()
    
    def _reset_simulation(self):
        """Resetear simulación al estado inicial"""
        print("🔄 Reiniciando simulación...")
        self.time = 0
        self.paused = False
        self.speed_multiplier = 1
        
        # Resetear datos de estadísticas
        self.riders_now = []
        self.queued_now = []
        self.departed_total = []
        
        # Resetear visitantes y atracciones
        spawns = self.terrain.spawn_points
        exits = self.terrain.exit_points
        
        from patrons import PatronType
        self.patrons = []
        for i in range(len(self.patrons) if hasattr(self, 'original_patron_count') else 60):
            patron_type = self._assign_patron_type(i, 60)
            patron = Patron(name=f"P{i:03d}", spawns=spawns, exits=exits, 
                          terrain=self.terrain, patron_type=patron_type)
            self.patrons.append(patron)
        
        # Resetear rides
        for ride in self.rides:
            ride.queue = []
            ride.riders = []
            ride.state = "idle"
            ride.timer = 0
        
        # Actualizar botones
        self.buttons['pause']['current_text'] = '⏸️'
        self.buttons['pause']['rect'].set_facecolor('lightgreen')
        self._set_speed(1)  # Resetear velocidad
        
        print("✅ Simulación reiniciada")
    
    def _exit_simulation(self):
        """Salir de la simulación"""
        print("👋 Cerrando simulación...")
        self.running = False
        plt.close('all')

    def _on_key_press(self, event):
        """🎯 ÉPICA 4: Maneja controles de teclado (mantenido como alternativa)"""
        if event.key == ' ':  # Barra espaciadora para pausar/reanudar
            self._toggle_pause()
        elif event.key == '1':  # Velocidad normal (1x)
            self._set_speed(1)
        elif event.key == '5':  # Velocidad rápida (5x)
            self._set_speed(5)
        elif event.key == '0':  # Velocidad muy rápida (10x)
            self._set_speed(10)
        elif event.key == 'h':  # Mostrar ayuda
            self._show_controls_help()
        elif event.key == 'r':  # Reset
            self._reset_simulation()
        elif event.key == 'q':  # Quit
            self._exit_simulation()

    def _show_controls_help(self):
        """🎯 ÉPICA 4: Muestra la ayuda de controles"""
        print("\n" + "="*60)
        print("🎮 CONTROLES DE SIMULACIÓN - ÉPICA 4")
        print("="*60)
        print("🖱️  CONTROLES POR CLICK:")
        print("   ⏸️/▶️  - Pausar/Reanudar simulación")
        print("   🐌 1x  - Velocidad normal")
        print("   🏃 5x  - Velocidad rápida") 
        print("   🚀 10x - Velocidad muy rápida")
        print("   📊     - Toggle estadísticas")
        print("   🔄     - Reiniciar simulación")
        print("   ❌     - Salir")
        print("\n⌨️  CONTROLES POR TECLADO (alternativo):")
        print("   ESPACIO - Pausar/Reanudar")
        print("   1,5,0   - Cambiar velocidad")
        print("   R       - Reiniciar") 
        print("   Q       - Salir")
        print("   H       - Mostrar esta ayuda")
        print("="*60 + "\n")

    def step(self):
        for ride in self.rides:
            ride.step_change(self.time)
        for p in self.patrons:
            p.step_change(self.time, self.rides)

        # Estadísticas básicas
        riders = sum(len(r.riders) for r in self.rides)
        queued = sum(len(r.queue) for r in self.rides)
        departed = sum(1 for p in self.patrons if p.state == "left")
        
        # 🎯 ÉPICA 2: Estadísticas avanzadas por tipo de visitante
        abandoned_total = sum(p.abandoned_queues for p in self.patrons)
        
        self.riders_now.append(riders)
        self.queued_now.append(queued)  
        self.departed_total.append(departed)
        
        # Nuevo: estadísticas de abandono para Epic 2
        if not hasattr(self, 'abandoned_now'):
            self.abandoned_now = []
        self.abandoned_now.append(abandoned_total)
        
        self.time += 1

    def draw(self):
        self.ax_map.clear()
        self.ax_map.set_xlim(-1, self.terrain.width + 1)
        self.ax_map.set_ylim(-1, self.terrain.height + 1)
        self.ax_map.set_aspect("equal")
        
        # 🎯 ÉPICA 4: Mostrar estado de simulación en el título
        status = "⏸️ PAUSADA" if self.paused else f"▶️ {self.speed_names[self.speed_multiplier]}"
        self.ax_map.set_title(f"AdventureWorld Park - {status} [T:{self.time}]")
        self.ax_map.grid(True, alpha=0.2)

        self.terrain.plot(self.ax_map)
        for ride in self.rides:
            ride.plot(self.ax_map, self.time)
        for p in self.patrons:
            p.plot(self.ax_map)

        if self.ax_stats is not None:
            self.ax_stats.clear()
            self.ax_stats.set_title("🎯 Epic 2: Stats Avanzadas")
            self.ax_stats.set_xlabel("timestep")
            self.ax_stats.plot(self.riders_now, label="riding", color="green")
            self.ax_stats.plot(self.queued_now, label="queueing", color="orange") 
            self.ax_stats.plot(self.departed_total, label="departed", color="red")
            
            # 🎯 ÉPICA 2: Nueva estadística de abandono
            if hasattr(self, 'abandoned_now') and self.abandoned_now:
                self.ax_stats.plot(self.abandoned_now, label="abandoned", 
                                 color="purple", linestyle="--")
            
            self.ax_stats.legend(loc="upper left")
            self.ax_stats.grid(True, alpha=0.3)

        # 🎯 ÉPICA 4: Pausa ajustable según velocidad
        pause_time = 0.001 / self.speed_multiplier if not self.paused else 0.05
        plt.pause(pause_time)

    def run(self):
        # � ÉPICA 4: Simulación con controles visuales
        self._show_controls_help()
        print(f"🚀 Iniciando simulación de {self.steps} pasos...")
        print("🖱️ ¡Haz click en los botones para controlar la simulación!")
        
        step_count = 0
        try:
            while step_count < self.steps and self.running:
                # Verificar si la ventana fue cerrada
                if not plt.fignum_exists(self.fig.number):
                    print("👋 Ventana cerrada - terminando simulación")
                    break
                
                if not self.paused:
                    # Solo avanzar la simulación si no está pausada
                    for _ in range(self.speed_multiplier):  # Múltiples pasos según velocidad
                        if step_count < self.steps and self.running:
                            self.step()
                            step_count += 1
                        else:
                            break
                
                # Siempre dibujar (para mostrar estado de pausa)
                if self.running:
                    self.draw()
                
                # Pausa inteligente según estado
                if self.paused:
                    plt.pause(0.1)  # Pausa más larga para no consumir CPU
                else:
                    plt.pause(0.01)  # Pausa mínima para fluidez
                    
        except KeyboardInterrupt:
            print("\n⏸️ Simulación interrumpida con Ctrl+C")
        except Exception as e:
            print(f"\n❌ Error en simulación: {e}")
        
        if self.running and step_count >= self.steps:
            print(f"\n✅ Simulación completada en {step_count} pasos")
            # 🎯 ÉPICA 2: Reporte final mejorado
            self._print_epic2_report()
        
        if self.running:
            # Cambiar botón de salir por "Finalizado"
            self.buttons['exit']['current_text'] = '✅ OK'
            self.buttons['exit']['rect'].set_facecolor('lightgreen')
            self._update_button_texts()
            self.fig.canvas.draw()
            
            print("\n🎮 Simulación finalizada - Usa el botón ✅ OK para cerrar")
            print("   O cierra la ventana manualmente")
            
            # Mantener ventana abierta hasta que el usuario decida cerrar
            while self.running and plt.fignum_exists(self.fig.number):
                plt.pause(0.1)
        
        plt.close('all')
        
    def _print_epic2_report(self):
        """🎯 ÉPICA 2: Reporte detallado de visitantes por tipo"""
        print("\n" + "="*60)
        print("🎯 ÉPICA 2: REPORTE FINAL DE VISITANTES")
        print("="*60)
        
        # Estadísticas por tipo de visitante
        from patrons import PatronType
        type_stats = {ptype: {"count": 0, "completed": 0, "abandoned": 0, "departed": 0} 
                     for ptype in PatronType}
        
        for patron in self.patrons:
            ptype = patron.patron_type
            type_stats[ptype]["count"] += 1
            type_stats[ptype]["completed"] += patron.rides_completed
            type_stats[ptype]["abandoned"] += patron.abandoned_queues
            if patron.state == "left":
                type_stats[ptype]["departed"] += 1
        
        print(f"👥 Distribución de visitantes:")
        for ptype, stats in type_stats.items():
            icon = {"aventurero": "🏴‍☠️", "familiar": "👨‍👩‍👧", "impaciente": "⚡", "explorador": "🔍"}.get(ptype.value, "👤")
            avg_rides = stats["completed"] / max(stats["count"], 1)
            avg_abandoned = stats["abandoned"] / max(stats["count"], 1)
            
            print(f"   {icon} {ptype.value.capitalize()}: {stats['count']:2d} visitantes")
            print(f"      Rides promedio: {avg_rides:.1f}")
            print(f"      Abandonos promedio: {avg_abandoned:.1f}")
            print(f"      Salieron del parque: {stats['departed']}")
        
        # Estadísticas generales
        total_rides = sum(p.rides_completed for p in self.patrons)
        total_abandoned = sum(p.abandoned_queues for p in self.patrons)
        total_departed = sum(1 for p in self.patrons if p.state == "left")
        
        print(f"\n📊 Resumen general:")
        print(f"   🎢 Total rides completados: {total_rides}")
        print(f"   🚶 Total abandonos de cola: {total_abandoned}")
        print(f"   🚪 Visitantes que salieron: {total_departed}/{len(self.patrons)}")
        
        if total_rides > 0:
            abandono_rate = (total_abandoned / (total_rides + total_abandoned)) * 100
            print(f"   📈 Tasa de abandono: {abandono_rate:.1f}%")
        
        print("="*60)


if __name__ == "__main__":
    args = parse_args()
    
    # Configurar semilla aleatoria si se especifica
    if args.seed is not None:
        random.seed(args.seed)

    # Determinar fuente de configuración y cargar parámetros
    config_source = "default"
    
    if args.config:
        # Prioridad 1: Configuración YAML
        config = load_config_yaml(args.config)
        if config:
            config_source = "yaml"
            
            # Configuración del parque
            park_config = config.get('park', {})
            terrain = Terrain.from_size(
                park_config.get('width', 100), 
                park_config.get('height', 70)
            )
            
            # Configuración de atracciones
            rides_params = []
            for ride_config in config.get('rides', []):
                rides_params.append({
                    'type': ride_config.get('type', 'pirate'),
                    'capacity': ride_config.get('capacity', 12),
                    'duration': ride_config.get('duration', 40),
                    'bbox': tuple(ride_config.get('bbox', [10, 10, 20, 12]))
                })
            
            # Si no hay rides en YAML, usar defaults
            if not rides_params:
                rides_params = [
                    {"type": "pirate", "capacity": 12, "duration": 40, "bbox": (10, 10, 20, 12)},
                    {"type": "ferris", "capacity": 20, "duration": 70, "bbox": (45, 15, 20, 20)},
                ]
            
            rides = build_rides(rides_params, terrain)
            
            # Configuración de visitantes
            num_patrons = config.get('patrons', {}).get('count', 60)
            
            # Configuración de simulación (los argumentos CLI tienen precedencia)
            simulation_config = config.get('simulation', {})
            steps = args.steps if args.steps != 300 else simulation_config.get('steps', 300)
            stats = args.stats or simulation_config.get('stats', False)
            seed = args.seed if args.seed is not None else simulation_config.get('seed', None)
            
            # Aplicar semilla si viene del YAML y no se especificó en CLI
            if seed is not None and args.seed is None:
                random.seed(seed)
        else:
            # Si falla la carga de YAML, usar configuración por defecto
            print("Usando configuración por defecto debido a errores en YAML...")
            config_source = "default"
            terrain = Terrain.from_size(100, 70)
            rides_params = [
                {"type": "pirate", "capacity": 12, "duration": 40, "bbox": (10, 10, 20, 12)},
                {"type": "ferris", "capacity": 20, "duration": 70, "bbox": (45, 15, 20, 20)},
            ]
            rides = build_rides(rides_params, terrain)
            num_patrons = 60
            steps = args.steps
            stats = args.stats
            seed = args.seed
    
    elif args.interactive:
        # Prioridad 2: Modo interactivo
        config_source = "interactive"
        terrain, rides, num_patrons = interactive_setup()
        steps = args.steps
        stats = args.stats 
        seed = args.seed
        
    else:
        # Prioridad 3: Archivos CSV individuales o defaults
        if args.rides_csv or args.patrons_csv or args.map_csv:
            config_source = "csv"
        else:
            config_source = "default"
            
        terrain = Terrain.from_csv(args.map_csv) if args.map_csv else Terrain.from_size(100, 70)
        rides_params = read_rides_csv(args.rides_csv) if args.rides_csv else [
            {"type": "pirate", "capacity": 12, "duration": 40, "bbox": (10, 10, 20, 12)},
            {"type": "ferris", "capacity": 20, "duration": 70, "bbox": (45, 15, 20, 20)},
        ]
        rides = build_rides(rides_params, terrain)
        num_patrons = read_patrons_csv(args.patrons_csv) if args.patrons_csv else 60
        steps = args.steps
        stats = args.stats
        seed = args.seed

    # Imprimir configuración final utilizada
    print_final_config(terrain, rides, num_patrons, steps, seed, stats, config_source)

    # Ejecutar simulación
    sim = Simulation(terrain, rides, num_patrons, steps=steps, show_stats=stats)
    sim.run()

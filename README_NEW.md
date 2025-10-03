# 🎢 AdventureWorld - Simulación Modular de Parque Temático

## 📁 Estructura del Proyecto

```
AdventureWorld/
├── 📊 data/                          # Archivos de datos
│   ├── map1.csv                     # Configuración del mapa
│   └── rides.csv                    # Configuración de atracciones
│
├── 🏗️  models/                       # Modelos de datos
│   ├── __init__.py
│   ├── patron_types.py              # Enums y tipos de visitantes
│   └── patron.py                    # Clase Patron refactorizada
│
├── 🎯 behaviors/                     # Comportamientos especializados
│   ├── __init__.py
│   ├── movement_behavior.py         # Movimiento y pathfinding
│   ├── decision_behavior.py         # Toma de decisiones
│   └── queue_behavior.py            # Comportamiento en colas
│
├── 🎠 rides/                         # Sistema de atracciones
│   ├── __init__.py
│   ├── ride_states.py              # Estados y temporización
│   ├── base_ride.py                # Clase base de atracciones
│   ├── ride_visuals.py             # Visualización de atracciones
│   └── ride_types.py               # PirateShip y FerrisWheel
│
├── 🖥️  interface/                    # Interface de usuario modular
│   ├── __init__.py
│   ├── cli.py                      # Interface de línea de comandos
│   ├── display.py                  # Gestor de visualización
│   ├── controls.py                 # Gestor de controles
│   ├── renderers/                  # Renderizadores especializados
│   │   ├── __init__.py
│   │   ├── map_renderer.py         # Renderizado del mapa
│   │   ├── stats_renderer.py       # Renderizado de estadísticas
│   │   └── button_renderer.py      # Renderizado de botones
│   └── events/                     # Manejadores de eventos
│       ├── __init__.py
│       ├── mouse_handler.py        # Eventos de mouse
│       └── keyboard_handler.py     # Eventos de teclado
│
├── ⚙️  config/                       # Configuración
│   ├── __init__.py
│   └── loader.py                   # Cargador de configuración
│
├── 🔧 core/                          # Motor de simulación
│   ├── __init__.py
│   └── engine.py                   # Motor principal
│
├── 🧮 simulation/                    # Lógica de simulación
│   ├── __init__.py
│   ├── terrain.py                  # Gestión del terreno
│   └── utils.py                    # Utilidades generales
│
├── 📜 scripts/                       # Scripts de ejecución
│   └── adventureworld.py           # Script principal
│
├── 📦 backup/                        # Archivos backup
│   └── [archivos_old.py]
│
├── 🌐 adventure_env/                 # Entorno virtual Python
├── 📖 contexto/                      # Documentación del desarrollo
├── 🗃️  __pycache__/                  # Cache de Python
├── 🚀 run_simulation.py              # Launcher principal
├── 📋 requirements.txt               # Dependencias
├── 📄 README.md                      # Este archivo
└── 📋 PROYECTO.md                    # Documentación del proyecto
```

## 🚀 Ejecución

### Método Recomendado (desde la raíz):
```bash
# Activar entorno virtual
source adventure_env/bin/activate

# Ejecutar simulación (configuración por defecto)
python run_simulation.py

# Ejecutar con estadísticas en vivo
python run_simulation.py --stats

# Ejecutar con semilla específica para reproducibilidad
python run_simulation.py --stats --seed 123

# Ver todas las opciones
python run_simulation.py --help
```

### Método Alternativo (script directo):
```bash
source adventure_env/bin/activate
cd scripts/
python adventureworld.py
```

## 🏗️ Arquitectura

### Principios de Diseño Aplicados:
- ✅ **Separación de Responsabilidades**: Cada módulo tiene una función específica
- ✅ **Principio de Responsabilidad Única**: Archivos pequeños (20-140 líneas)
- ✅ **Composición sobre Herencia**: Uso de componentes especializados
- ✅ **Inversión de Dependencias**: Interfaces claramente definidas
- ✅ **Modularidad**: Fácil mantenimiento y testing

### Patrones Implementados:
- 🔧 **Strategy Pattern**: Comportamientos intercambiables
- 🏗️ **Builder Pattern**: Construcción de objetos complejos
- 👀 **Observer Pattern**: Actualización de visualización
- 🎛️ **Command Pattern**: Manejo de eventos de usuario

## 📊 Beneficios del Refactoring

**Antes:** 4 archivos grandes (240-393 líneas cada uno)
**Después:** 19+ módulos especializados (20-140 líneas cada uno)

### Mejoras Logradas:
- 🔍 **Mantenibilidad**: Código más fácil de entender y modificar
- 🧪 **Testabilidad**: Módulos pequeños más fáciles de probar
- 📈 **Escalabilidad**: Estructura lista para nuevas funcionalidades
- 📖 **Legibilidad**: Archivos concentrados en una responsabilidad
- 🔄 **Reutilización**: Componentes intercambiables y modulares

## 🎮 Características

- **Épica 1**: Configuración del Parque ✅
- **Épica 2**: Sistema Avanzado de Visitantes ✅  
- **Épica 3**: Sistema Avanzado de Atracciones ✅
- **Épica 4**: Controles Interactivos Avanzados ✅

### Controles Disponibles:
- 🖱️ **Click**: Botones interactivos para control
- ⌨️ **Teclado**: Atajos de teclado para todas las funciones
- ⏸️ **Pausa/Resume**: Control de simulación en tiempo real
- ⚡ **Velocidades**: 1x, 5x, 10x velocidad
- 🔄 **Reset**: Reiniciar simulación instantáneamente
- 📊 **Stats**: Panel de estadísticas en tiempo real

## 🛠️ Tecnologías

- **Python 3.12+**
- **Matplotlib**: Visualización interactiva
- **NumPy**: Computación numérica
- **PyYAML**: Configuración (opcional)

---

*Desarrollado como proyecto estudiantil con arquitectura profesional modular*
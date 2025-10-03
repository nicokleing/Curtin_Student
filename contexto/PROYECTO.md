# 🎢 AdventureWorld - Simulación de Parque de Diversiones

## 📁 Estructura del Proyecto

### 🚀 Archivos Principales
- **`adventureworld.py`** - Punto de entrada principal de la simulación
- **`requirements.txt`** - Dependencias del proyecto (matplotlib, numpy, pyyaml)

### 📦 Módulos Core
- **`core/engine.py`** - Motor de simulación principal
- **`interface/display.py`** - Visualización con matplotlib
- **`interface/controls.py`** - Controles interactivos y eventos
- **`interface/cli.py`** - Interface de línea de comandos
- **`config/loader.py`** - Carga de configuración

### 🎯 Clases de Dominio
- **`patrons.py`** - Visitantes del parque (tipos y comportamientos)
- **`rides.py`** - Atracciones (Barco Pirata, Noria)
- **`terrain.py`** - Mapa del parque
- **`utils.py`** - Funciones auxiliares

### 🗺️ Archivos de Configuración
- **`map1.csv`** - Mapa del terreno del parque
- **`rides.csv`** - Configuración de atracciones

### 📚 Documentación
- **`contexto/`** - Documentación de refactorización y análisis
- **`contexto/NORMAS_DESARROLLO.md`** - Normas estrictas de código profesional

## 🎮 Cómo Ejecutar

```bash
# Activar entorno virtual
source adventure_env/bin/activate

# Ejecutar simulación
python adventureworld.py

# Con opciones
python adventureworld.py --stats --seed 123 --steps 500
```

## 🎯 Arquitectura Modular

El proyecto está organizado siguiendo principios de arquitectura limpia:

1. **Separación de responsabilidades** - Cada módulo tiene un propósito específico
2. **Bajo acoplamiento** - Los módulos son independientes entre sí
3. **Alta cohesión** - Funciones relacionadas están agrupadas
4. **Facilidad de mantenimiento** - Código organizado y documentado

## ✨ Características

- 🎢 Simulación de atracciones (Barco Pirata, Noria)
- 👥 Visitantes con diferentes tipos y comportamientos  
- 🎮 Controles interactivos (pause, velocidades, reset)
- 📊 Estadísticas en tiempo real
- 🗺️ Visualización del parque con matplotlib
- ⚙️ Configuración flexible via CSV/YAML
# Adventu## D# AdventureWorld - Simulador de Parque Temá## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)  
3. [Technical Architecture](#technical-architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [Configuration Options](#configuration-options)
7. [File Formats](#file-formats)
8. [Simulation Mechanics](#simulation-mechanics)
9. [Visual Interface](#visual-interface)
10. [Troubleshooting](#troubleshooting)
11. [Technical Implementation](#technical-implementation)
12. [Academic Learning Outcomes](#academic-learning-outcomes) Project - Fundamentals of Programming (FOP)**  
**Author:** Nicolás Klein - Curtin University  
**Course:** Fundamentals of Programming  
**Academic Year:** 2025

---

## Documentación Organizada

**All technical documentation and context files are organized in [`contexto/`](./contexto/)**

Consulta [`contexto/README_CONTEXTO.md`](./contexto/README_CONTEXTO.md) para un índice completo de:
- Especificaciones técnicas
- Epic status and development progress  
- Example configurations
- Test and validation filesion

All technical documentation and context files are organized in the `contexto/` folder.

Ver `contexto/README_CONTEXTO.md` para índice completo de especificaciones técnicas, progreso de desarrollo, configuraciones de ejemplo y archivos de prueba. Simulador de Parque Temático

**Final Project - Fundamentals of Programming (FOP)**  
**Author:** Nicolás Klein - Curtin University  
**Course:** Fundamentals of Programming  
**Academic Year:** 2025

---

## � Documentación Organizada

**All technical documentation and context files are organized in [`contexto/`](./contexto/)**

Consulta [`contexto/README_CONTEXTO.md`](./contexto/README_CONTEXTO.md) para un índice completo de:
- 📖 Especificaciones técnicas
- Epic status and development progress  
- Example configurations
- Test and validation files

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic simulation
python run_simulation.py

# Run with YAML configuration
python run_simulation.py --config contexto/config_test.yaml

# Interactive mode
python run_simulation.py -i
```

## �📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)  
3. [Technical Architecture](#-technical-architecture)
4. [Installation & Setup](#-installation--setup)
5. [Usage Guide](#-usage-guide)
6. [Configuration Options](#-configuration-options)
7. [File Formats](#-file-formats)
8. [Simulation Mechanics](#-simulation-mechanics)
9. [Visual Interface](#-visual-interface)
10. [Troubleshooting](#-troubleshooting)
11. [Technical Implementation](#-technical-implementation)
12. [Academic Learning Outcomes](#-academic-learning-outcomes)

---

## Project Overview

**AdventureWorld** es un simulador de parque temático en tiempo real desarrollado como proyecto final de Fundamentos de Programación (FOP). El proyecto incluye simulación interactiva de comportamiento de visitantes, operaciones de atracciones y dinámicas del parque.

### Simulation Highlights
- **Real-time Visualization**: Dynamic matplotlib-based graphics with live updates
- **Sistema de Visitantes**: Modelado de comportamiento de visitantes con máquinas de estado
- **Interactive Park Management**: Multiple configuration methods (CLI, CSV, interactive)
- **Statistical Analysis**: Live performance monitoring and data visualization
- **Modular Architecture**: Clean, maintainable code following OOP principles

---

## Key Features

### Sistema de Visitantes
- **Multi-State Behavior**: Visitors transition through realistic states:
  - `EXPLORING`: Random movement and attraction discovery
  - `QUEUING`: Waiting in line with patience mechanics  
  - `RIDING`: Experiencing attractions with timed duration
  - `LEAVING`: Exiting the park through designated exits
- **Decision Making**: Probabilistic attraction selection and exit decisions
- **Navegación**: Movimiento evitando obstáculos y barreras
- **Individual Preferences**: Each visitor has unique behavior patterns

### Mecánicas de Atracciones
- **Multiple Ride Types**:
  - `PirateShip`: High-capacity, medium-duration thrill ride
  - `FerrisWheel`: Scenic ride with customizable cabin count
- **Dynamic Operations**:
  - Capacity management with queue systems
  - Realistic loading/unloading cycles
  - Ride duration timing and state management
  - Visual operation indicators (idle/running states)

### Sistema de Terreno
- **Generación de Mapas**: Soporte para layouts personalizados
- **Barrier Management**: Collision detection and pathfinding obstacles
- **Spawn Point System**: Configurable visitor entry points
- **Exit Management**: Multiple park exit locations
- **Dimensiones Variables**: Tamaño de parque personalizable (defecto: 100x70)

### Real-Time Analytics Dashboard
- **Live Statistics Visualization**:
  - Active riders count over time
  - Queue length monitoring  
  - Visitor flow analysis
  - Park capacity utilization
- **Performance Metrics**: Real-time simulation statistics
- **Data Export**: Statistical data for analysis

### Sistema de Configuración
- **Interactive Setup Mode**: Guided configuration wizard
- **CSV-Based Configuration**: External file-based setup
- **Command-Line Interface**: Full parameter control via CLI arguments
- **Reproducible Simulations**: Random seed support for consistent testing

---

## Technical Architecture

```
AdventureWorld/
├── adventureworld.py     # Main simulation engine and CLI interface
├── terrain.py           # Park terrain, barriers, and spatial management
├── patrons.py           # Visitor AI, behavior states, and pathfinding
├── rides.py             # Ride mechanics, operations, and queue management  
├── utils.py             # CSV parsing, ride construction, and utilities
├── README.md            # Complete project documentation
├── .gitignore           # Version control exclusions
├── map1.csv             # Sample terrain configuration
├── rides.csv            # Sample ride configuration
└── patrons.csv          # Sample visitor count configuration
```

### Core Components

#### **Simulation Engine (`adventureworld.py`)**
- Main event loop with configurable step count
- Matplotlib integration for real-time visualization
- Command-line argument parsing and validation
- Statistics collection and display management
- Interactive setup wizard implementation

#### **Terrain Management (`terrain.py`)**
- Grid-based spatial representation system
- Barrier placement and collision detection
- Spawn point and exit location management
- Pathfinding support infrastructure
- CSV-based terrain loading capabilities

#### **Visitor AI System (`patrons.py`)**
- State machine implementation for visitor behavior
- Probabilistic decision-making algorithms
- Queue management and ride selection logic
- Individual visitor tracking and persistence
- Movement validation and constraint handling

#### **Ride Operations (`rides.py`)**
- Abstract ride base class with common functionality
- Specialized ride implementations (PirateShip, FerrisWheel)
- Queue management and capacity enforcement
- Ride state transitions (idle → loading → running → unloading)
- Visual representation and animation support

#### **Utility Functions (`utils.py`)**
- CSV file parsing and validation
- Dynamic ride construction from parameters
- Spawn point generation algorithms
- Matplotlib axes configuration and styling
- Data structure manipulation utilities

---

## Installation & Setup

### **Prerequisites**
- **Python 3.8+** (recommended: Python 3.12)
- **pip** package manager
- **Git** for version control

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/nicokleing/Curtin_Student.git
cd Curtin_Student
git checkout Final-Work
```

### **Step 2: Create Virtual Environment (Recommended)**
```bash
# Create virtual environment
python3 -m venv adventure_env

# Activate environment
source adventure_env/bin/activate  # Linux/macOS
# OR
adventure_env\Scripts\activate     # Windows

# Verify activation
which python  # Should show path to adventure_env
```

### **Step 3: Install Dependencies**
```bash
# Install required packages
pip install matplotlib numpy

# Verify installation
python -c "import matplotlib, numpy; print('Dependencies installed successfully!')"
```

### **Step 4: Verify Installation**
```bash
# Test basic functionality
python3 adventureworld.py --help

# Quick simulation test
python3 adventureworld.py --steps 50
```

---

## 📖 Usage Guide

### **Quick Start**
```bash
# Basic simulation (300 steps, default settings)
python3 adventureworld.py

# Recommended first run (with live statistics)
python3 adventureworld.py --stats --steps 200

# Interactive setup (guided configuration)
python3 adventureworld.py -i
```

### **Execution Modes**

#### **1. Default Mode**
```bash
python3 adventureworld.py
```
**Configuration:**
- Park size: 100x70 units
- Rides: 2 attractions (1 Pirate Ship, 1 Ferris Wheel)
- Visitors: 60 patrons
- Duration: 300 simulation steps

#### **2. Interactive Setup Mode**
```bash
python3 adventureworld.py -i
```
**Features:**
- Guided step-by-step configuration
- Custom park dimensions input
- Individual ride configuration (type, capacity, duration)
- Visitor count specification
- Real-time parameter validation

#### **3. Statistics Mode (Recommended)**
```bash
python3 adventureworld.py --stats
```
**Displays:**
- Main simulation window with park visualization
- Secondary statistics window with live graphs
- Real-time performance metrics

#### **4. Extended Simulation**
```bash
python3 adventureworld.py --steps 500 --stats
```
**Features:**
- Longer simulation duration
- Better pattern observation
- More comprehensive statistics

#### **5. Reproducible Simulation**
```bash
python3 adventureworld.py --seed 42 --stats
```
**Benefits:**
- Consistent results across runs
- Debugging and testing support
- Demonstration reliability

#### **6. CSV Configuration Mode**
```bash
python3 adventureworld.py --rides-csv rides.csv --patrons-csv patrons.csv --stats
```
**Advantages:**
- External configuration management
- Batch simulation setup
- Configuration version control

---

## Configuration Options

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `-i, --interactive` | Flag | False | Enable interactive setup wizard |
| `--map-csv` | String | None | CSV file path for terrain layout |
| `--rides-csv` | String | None | CSV file path for ride configuration |
| `--patrons-csv` | String | None | CSV file path for patron count |
| `--steps` | Integer | 300 | Number of simulation steps to execute |
| `--stats` | Flag | False | Enable live statistics visualization |
| `--seed` | Integer | Random | Random seed for reproducible results |

### Interactive Mode Options

When using `-i` flag, the system prompts for:

1. **Park Dimensions**
   - Width (10-200 units)
   - Height (10-200 units)

2. **Ride Configuration** (for each ride)
   - Ride type (Pirate Ship / Ferris Wheel)
   - Capacity (1-50 visitors)
   - Duration (10-120 time steps)
   - Position (X, Y coordinates)
   - Dimensions (Width, Height)

3. **Visitor Settings**
   - Total visitor count (1-200 patrons)

### **Default Configuration Values**

```python
DEFAULT_SETTINGS = {
    'park_width': 100,
    'park_height': 70,
    'simulation_steps': 300,
    'visitor_count': 60,
    'rides': [
        {
            'type': 'pirate',
            'capacity': 12,
            'duration': 40,
            'position': (20, 30),
            'size': (15, 10)
        },
        {
            'type': 'ferris',
            'capacity': 20,
            'duration': 70,
            'position': (60, 25),
            'size': (18, 18)
        }
    ]
}
```

---

## File Formats

### Rides Configuration CSV (`rides.csv`)

**Format:**
```csv
tipo,capacidad,duracion,x,y,ancho,alto
pirate,12,40,20,30,15,10
ferris,20,70,60,25,18,18
pirate,8,35,15,50,12,8
```

**Field Descriptions:**
- `tipo`: Ride type (`pirate` for Pirate Ship, `ferris` for Ferris Wheel)
- `capacidad`: Maximum visitor capacity (1-50)
- `duracion`: Ride duration in simulation steps (10-120)
- `x,y`: Ride position coordinates (0 to park_width/height)
- `ancho,alto`: Ride dimensions in grid units

**Validation Rules:**
- Coordinates must be within park boundaries
- Rides cannot overlap
- Capacity must be positive integer
- Duration must be reasonable (10-120 steps)

### Patrons Configuration CSV (`patrons.csv`)

**Format:**
```csv
60
```

**Simple single-line format containing total visitor count**

**Alternative Extended Format:**
```csv
patron_count,spawn_rate,exit_probability
60,0.02,0.001
```

### Map Configuration CSV (`map1.csv`)

**Format:**
```csv
0,0,0,1,1,1,0,0,0
0,0,0,1,1,1,0,0,0
0,0,0,0,0,0,0,0,0
1,1,0,0,0,0,0,1,1
```

**Legend:**
- `0`: Free space (visitors can move)
- `1`: Barrier/obstacle (blocked space)

---

## Simulation Mechanics

### Core Simulation Loop

```python
for step in range(total_steps):
    # 1. Update all visitor states and positions
    for patron in patrons:
        patron.step_change(current_time=step, available_rides=rides)
    
    # 2. Process ride operations
    for ride in rides:
        ride.step_change(current_time=step)
    
    # 3. Update visualization
    render_frame(terrain, patrons, rides, step)
    
    # 4. Collect statistics
    update_statistics(patrons, rides, step)
    
    # 5. Check termination conditions
    if all_visitors_left() or step >= max_steps:
        break
```

### Visitor Behavior State Machine

**State Transitions:**
- `EXPLORING → QUEUING`: Probabilistic attraction selection (1% chance per step)
- `QUEUING → RIDING`: When ride becomes available and has capacity
- `RIDING → FINISHED_RIDE`: After ride duration completes
- `FINISHED_RIDE → EXPLORING`: Return to exploration (90% probability)
- `ANY_STATE → LEAVING`: Random exit decision (0.1% chance per step)

### Ride Operation Cycles

**Pirate Ship Cycle:**
1. `IDLE`: Waiting for visitors (brown color)
2. `LOADING`: Visitors board from queue (5 steps)
3. `RUNNING`: Ride operation (duration steps, orange color)
4. `UNLOADING`: Visitors disembark (3 steps)

**Ferris Wheel Cycle:**
1. `IDLE`: Stationary wheel (brown color)
2. `LOADING`: Cabin loading process (8 steps)
3. `RUNNING`: Wheel rotation (duration steps, orange color)
4. `UNLOADING`: Cabin unloading (8 steps)

### Statistics Collection

**Per-Step Metrics:**
- Active riders count
- Total queue length across all rides
- Visitors in each state (exploring, queuing, riding, left)
- Ride utilization percentages
- Average wait times

**Cumulative Metrics:**
- Total visitors served
- Average ride satisfaction
- Park capacity utilization
- Peak usage periods

---

## Visual Interface

### Main Simulation Window

**Visual Elements:**
- **Green Circles**: Visitor spawn points (entry gates)
- **Blue X**: Park exit points
- **Brown Rectangles**: Idle rides
- **Orange Rectangles**: Active/running rides
- **Colored Dots**: Visitors with state-based colors
  - Blue: Exploring the park
  - Yellow: Queuing for rides
  - Red: Currently riding
  - Green: Just finished riding
- **Red Squares**: Terrain barriers/obstacles

**Window Controls:**
- **Mouse Interaction**: Zoom and pan functionality
- **Real-time Updates**: 60 FPS refresh rate
- **Auto-scaling**: Adapts to park dimensions

### Statistics Dashboard (--stats mode)

**Live Graphs:**
1. **Riders Timeline**: Red line showing active riders over time
2. **Queue Timeline**: Yellow line showing total queue length
3. **Departed Visitors**: Blue line showing cumulative exits

**Dashboard Features:**
- **Real-time Updates**: Synchronized with main simulation
- **Interactive Legend**: Click to hide/show data series
- **Performance Indicators**: FPS and step counter
- **Statistical Summary**: Running averages and peaks

### Keyboard Controls
- **Space**: Pause/resume simulation
- **ESC**: Exit simulation early
- **S**: Save current frame as image
- **R**: Reset simulation (if implemented)

---

## Troubleshooting

### Common Issues and Solutions

#### **Issue: `ModuleNotFoundError: No module named 'matplotlib'`**
```bash
# Solution: Install missing dependencies
source adventure_env/bin/activate  # If using virtual environment
pip install matplotlib numpy
```

#### **Issue: `zsh: command not found: python`**
```bash
# Solution: Use python3 instead of python
python3 adventureworld.py --stats
```

#### **Issue: Simulation window closes immediately**
```bash
# Solution: Check for errors and use shorter simulation
python3 adventureworld.py --steps 50 --stats
```

#### **Issue: Permission denied errors**
```bash
# Solution: Check file permissions
chmod +x adventureworld.py
ls -la *.py
```

#### **Issue: Git repository issues**
```bash
# Solution: Verify repository status
git status
git remote -v
git branch
```

### Debug Mode
```bash
# Enable verbose output for debugging
python3 -v adventureworld.py --stats --steps 100
```

### System Requirements Check
```bash
# Verify Python version (should be 3.8+)
python3 --version

# Check installed packages
pip list | grep -E "(matplotlib|numpy)"

# Test basic imports
python3 -c "import matplotlib.pyplot as plt; import numpy as np; print('All imports successful')"
```

---

## Technical Implementation

### Object-Oriented Design Patterns

#### **1. State Pattern (Visitor Behavior)**
```python
class PatronState:
    EXPLORING = "exploring"
    QUEUING = "queuing"
    RIDING = "riding"
    LEAVING = "leaving"
```

#### **2. Factory Pattern (Ride Creation)**
```python
def create_ride(ride_type, parameters):
    if ride_type.startswith('pir'):
        return PirateShip(**parameters)
    elif ride_type.startswith('fer'):
        return FerrisWheel(**parameters)
```

#### **3. Observer Pattern (Statistics Collection)**
```python
class StatisticsCollector:
    def update(self, simulation_state):
        # Collect and update statistics
        pass
```

### Data Structures and Algorithms

#### **Spatial Management**
- **Grid-based Representation**: 2D array for terrain mapping
- **Collision Detection**: O(1) lookup for barrier checking
- **Pathfinding**: A* algorithm for optimal movement (future enhancement)

#### **Queue Management**
- **FIFO Queue Implementation**: First-in, first-out ride queues
- **Priority Queue**: VIP visitor support (extensible)
- **Capacity Management**: Dynamic queue size limiting

#### **Statistical Analysis**
- **Promedios Dinámicos**: Cálculos de ventana deslizante
- **Datos de Series Temporales**: Almacenamiento para gráficos en vivo
- **Performance Metrics**: Real-time FPS and memory monitoring

### Performance Optimizations

#### **Rendering Optimizations**
- **Selective Redrawing**: Only update changed elements
- **Batch Operations**: Group similar drawing operations
- **Mapeo de Colores**: Esquemas pre-computados

#### **Simulation Optimizations**
- **Vectorized Operations**: NumPy-based calculations where applicable
- **Event-driven Updates**: Only process active entities
- **Memory Management**: Efficient object recycling

---

## Academic Learning Outcomes

### Programming Concepts Demonstrated

#### 1. Object-Oriented Programming (OOP)
- **Encapsulation**: Data hiding and method organization
- **Inheritance**: Ride base class and specialized implementations
- **Polymorphism**: Common interfaces for different ride types
- **Abstraction**: Complex behavior simplified into clean interfaces

#### 2. Data Structures and Algorithms
- **Arrays and Lists**: Visitor and ride collections
- **Dictionaries**: Fast state lookup and parameter storage
- **Queues**: FIFO ride queue implementation
- **Sets**: Efficient barrier collision detection

#### 3. File I/O and Data Processing
- **CSV Parsing**: External configuration file handling
- **Error Handling**: Robust file reading with validation
- **Data Validation**: Input sanitization and bounds checking

#### 4. Control Structures
- **State Machines**: Complex visitor behavior modeling
- **Event Loops**: Main simulation timing and control
- **Conditional Logic**: Decision-making algorithms
- **Iteration**: Efficient collection processing

#### 5. Modular Programming
- **Module Organization**: Logical code separation
- **Import Management**: Clean dependency handling
- **Code Reusability**: Utility functions and shared methods
- **Documentation**: Inline and external documentation

### Software Engineering Practices

#### Version Control
- **Git Workflow**: Branch management and commit practices
- **Repository Organization**: Clean project structure
- **.gitignore Configuration**: Appropriate file exclusions

#### Code Quality
- **PEP 8 Compliance**: Python style guide adherence
- **Meaningful Naming**: Descriptive variables and functions
- **Code Comments**: Clear inline documentation
- **Error Handling**: Graceful failure management

#### Testing and Debugging
- **Debug Output**: Error reporting and logging
- **Input Validation**: Robust parameter checking
- **Edge Case Handling**: Boundary condition management

### Project Complexity Analysis

**Lines of Code:** ~1000+ (distributed across multiple modules)
**Classes Implemented:** 6+ (Terrain, Patron, Ride, PirateShip, FerrisWheel, Simulation)
**Design Patterns:** 3+ (State, Factory, Observer)
**External Libraries:** 3 (matplotlib, numpy, argparse, csv)
**Configuration Options:** 10+ command-line parameters
**File Formats:** 3 (CSV terrain, rides, patrons)

---

## Support and Contact

### Getting Help
- **Course Forum**: Post questions in FOP discussion board
- **Office Hours**: Visit instructor during designated times
- **Email Support**: Contact course coordinator for technical issues

### Project Information
- **Developer**: Nicolás Klein
- **Institution**: Curtin University
- **Course**: Fundamentals of Programming (FOP)
- **Project Type**: Final Assignment
- **Development Period**: 2025 Academic Year

### Related Resources
- [Python Official Documentation](https://docs.python.org/3/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [NumPy Documentation](https://numpy.org/doc/stable/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)

---

## License and Academic Integrity

**Academic Use Only**: This project is developed for educational purposes as part of the Fundamentals of Programming coursework at Curtin University. 

**Collaboration Policy**: Individual project following university academic integrity guidelines.

**Code Attribution**: All code developed independently with appropriate citation of external resources and documentation references.

---

*Last Updated: October 2025*  
*Project Version: Final Submission*  
*Documentation Version: 2.0*
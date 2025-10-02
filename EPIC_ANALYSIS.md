# 📋 Épica 1: Configuración del Parque - Análisis Comparativo

## 🎯 Estado de Implementación vs Historias de Usuario

### ✅ **HU-01: Configuración de Dimensiones del Parque**
**Estado: COMPLETAMENTE IMPLEMENTADA** ✓

#### **Funcionalidades Implementadas:**
- ✅ **Modo Interactivo (-i)**: Solicita ancho y alto por consola
- ✅ **Valores por Defecto**: 100x70 si no se especifica
- ✅ **Validación de Entrada**: Manejo de errores con try/catch
- ✅ **Visualización**: Dimensiones reflejadas correctamente en el mapa

#### **Código de Referencia:**
```python
# Líneas 32-39 en adventureworld.py
def interactive_setup():
    print("Modo interactivo (Enter = default)")
    try:
        width = int(input("Ancho [100]: ") or 100)
        height = int(input("Alto [70]: ") or 70)
        # ...
    except ValueError:
        width, height = 100, 70
```

#### **Criterios de Aceptación:**
- ✅ Al iniciar con `-i`, el sistema pide ancho y alto
- ✅ Los valores quedan registrados en `Terrain.from_size(width, height)`
- ✅ Se ven reflejados en el mapa con límites correctos

---

### ✅ **HU-02: Carga desde Archivos CSV**
**Estado: COMPLETAMENTE IMPLEMENTADA** ✓

#### **Funcionalidades Implementadas:**
- ✅ **--rides-csv**: Carga atracciones desde CSV
- ✅ **--patrons-csv**: Carga número de visitantes desde CSV
- ✅ **Parseo Robusto**: Ignora comentarios (#) y líneas vacías
- ✅ **Validación de Formato**: Verifica número correcto de columnas
- ✅ **Manejo de Errores**: Continúa con valores por defecto si hay problemas

#### **Formatos Soportados:**

**rides.csv:**
```csv
# Formato: tipo,capacidad,duracion,x,y,ancho,alto
pirate,12,40,10,10,20,12
ferris,20,70,45,15,20,20
```

**patrons.csv:**
```csv
# Número total de visitantes
60
```

#### **Código de Referencia:**
```python
# utils.py - Función read_rides_csv()
def read_rides_csv(path):
    rides = []
    if path is None:
        return rides
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 7:  # Validación de formato
                continue
            # Parseo y construcción del diccionario...
```

#### **Criterios de Aceptación:**
- ✅ `--rides-csv` y `--patrons-csv` aceptan rutas a archivos
- ✅ Si el archivo está mal formado, ignora líneas problemáticas
- ✅ El sistema no se cae, continúa con valores por defecto

---

### ❌ **HU-03: Configuración YAML**
**Estado: NO IMPLEMENTADA** ❌

#### **Funcionalidad Faltante:**
- ❌ **--config config.yaml**: No existe esta opción
- ❌ **Soporte YAML**: No hay parseo de archivos YAML
- ❌ **Impresión de Configuración**: No se muestra la config usada al final

#### **Implementación Requerida:**

**1. Agregar dependencia:**
```bash
pip install pyyaml
```

**2. Estructura de config.yaml esperada:**
```yaml
# config.yaml
park:
  width: 120
  height: 80

rides:
  - type: pirate
    capacity: 15
    duration: 35
    bbox: [15, 20, 18, 12]
  - type: ferris
    capacity: 24
    duration: 80
    bbox: [50, 25, 22, 22]

patrons:
  count: 75

simulation:
  steps: 400
  seed: 42
  stats: true
```

**3. Modificaciones de código necesarias:**

**A. En `parse_args()` agregar:**
```python
parser.add_argument("--config", default=None, help="Archivo YAML de configuración")
```

**B. Crear función `load_config_yaml()`:**
```python
import yaml

def load_config_yaml(path):
    """Carga configuración desde archivo YAML."""
    if path is None:
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error cargando config YAML: {e}")
        return None
```

**C. En `main()` agregar lógica de configuración:**
```python
if args.config:
    config = load_config_yaml(args.config)
    if config:
        # Sobrescribir argumentos con valores del YAML
        terrain = Terrain.from_size(
            config.get('park', {}).get('width', 100),
            config.get('park', {}).get('height', 70)
        )
        rides_params = config.get('rides', [])
        num_patrons = config.get('patrons', {}).get('count', 60)
        steps = config.get('simulation', {}).get('steps', args.steps)
        # ...
        
        # Imprimir configuración usada
        print("=== Configuración Utilizada ===")
        print(f"Parque: {terrain.width}x{terrain.height}")
        print(f"Atracciones: {len(rides_params)}")
        print(f"Visitantes: {num_patrons}")
        print(f"Pasos: {steps}")
        print("==============================")
```

---

## 📊 **Resumen de Estado de la Épica**

| Historia de Usuario | Estado | Porcentaje | Observaciones |
|-------------------|--------|------------|---------------|
| **HU-01**: Dimensiones del Parque | ✅ Completa | 100% | Totalmente funcional |
| **HU-02**: Carga CSV | ✅ Completa | 100% | Robusto y bien implementado |
| **HU-03**: Configuración YAML | ❌ Faltante | 0% | Requiere implementación |

### **🎯 Porcentaje de Completitud de la Épica: 66.7%**

---

## 🚀 **Funcionalidades Adicionales Implementadas (Bonus)**

El proyecto incluye características que van más allá de la épica básica:

### ✅ **Características Extra:**
1. **Modo de Estadísticas en Vivo** (`--stats`)
   - Gráficos en tiempo real
   - Métricas de visitantes montando, en cola y que han salido

2. **Semilla Aleatoria Reproducible** (`--seed`)
   - Simulaciones determinísticas para testing
   - Resultados reproducibles

3. **Configuración de Pasos** (`--steps`)
   - Control de duración de simulación
   - Valor por defecto: 300 pasos

4. **Soporte para Mapas CSV** (`--map-csv`)
   - Carga de terreno personalizado
   - Formato 0=libre, 1=barrera

### ✅ **Robustez del Sistema:**
- Manejo de errores en entrada de usuario
- Valores por defecto sensatos en todos los parámetros
- Documentación completa de argumentos (`--help`)
- Validación de formato de archivos CSV

---

## 🎯 **Recomendaciones para Completar la Épica**

### **Prioridad Alta:**
1. **Implementar HU-03** - Soporte para configuración YAML
   - Agregar dependencia PyYAML
   - Crear función de parseo YAML
   - Implementar lógica de sobrescritura de parámetros
   - Agregar impresión de configuración final

### **Prioridad Media:**
1. **Mejorar manejo de errores** en carga CSV
   - Mostrar errores específicos por línea
   - Logs más detallados de problemas de parseo

2. **Validación de configuración** más estricta
   - Verificar rangos válidos para dimensiones
   - Validar que las atracciones no se superpongan

### **Valor Académico:**
La implementación actual demuestra:
- ✅ **Parseo de archivos** (CSV)
- ✅ **Interfaces de línea de comandos** (argparse)
- ✅ **Configuración flexible** (interactivo vs archivos)
- ✅ **Manejo de errores** robusto
- ✅ **Valores por defecto** sensatos

La adición de soporte YAML completaría el demostración de:
- 📝 **Formatos de configuración modernos**
- 📝 **Jerarquías de configuración** (CLI > YAML > defaults)
- 📝 **Serialización/deserialización** de datos

---

## 📋 **Plan de Implementación para HU-03**

### **Paso 1: Dependencias**
```bash
echo "pyyaml>=6.0" >> requirements.txt
pip install pyyaml
```

### **Paso 2: Estructura de Archivos**
- Crear `config_example.yaml` con ejemplo completo
- Actualizar documentación en README.md

### **Paso 3: Código**
- Modificar `parse_args()` 
- Crear `load_config_yaml()` en utils.py
- Integrar en lógica principal
- Agregar función de impresión de configuración

### **Paso 4: Testing**
- Crear archivos YAML de prueba
- Verificar precedencia de parámetros
- Validar manejo de errores

**Tiempo estimado:** 2-3 horas de desarrollo
**Complejidad:** Baja-Media
**Valor académico:** Alto
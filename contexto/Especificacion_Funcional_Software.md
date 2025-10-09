# Especificación Funcional del Software (EFS) - AdventureWorld

## 1. Propósito y Alcance

### Propósito
Simular, visualizar y medir el funcionamiento de un parque de atracciones con visitantes y colas, para fines educativos de Fundamentos de Programación (POO, simulación discreta, lectura de CSV, visualización).

### Alcance
- Crear un parque 2D con límites, obstáculos, entradas y salidas.
- Incluir ≥2 atracciones (FerrisWheel, PirateShip) con capacidad, duración, cola y estados.
- Simular visitantes que se mueven, hacen cola, montan y salen.
- Ejecutar en modo interactivo o por argumentos/CSV.
- (Postgrad) Mostrar estadísticas en vivo y resumen final.

### Fuera de alcance (esta entrega)
Pathfinding A*, economía completa, IA avanzada, persistencia en BD, UI gráfica distinta a matplotlib.

## 2. Actores y Perfiles

- **Usuario**: ejecuta la app, define parámetros (interactivo o CLI), observa el mapa y (postgrad) estadísticas.
- **Analista** (mismo usuario en rol analítico): interpreta KPIs y exporta resultados.
- **Entidades Simuladas**: Patrons (visitantes) y Rides (atracciones).

## 3. Suposiciones y Dependencias

- Python 3.10+; librerías estándar y matplotlib, numpy (opcional).
- CSV bien formados (o validación con error claro).
- Semilla (--seed) fija todas las decisiones pseudoaleatorias.
- La simulación es discreta por ticks (Δt = 1).

## 4. Requisitos Funcionales

### 4.1 Configuración y Entrada

**RF-01.** El sistema debe permitir modo interactivo (-i) para configurar: ancho/alto del parque, nº de rides, nº de patrons, capacity y duration por ride. (HU-11)

**RF-02.** El sistema debe aceptar argumentos para ejecutar directo:
--width, --height, --steps, --rides-csv, --patrons-csv, --stats (postgrad), --seed, --save-run. (HU-12, HU-14, HU-15, HU-16)

**RF-03.** El sistema debe leer CSV:
- `rides.csv`: id,name,type,x,y,width,height,capacity,duration,queue_limit
- `patrons.csv`: id,spawn_x,spawn_y
y validar campos con mensajes claros. (HU-02, HU-03)

**RF-04.** (Opcional) --config config.yaml puede sobreescribir parámetros y rutas de CSV.

### 4.2 Terreno y Geometría

**RF-05.** Debe crear un mapa rectangular de dimensiones configurables. (HU-09)

**RF-06.** Debe soportar obstáculos (celdas o rectángulos no transitables). (HU-09)

**RF-07.** Debe definir entradas (spawn, verde) y salidas (azul) del parque. (HU-10)

### 4.3 Atracciones (Rides)

**RF-08.** Cada ride debe tener posición y tamaño (bounding box) sin solaparse con otras. (HU-03)

**RF-09.** Cada ride debe tener cola (FIFO) con queue_limit. (HU-07, HU-08)

**RF-10.** Cada ride opera con estados: IDLE → LOADING → RUNNING → UNLOADING → IDLE. (HU-01)

**RF-11.** En la transición LOADING, el ride embarca hasta capacity patrons de la cola; en RUNNING consume duration ticks; en UNLOADING descarga a los pasajeros. (HU-02)

### 4.4 Visitantes (Patrons)

**RF-12.** Un patron tiene ciclo de vida: ROAMING → QUEUING → RIDING → EXITED. (HU-04)

**RF-13.** Los patrons se mueven un paso por tick hacia su objetivo, evitando obstáculos y rides. (HU-05)

**RF-14.** Los patrons deciden objetivos: al terminar un ride, con probabilidad configurable, eligen otro ride o una salida; en cola llena, eligen otra opción. (HU-06, HU-08)

**RF-15.** Los patrons en QUEUE permanecen estáticos hasta embarcar o cambiar de objetivo. (HU-07)

### 4.5 Motor de Simulación

**RF-16.** La simulación debe avanzar por ticks, actualizando primero rides o patrons según política fija (determinismo). (HU-13)

**RF-17.** --seed debe fijar la reproducibilidad (random, orden de desempates). (HU-14)

### 4.6 Visualización y Estadísticas

**RF-18.** Debe renderizar un mapa matplotlib:
Spawn (verde), salida (azul), rides (marrón / naranja si RUNNING), obstáculos (rojo), patrons coloreados por estado. (HU-16)

**RF-19.** (Postgrad) --stats debe mostrar subplots con:
Nº en cola total, nº en ride total, nº salidos; actualizados en vivo. (HU-15)

**RF-20.** (Postgrad) Al finalizar, imprimir resumen (KPIs) y, si --save-run, exportar events.csv, summary.json, plot.png. (HU-16)

## 5. Requisitos No Funcionales

**RNF-01.** Usabilidad: CLI clara, --help, mensajes de error legibles.

**RNF-02.** Input validation: if a CSV is invalid, stop and show a clear error message explaining the problem.

**RNF-03.** Rendimiento: 60–200 patrons y 2–6 rides deben correr fluido (actualización y render sin parpadeos notables).

**RNF-04.** Calidad de código: PEP8, docstrings, sin globals innecesarios, sin while True descontrolado.

## 6. Casos de Uso (resumen)

### CU-01. Configurar y lanzar (interactivo)
- Usuario ejecuta `python adventureworld.py -i`.
- El sistema solicita dimensiones, nº rides, nº patrons, capacity/duration por ride.
- Se crea el parque y comienza la simulación.

### CU-02. Cargar escenario por CSV y lanzar
- Usuario ejecuta `python adventureworld.py --rides-csv data/rides.csv --patrons-csv data/patrons.csv --steps 300 --seed 42 --stats`.
- Se validan CSV; se inicializa estado; se simula y visualiza con stats.

### CU-03. Exportar resultados
- Usuario añade `--save-run`.
- Al finalizar, se crean `runs/<timestamp>/{events.csv,summary.json,plot.png}`.

## 7. Datos y Formatos

### 7.1 CSV de Rides (rides.csv)
```csv
id,name,type,x,y,width,height,capacity,duration,queue_limit
R1,FerrisWheel,FERRIS,20,15,4,4,12,10,24
R2,PirateShip,PIRATE,60,30,5,3,20,8,30
```

### 7.2 CSV de Patrons (patrons.csv)
```csv
id,spawn_x,spawn_y
P1,2,5
P2,2,5
```

### 7.3 Resumen (summary.json)
```json
{
  "seed": 42,
  "steps": 300,
  "park": {"width":100,"height":70},
  "rides": [{"id":"R1","type":"FERRIS","capacity":12,"duration":10}],
  "kpis": {
    "total_served": 180,
    "avg_wait_time": 7.4,
    "avg_queue_length": 9.2,
    "ride_utilization": {"R1":0.82,"R2":0.77}
  }
}
```

### 7.4 Eventos (events.csv)
```csv
tick,event_type,entity_id,ride_id,extra
12,QUEUE_ENTER,P17,R1,
20,BOARD,P04,R1,seat=10
30,UNBOARD,P04,R1,
45,EXIT,P04,,
```

## 8. Reglas de Negocio y Lógica

**RB-01.** Colas: FIFO; no se admiten más de queue_limit.

**RB-02.** Embarque: al entrar en LOADING, el ride toma min(capacity, len(queue)) patrons y los marca RIDING.

**RB-03.** Ciclos de ride: LOADING(1-2 ticks) → RUNNING(duration) → UNLOADING(1-2 ticks) → IDLE.

**RB-04.** Decisiones de patrons:
- Si la cola del objetivo está llena, buscar otro ride o salida.
- Tras UNBOARD, con prob. p_ride elige otro ride; con 1 - p_ride va a la salida.

**RB-05.** Movimiento: un paso por tick; prohibido entrar en bounding boxes de rides/obstáculos o salir del mapa.

**RB-06.** Semilla: todas las decisiones que involucren aleatoriedad dependen de --seed.

## 9. Métricas (KPIs)

- **Utilización por ride** = ticks en RUNNING / ticks simulados.
- **Throughput por ride** = pasajeros atendidos / ticks.
- **Tiempo medio de espera** = promedio(tick_board − tick_queue_enter).
- **Cola media total** = promedio de largo de colas en el tiempo.
- **Total salidos** = nº de patrons que alcanzan salida.

## 10. Interfaz de Usuario (CLI) y Comandos

### Ayuda
```bash
python adventureworld.py --help
```

### Modo interactivo
```bash
python adventureworld.py -i
```

### CSV + estadísticas + semilla
```bash
python adventureworld.py --rides-csv data/rides.csv --patrons-csv data/patrons.csv --steps 300 --stats --seed 42
```

### Guardar corrida
```bash
python adventureworld.py --rides-csv data/rides.csv --patrons-csv data/patrons.csv --steps 300 --seed 123 --stats --save-run
```

## 11. Requisitos de Visualización

### Vista 2D del parque:
- 🟢 spawn, 🔵 exit, 🟤 rides (🟧 si RUNNING), 🔴 obstáculos.
- Puntos (scatter) para patrons: color por estado (ROAMING, QUEUE, RIDING, EXITED).
- (Postgrad) Panel de estadísticas en vivo (subplot a la derecha) con 3 líneas: en cola, en ride, salidos.
- Actualización sin "parpadeo" (reutilizar artistas; evitar plt.clf()).

## 12. Criterios de Aceptación (por HU)

- **HU-01/02/11**: ride muestra estados y respeta capacity/duration; color cambia en mapa; se ve embarque/descarga.
- **HU-03/08**: rides no se solapan; queue_limit respeta rechazos.
- **HU-04/05/06/07/10**: patrons cambian de estado correctamente, no atraviesan obstáculos/rides, aparecen en spawn y salen por exit.
- **HU-11/12/14**: -i funciona; CLI acepta argumentos; --seed hace reproducible el escenario.
- **HU-13**: cada tick actualiza y renderiza; no hay "saltos" de lógica.
- **HU-15/16 (postgrad)**: estadísticas en vivo + resumen final y exportación si --save-run.

## 13. Pruebas (alto nivel)

- **T-01 (Ride States)**: transitions IDLE→LOADING→RUNNING→UNLOADING→IDLE occur at the expected ticks.
- **T-02 (Queue Capacity)**: cuando la cola está llena, nuevos patrons no se encolan.
- **T-03 (Boarding)**: embarca como máximo capacity.
- **T-04 (Patron States)**: cambios ROAMING→QUEUE→RIDING→EXITED.
- **T-05 (Boundaries/Obstacles)**: nadie sale del mapa ni atraviesa obstáculos.
- **T-06 (Seed)**: misma corrida con mismo --seed produce mismos eventos clave.
- **T-07 (Stats/Export)**: con --stats se actualizan líneas; --save-run crea archivos válidos.

## 14. Trazabilidad HU ↔ RF ↔ Pruebas (extracto)

| HU | RF relacionados | Pruebas |
|---|---|---|
| HU-01, HU-02 | RF-10, RF-11 | T-01, T-03 |
| HU-03 | RF-08 | T-02 |
| HU-04, HU-05 | RF-12, RF-13 | T-04, T-05 |
| HU-07, HU-08 | RF-09, RF-14 | T-02, T-04 |
| HU-11, HU-12 | RF-01, RF-02, RF-03 | (CLI smoke) |
| HU-13 | RF-16 | (tick determinism) |
| HU-14 | RF-17 | T-06 |
| HU-15, HU-16 | RF-19, RF-20 | T-07 |

## 15. Riesgos y Mitigaciones

- **Rendimiento de render**: usar set_offsets/reusar artistas.
- **No determinismo por orden de actualización**: fijar orden (p.ej., rides luego patrons) y documentarlo.
- **CSV inválidos**: validación temprana con mensajes explícitos.

## 16. Extras Sugeridos (opcionales, bonus)

- **HU-17**: Abandono por impaciencia. Campo patience en patrons; evento QUEUE_ABANDON.
- **HU-18**: Fallos de ride con prob. por tick; estado MAINTENANCE; la cola se congela.
- **HU-19**: Nueva atracción (RollerCoaster) con capacity y duration distintos para mostrar polimorfismo.

## 17. Definition of Done (DoD)

- CLI y -i operativos, --help completo.
- Dos escenarios de ejemplo (por CSV) corriendo sin errores.
- (Postgrad) --stats y --save-run generan salidas verificables.
- README con: cómo ejecutar, ejemplos de comandos, captura de mapa (y stats), y un runs/ de ejemplo.

---

**Documento creado:** 3 de octubre de 2025  
**Proyecto:** AdventureWorld - Simulador de Parque de Atracciones  
**Versión:** 1.0
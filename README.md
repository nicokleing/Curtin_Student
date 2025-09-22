# Curtin_Student

## PT3 Showground Tasks

### Informacion del estudiante
- Student Name: Nicolas Klein
- Student ID: 21892288

## Descripcion general
Coleccion de ejercicios de programacion grafica que recrean barcos pirata dentro de marcos usando Matplotlib. Cada tarea agrega funcionalidades nuevas, desde un dibujo estatico hasta una pequena simulacion animada con rebotes.

## Requisitos previos
- Python 3.10 o superior
- Paquetes: `matplotlib`, `numpy`

## Estructura del repositorio
- `Task1/` dibujo inicial con un solo pirata y marco rectangular.
- `Task2/` incorpora el modelo de barco con numpy y colores basicos.
- `Task3/` agrega configuracion por instancia para colores, tamanos y margenes.
- `Task4/` anima varias naves con velocidades y rebotes.
- `showDemo.py` ejemplo rapido que reutiliza el modulo de la tarea en uso.
- `COMP1005_Showground_Documentation.pdf` enunciado original de la practica.

## Instrucciones de ejecucion
Ejecuta cada tarea de forma independiente desde la raiz del proyecto:

```bash
python Task1/task1.py
python Task2/task2.py
python Task3/task3.py
python Task4/task4.py
```

Cada script genera una ventana con la figura y guarda una captura en su carpeta (`taskX.png`). En la tarea 4 se activa el modo interactivo (`plt.ion`) para mostrar la animacion en tiempo real antes de exportar la ultima escena.

## Detalle por tarea

### Task 1 - Pirata con caja basica
- Script principal: `Task1/task1.py`
- Modulo de soporte: `Task1/showground.py` define la clase `Pirate` con un rectangulo fijo y `step_change` que desplaza 10 unidades en X.
- Salida grafica: `Task1/task1.png`
- Nota: el titulo actual usa caracteres fuera de ASCII (`Showground ?"`); puedes reemplazarlos por comillas normales si necesitas un titulo limpio.

### Task 2 - Barco dentro del marco
- Script principal: `Task2/task2.py`
- Modulo de soporte: `Task2/showground.py` introduce `Frame`, `Ship` y una version ampliada de `Pirate` que dibuja el navio dentro del marco con coordenadas normalizadas.
- Salida grafica: `Task2/task2.png`
- Claves del codigo: la clase `Ship` escala los puntos definidos con numpy para que encajen dentro del rectangulo segun el margen indicado.

### Task 3 - Flota multicolor
- Script principal: `Task3/task3.py`
- Modulo de soporte: `Task3/showground.py` admite colores personalizados por instancia y espesores de linea.
- Salida grafica: `Task3/task3.png`
- Claves del codigo: se crean tres `Pirate` con distintos `frame_color`, `accent_color`, `height` y `margin`, mostrando la reutilizacion del modelo.

### Task 4 - Simulacion animada
- Script principal: `Task4/task4.py`
- Modulo de soporte: `Task4/showground.py` anade velocidades (`vx`, `vy`) y rebotes contra los limites 0..200.
- Salida grafica: `Task4/task4.png`
- Claves del codigo: dentro del bucle de simulacion se limpian los ejes, se llama a `plot_me`, luego `step_change` actualiza posicion y sentido al chocar con los bordes.

## Otras notas
- Las imagenes de salida (`TaskX/taskX.png`) se pueden insertar en informes o presentaciones como evidencia visual de cada ejercicio.
- Cada carpeta mantiene su propia version de `showground.py`; si haces mejoras compartidas considera extraer la logica comun a un modulo reutilizable.

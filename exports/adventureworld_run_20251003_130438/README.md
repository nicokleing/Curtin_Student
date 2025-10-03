# AdventureWorld - Exportación de Simulación
            
## Información de Ejecución
- **Nombre de ejecución**: adventureworld_run_20251003_130438
- **Fecha de exportación**: 2025-10-03 13:04:43
- **Archivos generados**: 4

## Archivos Incluidos

### events.csv
Registro cronológico de todos los eventos de la simulación:
- Movimientos de visitantes
- Cambios de estado de atracciones  
- Entrada y salida de visitantes

### summary.json
Resumen completo de la simulación incluyendo:
- Configuración utilizada
- Estadísticas finales
- Análisis de eventos
- Timeline de datos (si se usó --stats)

### plot.png
Visualización gráfica de la simulación:
- Estado final del mapa con visitantes y atracciones
- Gráficos de estadísticas en tiempo real (si se usó --stats)

## Uso de los Datos

Los archivos CSV y JSON pueden ser importados en herramientas de análisis como:
- Excel / LibreOffice Calc
- Python pandas
- R
- Tableau
- Power BI

## Reproducibilidad

Para reproducir esta simulación, usar los mismos parámetros de configuración 
incluidos en summary.json, especialmente el valor de semilla (seed) si se utilizó.

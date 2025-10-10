# AdventureWorld – Checklist de Rúbrica (Postgrado)

Esta lista cubre los criterios principales indicados en la rúbrica COMP5005 (Sem 2 2025 v1.0). Usa las casillas para registrar el estado actual del proyecto.

## Estado

- `❌` Pendiente  
- `⚠️` En progreso / requiere verificación  
- `✅` Completado / evidencias listas  

## 1. Código + Demostración (60 %)

| Criterio | Estado | Evidencia / notas |
| --- | --- | --- |
| **Usabilidad / Flexibilidad / Robustez** – Argumentos CLI, modos interactivo y batch, manejo de archivos faltantes | ⚠️ | CLI completa; falta repasar manejo de errores/archivos inexistentes |
| **Rides (≥3 tipos)** – Animaciones/estados múltiples, variación de movimiento | ✅ | Pirate, Ferris, RollerCoaster con animaciones |
| **Patrons** – Estrategias de movimiento/comportamiento complejas | ✅ | Tipos con preferencias, DecisionBehavior avanzado |
| **Colas / Gestión de riders** – Diferentes fases (espera, abordo, descarga) | ✅ | QueueBehavior + estados RideState |
| **Terreno** – Obstáculos, lectura desde archivos, validación de solapamientos | ✅ | `Terrain.from_csv` + `auto_place` + colisión |
| **Simulación** – `step_change` orquesta spawns, movimiento, colas, stats | ✅ | `SimulationEngine.step` integra todos los objetos |
| **Estadísticas (postgrado)** – Subplots en tiempo real + resumen final | ✅ | `StatsRenderer`, métricas exportadas |
| **Estilo de código (PEP8, comentarios, sin globals)** | ⚠️ | Revisar linting/imprimir logs antes entrega |
| **Bonos / extensiones** (visualización extra, estrategias configurables, etc.) | ⚠️ | Identificar highlights (p. ej. autoplace, exports) |

## 2. Documentación (40 %)

| Documento | Estado | Notas |
| --- | --- | --- |
| **README** – Dependencias, instrucciones de ejecución, archivos de entrada | ⚠️ | Existe; ampliar con escenarios y dependencias opcionales |
| **Informe – Overview** | ❌ | |
| **Informe – Guía de uso (User Guide)** | ❌ | |
| **Informe – Traceability Matrix** (feature ↔ código ↔ tests ↔ resultado) | ❌ | |
| **Informe – Discusión + UML** | ❌ | |
| **Informe – Showcase** (introducción + 3 escenarios documentados) | ❌ | |
| **Informe – Conclusión / Reflexión** | ❌ | |
| **Informe – Trabajo futuro** | ❌ | |
| **Informe – Referencias** | ❌ | |
| **Entrega Turnitin** (PDF/docx del informe) | ❌ | |

## 3. Pruebas y Evidencias

- `⚠️` Scripts o comandos reproducibles para escenarios clave (batch y GUI).  
- `⚠️` Capturas o gráficos para estadísticas comparativas.  
- `⚠️` Resultados resumidos en `exports/` o equivalente.  

## 4. Acciones Pendientes

- [ ] Revisar fechas de demostración y preparar guion.  
- [ ] Asegurar empaquetado `FOP_Assignment_<id>.zip` con todos los archivos.  
- [ ] Confirmar ausencia de dependencias externas no permitidas.  
- [ ] Autoevaluar cada criterio y actualizar estados antes de la entrega.  

> Actualiza este checklist conforme avances; servirá como evidencia durante la demostración y para completar la Traceability Matrix.

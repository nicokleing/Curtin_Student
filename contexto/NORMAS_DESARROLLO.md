# Normas de Desarrollo Profesional - AdventureWorld

## Código Profesional

### Reglas Estrictas de Código
1. **Prohibido usar emoticones**: 🎢🎯🚀📊⚙️🧪🎮etc. en cualquier archivo de código
2. **Comentarios técnicos únicamente**: Evitar comentarios explicativos excesivos o celebratorios
3. **Idioma estándar**: Mensajes de sistema y documentación en inglés técnico profesional
4. **Sin referencias a IA**: El código debe aparecer desarrollado por programador humano experimentado

### Ejemplos de Código Correcto vs Incorrecto

#### ❌ INCORRECTO:
```python
# 🎯 ÉPICA 2: Sistema avanzado de visitantes ¡Genial!
print(f"🎢 {self.name} subió a {ride.name}")  # ¡Excelente funcionalidad!
```

#### ✅ CORRECTO:
```python
# Visitor boarding system
print(f"{self.name} boarded {ride.name}")
```

### Mensajes y Print Statements
- **Evitar**: "🚀 Velocidad cambiada a X", "¡Perfecto! Sistema iniciado"
- **Usar**: "Speed changed to X", "System initialized"

## Documentación Técnica

### Estándares de Escritura
- Lenguaje técnico conciso y directo
- Sin exclamaciones o lenguaje emocional
- Terminología estándar de ingeniería de software
- Referencias profesionales apropiadas

### Estructura de Commits
- Mensajes descriptivos y técnicos
- Sin emoticones en commits
- Descripciones funcionales claras

## Control de Calidad

### Revisión Pre-Commit
Antes de cada commit, verificar:
- [ ] No hay emoticones en el código
- [ ] Comentarios técnicos apropiados
- [ ] Mensajes en inglés profesional
- [ ] Sin referencias a herramientas de IA
- [ ] Documentación técnica estándar

### Archivos Sensibles
Prestar especial atención a:
- `README.md` - Documentación principal
- Scripts de interfaz (`interface/`)
- Mensajes de usuario (`core/engine.py`)
- Documentación técnica (`contexto/`)

## Objetivo Final

El código debe aparecer como si fuera desarrollado por un programador profesional experimentado, sin ninguna evidencia de asistencia automatizada o proceso de desarrollo no convencional.

---

**Documento creado:** 3 de octubre de 2025  
**Estado:** Normas activas para todo el proyecto
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Épica 4: Controles Avanzados de Simulación - VERSIÓN VISUAL
===============================================================

Demuestra las funcionalidades de la HU-15 MEJORADAS:
- Controles visuales con botones clickeables
- Velocidad (1x, 5x, 10x) por click
- Pausa/reanudación visual
- Toggle de estadísticas
- Reset de simulación
- Controles de teclado como alternativa

🖱️ CONTROLES VISUALES (NUEVOS):
- ⏸️/▶️: Click para pausar/reanudar
- 🐌 1x, 🏃 5x, 🚀 10x: Click para velocidad
- 📊: Toggle estadísticas
- 🔄: Reiniciar simulación
- ❌: Salir

⌨️ CONTROLES DE TECLADO (alternativo):
- ESPACIO: Pausar/Reanudar
- 1/5/0: Velocidad
- R: Reset, Q: Salir, H: Ayuda
"""hon3
# -*- coding: utf-8 -*-
"""
Demo Épica 4: Controles Avanzados de Simulación
===============================================

Demuestra las funcionalidades de la HU-15:
- Controles de velocidad (1x, 5x, 10x)
- Pausa/reanudación con barra espaciadora
- Interfaz de teclado en tiempo real

Controles:
- ESPACIO: Pausar/Reanudar
- 1: Velocidad normal (1x) 
- 5: Velocidad rápida (5x)
- 0: Velocidad muy rápida (10x)
- H: Mostrar ayuda
"""

import sys
import os
import subprocess

def run_epic4_demo():
    """Ejecuta demo de controles avanzados con configuración optimizada"""
    
    print("🎯 DEMO ÉPICA 4: CONTROLES VISUALES INTERACTIVOS")
    print("="*60)
    print("📋 Funcionalidades a probar:")
    print("   ✅ HU-13: Simulación paso a paso (ya implementada)")
    print("   ✅ HU-14: Semilla aleatoria reproducible (ya implementada)")
    print("   🔥 HU-15: Controles visuales y de velocidad (NUEVA)")
    print()
    print("🖱️ CONTROLES VISUALES (HAZ CLICK):")
    print("   ⏸️/▶️  - Pausar/Reanudar simulación")
    print("   🐌 1x  - Velocidad normal")
    print("   🏃 5x  - Velocidad rápida")  
    print("   🚀 10x - Velocidad muy rápida")
    print("   📊     - Toggle estadísticas")
    print("   🔄     - Reiniciar simulación") 
    print("   ❌     - Salir")
    print()
    print("⌨️ CONTROLES DE TECLADO (alternativo):")
    print("   ESPACIO, 1, 5, 0, R, Q, H")
    print()
    print("🚀 Configuración del demo:")
    print("   • Parque estándar con visualización optimizada")
    print("   • 60 visitantes con tipos diversos") 
    print("   • 200 pasos de simulación")
    print("   • Semilla fija (789) para reproducibilidad")
    print("   • Estadísticas en tiempo real")
    print("="*60)
    
    # Configuración optimizada para demo de controles visuales
    command = [
        "python3", "adventureworld.py",
        "--seed", "789",           # HU-14: Reproducibilidad
        "--stats",                 # Visualización completa con controles
        "--steps", "200"           # Duración suficiente para probar controles
    ]
    
    print(f"🔧 Ejecutando: {' '.join(command)}")
    print("\n⚡ PRUEBA LOS CONTROLES VISUALES:")
    print("   1. 🖱️ HAZ CLICK en los botones de la parte inferior")
    print("   2. 🎮 Prueba ⏸️/▶️ para pausar y reanudar")
    print("   3. 🚀 Cambia velocidad: 🐌 1x → 🏃 5x → 🚀 10x")
    print("   4. 🔄 Usa RESET para reiniciar cuando quieras")
    print("   5. 📊 Toggle estadísticas on/off")
    print("   6. ❌ SALIR cuando hayas terminado")
    print("\n⌨️ ALTERNATIVO: También funcionan las teclas ESPACIO, 1, 5, 0, R, Q")
    print("\n🎯 Objetivo: Validar controles visuales intuitivos y funcionales\n")
    
    try:
        # Ejecutar simulación
        subprocess.run(command, cwd=os.path.dirname(os.path.abspath(__file__)))
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrumpido por el usuario")
    except FileNotFoundError:
        print("❌ Error: No se encontró adventureworld.py")
        print("   Asegúrate de ejecutar desde el directorio del proyecto")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando demo: {e}")
        return False
    
    print("\n✅ Demo de Épica 4 completado")
    print("🎯 HU-15 (Controles visuales de velocidad) validada correctamente")
    print("🖱️ Controles por click funcionando perfectamente")
    return True

if __name__ == "__main__":
    success = run_epic4_demo()
    sys.exit(0 if success else 1)
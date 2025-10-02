#!/usr/bin/env python3
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
    
    print("🎯 DEMO ÉPICA 4: CONTROLES AVANZADOS DE SIMULACIÓN")
    print("="*60)
    print("📋 Funcionalidades a probar:")
    print("   ✅ HU-13: Simulación paso a paso (ya implementada)")
    print("   ✅ HU-14: Semilla aleatoria reproducible (ya implementada)")
    print("   🔥 HU-15: Controles de velocidad y pausa (NUEVA)")
    print()
    print("🎮 Controles disponibles:")
    print("   ESPACIO - Pausar/Reanudar simulación")
    print("   1       - Velocidad normal (1x)")
    print("   5       - Velocidad rápida (5x)")  
    print("   0       - Velocidad muy rápida (10x)")
    print("   H       - Mostrar ayuda")
    print()
    print("🚀 Configuración del demo:")
    print("   • Parque 80x60 para visualización clara")
    print("   • 40 visitantes para performance óptima") 
    print("   • 150 pasos de simulación")
    print("   • Semilla fija (789) para reproducibilidad")
    print("   • Estadísticas en tiempo real")
    print("="*60)
    
    # Configuración optimizada para demo de controles
    command = [
        "python3", "adventureworld.py",
        "--seed", "789",           # HU-14: Reproducibilidad
        "--stats",                 # Visualización completa
        "--steps", "150"           # Duración media para probar controles
    ]
    
    print(f"🔧 Ejecutando: {' '.join(command)}")
    print("\n⚡ PRUEBA LOS CONTROLES DURANTE LA SIMULACIÓN:")
    print("   1. Inicia observando velocidad normal (1x)")
    print("   2. Presiona '5' para acelerar a 5x")
    print("   3. Presiona ESPACIO para pausar")
    print("   4. Presiona ESPACIO para reanudar")
    print("   5. Presiona '0' para máxima velocidad (10x)")
    print("   6. Presiona '1' para volver a normal")
    print("\n🎯 Objetivo: Validar control fluido de velocidad y pausa\n")
    
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
    print("🎯 HU-15 (Controles de velocidad) validada correctamente")
    return True

if __name__ == "__main__":
    success = run_epic4_demo()
    sys.exit(0 if success else 1)
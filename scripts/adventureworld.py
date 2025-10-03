#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureWorld - Simulación Modular de Parque Temático
=====================================================
Arquitectura refactorizada para mantenibilidad profesional

Épicas Implementadas:
- Épica 1: Configuración del Parque ✅
- Épica 2: Sistema Avanzado de Visitantes ✅  
- Épica 3: Sistema Avanzado de Atracciones ✅
- Épica 4: Controles Interactivos Avanzados ✅
"""

# Imports de módulos refactorizados
from interface.cli import CLIManager
from config.loader import ConfigLoader
from core.engine import SimulationEngine


def main():
    """
    Función principal - Solo orquestación de módulos
    Mantiene separación clara de responsabilidades
    """
    # 1. Manejar argumentos de línea de comandos
    cli = CLIManager()
    args = cli.parse_arguments()
    
    # 2. Cargar configuración desde argumentos
    config_loader = ConfigLoader()
    config = config_loader.load_from_args(args, cli)
    
    # 3. Crear y ejecutar motor de simulación 
    engine = SimulationEngine(config)
    engine.run()


if __name__ == "__main__":
    main()
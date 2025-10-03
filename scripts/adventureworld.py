#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureWorld - Simulador de Parque Temático
=============================================
Arquitectura modular para mantenibilidad

Características Implementadas:
- Epic 1: Sistema de Configuración del Parque
- Epic 2: Sistema de Visitantes  
- Epic 3: Sistema de Atracciones
- Epic 4: Controles Interactivos
"""

# Imports de módulos refactorizados
from interface.cli import CLIManager
from config.loader import ConfigLoader
from core.engine import SimulationEngine


def main():
    """
    Función principal - Orquestación de módulos
    Separación de responsabilidades
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
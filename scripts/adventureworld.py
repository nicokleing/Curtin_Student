#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureWorld - Theme Park Simulator
=====================================
Modular architecture for maintainability.

Implemented Features:
- Epic 1: Park configuration system
- Epic 2: Visitor system
- Epic 3: Ride system
- Epic 4: Interactive controls
"""

# Imports from the refactored modules
from interface.cli import CLIManager
from config.loader import ConfigLoader
from core.engine import SimulationEngine


def main():
    """
    Main function - module orchestration with clear separation of concerns.
    """
    # 1. Handle command-line arguments
    cli = CLIManager()
    args = cli.parse_arguments()
    
    # 2. Load configuration from arguments
    config_loader = ConfigLoader()
    config = config_loader.load_from_args(args, cli)
    
    # 3. Create and run the simulation engine
    engine = SimulationEngine(config)
    engine.run()


if __name__ == "__main__":
    main()

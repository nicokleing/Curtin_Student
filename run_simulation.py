#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureWorld Launcher
======================
Script principal para ejecutar la simulación desde la raíz del proyecto
"""

import sys
import os

# Agregar el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar el script principal
from scripts.adventureworld import main

if __name__ == "__main__":
    main()
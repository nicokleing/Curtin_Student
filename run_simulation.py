#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small wrapper to run the simulator from the project root."""

import sys
import os

# Ensure the project root is available for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main script
from scripts.adventureworld import main

if __name__ == "__main__":
    main()
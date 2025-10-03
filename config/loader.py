#!/usr/bin/env python3
"""
Configuration Loader Module
==========================
Handles loading configuration from YA        patron_types = [PatronType.AVENTURERO, PatronType.FAMILIAR, 
                        PatronType.IMPACIENTE, PatronType.EXPLORADOR]/CSV files and argument processing
"""
import random
import yaml
from types import SimpleNamespace
from simulation import Terrain, read_rides_csv, read_patrons_csv, build_rides, load_config_yaml, print_final_config
from models import PatronType, Patron


class ConfigLoader:
    """Loads and manages configuration from various sources"""
    
    def __init__(self):
        pass
    
    def load_from_args(self, args, cli_manager=None):
        """Load configuration based on parsed arguments"""
        
        # Set random seed if provided
        if args.seed is not None:
            random.seed(args.seed)
            
        # Interactive mode
        if args.interactive:
            if cli_manager:
                terrain, rides, num_patrons = cli_manager.interactive_setup()
            else:
                raise ValueError("CLI manager required for interactive mode")
        
        # YAML configuration mode
        elif args.config:
            terrain, rides, num_patrons = self._load_from_yaml(args.config)
            self.config_source = "yaml"
        
        # CSV configuration mode  
        elif args.map_csv or args.rides_csv or args.patrons_csv:
            terrain, rides, num_patrons = self._load_from_csv(args)
            self.config_source = "csv"
        
        # Default configuration
        else:
            terrain, rides, num_patrons = self._load_default_config()
            self.config_source = "default"
        
        # Create configuration object
        config = SimpleNamespace()
        config.terrain = terrain
        # If rides is already a list of Ride objects, use it; otherwise build from data
        if rides and hasattr(rides[0], 'name'):  # Check if it's already Ride objects
            config.rides = rides
        else:
            config.rides = build_rides(rides, terrain)  # Convert ride data to ride objects
        config.num_patrons = num_patrons
        config.steps = args.steps
        config.show_stats = args.stats
        config.seed = args.seed
        config.save_run = getattr(args, 'save_run', False)
        
        # Create patrons with Epic 2 diversity
        config.patrons = self._create_patrons(config.terrain, num_patrons)
        
        # Print final configuration
        print_final_config(config.terrain, config.rides, len(config.patrons), 
                           config.steps, config.seed, config.show_stats, self.config_source)
        
        return config
    
    def _load_from_yaml(self, file_path):
        """Load configuration from YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            # Convert the loaded data to proper objects
            terrain = Terrain.from_size(
                width=data['terrain']['width'],
                height=data['terrain']['height']
            )
            
            rides = [
                {
                    "type": ride_data['tipo'],
                    "capacity": ride_data.get('capacity', 20),
                    "duration": ride_data.get('duration', 120),
                    "bbox": (ride_data['position'][0], ride_data['position'][1], 4, 3)
                } for ride_data in data.get('rides', [])
            ]
            
            num_patrons = data.get('num_patrons', 60)
            

            
            return terrain, rides, num_patrons
        
        except FileNotFoundError:
            print(f" Archivo YAML no encontrado: {file_path}")
            return None
        except yaml.YAMLError as e:
            print(f" Error en formato YAML: {e}")
            return None
        except KeyError as e:
            print(f" Campo requerido no encontrado en YAML: {e}")
            return None
    
    def _load_from_csv(self, args):
        """Load configuration from CSV files"""
        
        # Load terrain
        if args.map_csv:
            terrain = Terrain(args.map_csv)
        else:
            terrain = Terrain('data/map1.csv')  # Default
            
        # Load rides
        if args.rides_csv:
            rides_data = read_rides_csv(args.rides_csv)
        else:
            rides_data = read_rides_csv('data/rides.csv')  # Default
            
        rides = build_rides(rides_data, terrain)
        
        # Load patrons count
        if args.patrons_csv:
            num_patrons = read_patrons_csv(args.patrons_csv)
        else:
            num_patrons = 60  # Default
            
        return terrain, rides, num_patrons
    
    def _load_default_config(self):
        """Load default configuration"""
        terrain = Terrain.from_csv('data/map1.csv')
        rides_data = read_rides_csv('data/rides.csv') 
        rides = build_rides(rides_data, terrain)
        num_patrons = 60
        
        return terrain, rides, num_patrons
    
    def _create_patrons(self, terrain, num_patrons):
        """Create patrons with Epic 2 type diversity"""
        spawns = terrain.spawn_points
        exits = terrain.exit_points
        
        patrons = []
        for i in range(num_patrons):
            # Epic 2: Distribute patron types
            patron_type = self._assign_patron_type(i, num_patrons)
            patron = Patron(name=f"P{i:03d}", spawns=spawns, exits=exits, 
                          terrain=terrain, patron_type=patron_type)
            patrons.append(patron)
            
        return patrons
    
    def _assign_patron_type(self, i, total):
        """Assign patron type based on Epic 2 distribution"""
        # Epic 2 distribution: 25% each type
        type_index = i % 4
        patron_types = [PatronType.AVENTURERO, PatronType.FAMILIAR, 
                       PatronType.IMPACIENTE, PatronType.EXPLORADOR]
        return patron_types[type_index]
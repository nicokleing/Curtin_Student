#!/usr/bin/env python3
"""
Módulo de Exportación - Generación de Datos y Reportes
======================================================
Exportación de resultados de simulación a varios formatos
"""
import os
import json
import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path


class ExportManager:
    """Gestiona exportación de datos de simulación a múltiples formatos."""
    
    def __init__(self, run_name=None):
        """Initialize export manager with optional run name."""
        if run_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"adventureworld_run_{timestamp}"
        
        self.run_name = run_name
        self.output_dir = Path(f"exports/{run_name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data collection
        self.events_log = []
        self.final_stats = {}
        self.config_data = {}
        
    def log_event(self, step, event_type, entity_id, details=None):
        """Log a simulation event for later export."""
        event = {
            'step': step,
            'timestamp': datetime.datetime.now().isoformat(),
            'event_type': event_type,
            'entity_id': entity_id,
            'details': details or {}
        }
        self.events_log.append(event)
        
    def set_config(self, config_data):
        """Store configuration data for export."""
        self.config_data = config_data
        
    def set_final_stats(self, stats_data, timeline_data=None):
        """Store final statistics for export."""
        self.final_stats = stats_data
        if timeline_data:
            self.final_stats['timeline'] = timeline_data
            
    def export_all(self, display_manager=None, metrics_calculator=None):
        """Export all data formats: CSV, JSON, and PNG."""
        files_created = []
        
        try:
            # Export events to CSV
            csv_file = self._export_events_csv()
            if csv_file:
                files_created.append(csv_file)
                
            # Epic 6: Export detailed visitor events CSV if metrics available
            if metrics_calculator:
                detailed_csv_file = self._export_detailed_visitor_events_csv(metrics_calculator)
                if detailed_csv_file:
                    files_created.append(detailed_csv_file)
                
            # Export summary to JSON
            json_file = self._export_summary_json()
            if json_file:
                files_created.append(json_file)
                
            # Export plot to PNG
            png_file = self._export_plot_png(display_manager)
            if png_file:
                files_created.append(png_file)
                
            # Create README file
            readme_file = self._create_readme(files_created)
            if readme_file:
                files_created.append(readme_file)
                
            return files_created
            
        except Exception as e:
            print(f"Error durante la exportación: {e}")
            return files_created
            
    def _export_events_csv(self):
        """Export events log to CSV file."""
        try:
            csv_path = self.output_dir / "events.csv"
            
            if not self.events_log:
                # Create minimal CSV with headers if no events
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['step', 'timestamp', 'event_type', 'entity_id', 'details'])
                    writer.writerow([0, datetime.datetime.now().isoformat(), 'simulation_start', 'system', '{}'])
                return str(csv_path)
                
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['step', 'timestamp', 'event_type', 'entity_id', 'details']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for event in self.events_log:
                    # Convert details dict to string for CSV
                    event_copy = event.copy()
                    event_copy['details'] = json.dumps(event_copy['details'])
                    writer.writerow(event_copy)
                    
            return str(csv_path)
            
        except Exception as e:
            print(f"Error exportando CSV: {e}")
            return None
            
    def _export_detailed_visitor_events_csv(self, metrics_calculator):
        """Export detailed visitor events CSV for Epic 6 HU-20."""
        try:
            csv_path = self.output_dir / "detailed_visitor_events.csv"
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'visitor_id', 'visitor_type', 'step', 'timestamp', 
                    'event_type', 'ride_name', 'queue_position', 
                    'wait_time', 'details'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Export all visitor events from metrics calculator
                for visitor_id, visitor_data in metrics_calculator.visitor_metrics.items():
                    for event in visitor_data['events']:
                        details = event.get('details', {})
                        row = {
                            'visitor_id': visitor_id,
                            'visitor_type': visitor_data['type'],
                            'step': event['step'],
                            'timestamp': event['timestamp'].isoformat(),
                            'event_type': event['event_type'],
                            'ride_name': details.get('ride_name', ''),
                            'queue_position': details.get('queue_position', ''),
                            'wait_time': '',  # Will be calculated below
                            'details': json.dumps(details)
                        }
                        
                        # Calculate wait time for boarding events
                        if event['event_type'] == 'boarded_ride':
                            ride_name = details.get('ride_name', '')
                            if ride_name and ride_name in visitor_data['queue_times']:
                                wait_times = visitor_data['queue_times'][ride_name]
                                if wait_times:
                                    row['wait_time'] = wait_times[-1]  # Most recent wait time
                        
                        writer.writerow(row)
                        
            return str(csv_path)
            
        except Exception as e:
            print(f"Error exportando CSV detallado de visitantes: {e}")
            return None
            
    def _export_summary_json(self):
        """Export summary data to JSON file."""
        try:
            json_path = self.output_dir / "summary.json"
            
            # Prepare comprehensive summary
            summary = {
                'run_info': {
                    'name': self.run_name,
                    'export_time': datetime.datetime.now().isoformat(),
                    'total_events': len(self.events_log)
                },
                'configuration': self.config_data,
                'final_statistics': self.final_stats,
                'events_summary': self._analyze_events()
            }
            
            with open(json_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(summary, jsonfile, indent=2, ensure_ascii=False, default=str)
                
            return str(json_path)
            
        except Exception as e:
            print(f"Error exportando JSON: {e}")
            return None
            
    def _export_plot_png(self, display_manager=None):
        """Export current simulation plot to PNG file."""
        try:
            png_path = self.output_dir / "plot.png"
            
            if display_manager and hasattr(display_manager, 'fig'):
                # Save current plot
                display_manager.fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                                          facecolor='white', edgecolor='none')
            else:
                # Create a summary plot from timeline data
                self._create_summary_plot(png_path)
                
            return str(png_path)
            
        except Exception as e:
            print(f"Error exportando PNG: {e}")
            return None
            
    def _create_summary_plot(self, png_path):
        """Create a summary plot with timeline data."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f'AdventureWorld - Resumen de Simulación\n{self.run_name}', fontsize=14)
        
        # Extract timeline data if available
        timeline = self.final_stats.get('timeline', {})
        
        if timeline and 'steps' in timeline:
            steps = timeline['steps']
            
            # Plot 1: Visitantes activos
            ax1.plot(steps, timeline.get('riders_timeline', []), 'r-', linewidth=2, label='En Atracciones')
            ax1.plot(steps, timeline.get('queued_timeline', []), 'orange', linewidth=2, label='En Cola')
            
            active = [r + q for r, q in zip(timeline.get('riders_timeline', []), 
                                          timeline.get('queued_timeline', []))]
            ax1.plot(steps, active, 'b-', linewidth=2, label='Total Activos')
            
            ax1.set_ylabel('Visitantes Activos')
            ax1.set_title('Visitantes en el Parque')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Visitantes que salieron
            ax2.plot(steps, timeline.get('departed_timeline', []), 'g-', linewidth=2, label='Salieron')
            
            if max(timeline.get('abandoned_timeline', [0])) > 0:
                ax2.plot(steps, timeline.get('abandoned_timeline', []), 'm--', linewidth=2, label='Abandonos')
                
            ax2.set_xlabel('Paso de Simulación')
            ax2.set_ylabel('Visitantes Salidos')
            ax2.set_title('Flujo de Salida')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
        else:
            # Create basic info plot if no timeline
            ax1.text(0.5, 0.5, 'Simulación Completada\nVer summary.json para detalles', 
                    ha='center', va='center', fontsize=16, transform=ax1.transAxes)
            ax1.axis('off')
            ax2.axis('off')
            
        plt.tight_layout()
        plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
    def _analyze_events(self):
        """Analyze events log for summary statistics."""
        if not self.events_log:
            return {'total_events': 0, 'event_types': {}}
            
        event_types = {}
        for event in self.events_log:
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
        return {
            'total_events': len(self.events_log),
            'event_types': event_types,
            'first_event': self.events_log[0]['timestamp'] if self.events_log else None,
            'last_event': self.events_log[-1]['timestamp'] if self.events_log else None
        }
        
    def _create_readme(self, files_created):
        """Create README file explaining the export contents."""
        try:
            readme_path = self.output_dir / "README.md"
            
            content = f"""# AdventureWorld - Exportación de Simulación
            
## Información de Ejecución
- **Nombre de ejecución**: {self.run_name}
- **Fecha de exportación**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Archivos generados**: {len(files_created)}

## Archivos Incluidos

### events.csv
Registro cronológico de todos los eventos de la simulación:
- Movimientos de visitantes
- Cambios de estado de atracciones  
- Entrada y salida de visitantes

### summary.json
Resumen completo de la simulación incluyendo:
- Configuración utilizada
- Estadísticas finales
- Análisis de eventos
- Timeline de datos (si se usó --stats)

### plot.png
Visualización gráfica de la simulación:
- Estado final del mapa con visitantes y atracciones
- Gráficos de estadísticas en tiempo real (si se usó --stats)

## Uso de los Datos

Los archivos CSV y JSON pueden ser importados en herramientas de análisis como:
- Excel / LibreOffice Calc
- Python pandas
- R
- Tableau
- Power BI

## Reproducibilidad

Para reproducir esta simulación, usar los mismos parámetros de configuración 
incluidos en summary.json, especialmente el valor de semilla (seed) si se utilizó.
"""

            with open(readme_path, 'w', encoding='utf-8') as readme_file:
                readme_file.write(content)
                
            return str(readme_path)
            
        except Exception as e:
            print(f"Error creando README: {e}")
            return None
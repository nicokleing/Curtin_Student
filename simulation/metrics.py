#!/usr/bin/env python3
"""
Módulo de Métricas y Análisis
============================
Cálculo de métricas de eficiencia del parque y KPIs
Registro detallado de eventos para auditoría completa
"""
import time
from datetime import datetime
from collections import defaultdict, deque
import statistics


class MetricsCalculator:
    """Cálculo de métricas de eficiencia del parque y KPIs."""
    
    def __init__(self):
        self.visitor_metrics = {}  # Per-visitor detailed tracking
        self.ride_metrics = defaultdict(lambda: {
            'boarding_events': [],
            'completion_events': [],
            'total_riders': 0,
            'total_cycles': 0,
            'downtime': 0,
            'queue_lengths': []
        })
        
        # Overall park metrics
        self.park_metrics = {
            'simulation_start_time': None,
            'total_visitors': 0,
            'total_boarding_events': 0,
            'total_abandonment_events': 0,
            'peak_concurrent_visitors': 0,
            'hourly_throughput': []
        }
        
    def initialize_visitor(self, visitor_id, visitor_type, spawn_time):
        """Initialize tracking for a new visitor."""
        self.visitor_metrics[visitor_id] = {
            'id': visitor_id,
            'type': visitor_type,
            'spawn_time': spawn_time,
            'events': [],
            'queue_times': defaultdict(list),  # Per ride
            'ride_completions': [],
            'abandonment_count': 0,
            'total_wait_time': 0,
            'satisfaction_score': 0,
            'departure_time': None,
            'current_state': 'spawning',
            'current_queue_start': None,
            'current_ride': None
        }
        
        if self.park_metrics['simulation_start_time'] is None:
            self.park_metrics['simulation_start_time'] = spawn_time
            
        self.park_metrics['total_visitors'] += 1
        
    def log_visitor_event(self, visitor_id, event_type, step, details=None):
        """Log a detailed visitor event for metrics calculation."""
        if visitor_id not in self.visitor_metrics:
            # Auto-initialize if not done
            self.initialize_visitor(visitor_id, 'unknown', step)
            
        visitor = self.visitor_metrics[visitor_id]
        
        event = {
            'step': step,
            'timestamp': datetime.now(),
            'event_type': event_type,
            'details': details or {}
        }
        
        visitor['events'].append(event)
        visitor['current_state'] = event_type
        
        # Process specific event types for metrics
        if event_type == 'joined_queue':
            ride_name = details.get('ride_name')
            visitor['current_queue_start'] = step
            visitor['current_ride'] = ride_name
            
        elif event_type == 'boarded_ride':
            ride_name = details.get('ride_name')
            if visitor['current_queue_start'] is not None:
                wait_time = step - visitor['current_queue_start']
                visitor['queue_times'][ride_name].append(wait_time)
                visitor['total_wait_time'] += wait_time
                
            self.ride_metrics[ride_name]['boarding_events'].append({
                'step': step,
                'visitor_id': visitor_id,
                'wait_time': wait_time if visitor['current_queue_start'] else 0
            })
            self.ride_metrics[ride_name]['total_riders'] += 1
            self.park_metrics['total_boarding_events'] += 1
            
        elif event_type == 'completed_ride':
            ride_name = details.get('ride_name')
            visitor['ride_completions'].append({
                'ride_name': ride_name,
                'step': step,
                'duration': details.get('duration', 0)
            })
            self.ride_metrics[ride_name]['completion_events'].append({
                'step': step,
                'visitor_id': visitor_id
            })
            
        elif event_type == 'abandoned_queue':
            ride_name = details.get('ride_name')
            visitor['abandonment_count'] += 1
            if visitor['current_queue_start'] is not None:
                wait_time = step - visitor['current_queue_start']
                visitor['total_wait_time'] += wait_time
                
            self.park_metrics['total_abandonment_events'] += 1
            
        elif event_type == 'departed':
            visitor['departure_time'] = step
            
        # Reset queue tracking after relevant events
        if event_type in ['boarded_ride', 'abandoned_queue']:
            visitor['current_queue_start'] = None
            visitor['current_ride'] = None
            
    def log_ride_event(self, ride_name, event_type, step, details=None):
        """Log a ride event for throughput and efficiency metrics."""
        ride = self.ride_metrics[ride_name]
        
        if event_type == 'cycle_completed':
            ride['total_cycles'] += 1
            ride['queue_lengths'].append(details.get('queue_length', 0))
            
        elif event_type == 'went_idle':
            ride['downtime'] += details.get('idle_duration', 1)
            
    def calculate_all_metrics(self):
        """Calcula todas las métricas de eficiencia del parque."""
        metrics = {
            'visitor_analytics': self._calculate_visitor_metrics(),
            'ride_analytics': self._calculate_ride_metrics(), 
            'park_performance': self._calculate_park_metrics(),
            'efficiency_kpis': self._calculate_efficiency_kpis()
        }
        
        return metrics
        
    def _calculate_visitor_metrics(self):
        """Calculate detailed visitor behavior metrics."""
        if not self.visitor_metrics:
            return {}
            
        wait_times = []
        abandonment_rates = {}
        type_performance = defaultdict(lambda: {
            'count': 0,
            'avg_wait_time': 0,
            'avg_rides_completed': 0,
            'abandonment_rate': 0
        })
        
        for visitor_id, data in self.visitor_metrics.items():
            visitor_type = data['type']
            type_stats = type_performance[visitor_type]
            type_stats['count'] += 1
            
            # Wait time analysis
            total_wait = data['total_wait_time']
            wait_times.append(total_wait)
            type_stats['avg_wait_time'] += total_wait
            
            # Ride completion analysis
            rides_completed = len(data['ride_completions'])
            type_stats['avg_rides_completed'] += rides_completed
            
            # Abandonment analysis
            abandonment_count = data['abandonment_count']
            type_stats['abandonment_rate'] += abandonment_count
            
        # Calculate averages per type
        for visitor_type, stats in type_performance.items():
            count = stats['count']
            if count > 0:
                stats['avg_wait_time'] = stats['avg_wait_time'] / count
                stats['avg_rides_completed'] = stats['avg_rides_completed'] / count
                stats['abandonment_rate'] = stats['abandonment_rate'] / count
                
        return {
            'overall_avg_wait_time': statistics.mean(wait_times) if wait_times else 0,
            'median_wait_time': statistics.median(wait_times) if wait_times else 0,
            'max_wait_time': max(wait_times) if wait_times else 0,
            'min_wait_time': min(wait_times) if wait_times else 0,
            'by_visitor_type': dict(type_performance)
        }
        
    def _calculate_ride_metrics(self):
        """Calculate ride-specific throughput and efficiency metrics."""
        ride_analytics = {}
        
        for ride_name, data in self.ride_metrics.items():
            boarding_events = data['boarding_events']
            completion_events = data['completion_events']
            
            # Throughput calculation
            total_riders = data['total_riders']
            total_cycles = data['total_cycles']
            
            # Wait time analysis for this ride
            ride_wait_times = [event['wait_time'] for event in boarding_events]
            
            # Queue analysis
            queue_lengths = data['queue_lengths']
            
            ride_analytics[ride_name] = {
                'total_riders': total_riders,
                'total_cycles': total_cycles,
                'avg_riders_per_cycle': total_riders / max(total_cycles, 1),
                'avg_wait_time': statistics.mean(ride_wait_times) if ride_wait_times else 0,
                'max_wait_time': max(ride_wait_times) if ride_wait_times else 0,
                'avg_queue_length': statistics.mean(queue_lengths) if queue_lengths else 0,
                'max_queue_length': max(queue_lengths) if queue_lengths else 0,
                'efficiency_score': self._calculate_ride_efficiency(data)
            }
            
        return ride_analytics
        
    def _calculate_park_metrics(self):
        """Calculate overall park performance metrics."""
        total_visitors = self.park_metrics['total_visitors']
        total_boardings = self.park_metrics['total_boarding_events']
        total_abandonments = self.park_metrics['total_abandonment_events']
        
        return {
            'total_visitors': total_visitors,
            'total_successful_boardings': total_boardings,
            'total_queue_abandonments': total_abandonments,
            'overall_abandonment_rate': (total_abandonments / max(total_visitors, 1)) * 100,
            'boarding_success_rate': (total_boardings / max(total_visitors, 1)) * 100,
            'average_rides_per_visitor': total_boardings / max(total_visitors, 1)
        }
        
    def _calculate_efficiency_kpis(self):
        """Calculate key performance indicators for park efficiency."""
        visitor_metrics = self._calculate_visitor_metrics()
        ride_metrics = self._calculate_ride_metrics()
        park_metrics = self._calculate_park_metrics()
        
        # Overall efficiency score (0-100)
        abandonment_penalty = min(park_metrics['overall_abandonment_rate'], 50)  # Cap at 50%
        wait_time_penalty = min(visitor_metrics.get('overall_avg_wait_time', 0) / 10, 30)  # Cap at 30 for very long waits
        
        efficiency_score = max(0, 100 - abandonment_penalty - wait_time_penalty)
        
        return {
            'park_efficiency_score': round(efficiency_score, 2),
            'avg_throughput_per_minute': self._calculate_throughput(),
            'visitor_satisfaction_estimate': self._estimate_satisfaction(),
            'capacity_utilization': self._calculate_capacity_utilization()
        }
        
    def _calculate_ride_efficiency(self, ride_data):
        """Calculate efficiency score for a specific ride (0-100)."""
        total_riders = ride_data['total_riders']
        total_cycles = ride_data['total_cycles']
        downtime = ride_data['downtime']
        
        if total_cycles == 0:
            return 0
            
        # Factor in rider throughput and uptime
        rider_efficiency = min(100, (total_riders / total_cycles) * 10)  # Assume capacity ~10
        uptime_efficiency = max(0, 100 - downtime)
        
        return (rider_efficiency + uptime_efficiency) / 2
        
    def _calculate_throughput(self):
        """Calculate average visitor throughput per simulation minute."""
        total_boardings = self.park_metrics['total_boarding_events']
        # Assuming each step = 1 minute of simulation time
        total_steps = max([data['departure_time'] or 0 for data in self.visitor_metrics.values()] + [0])
        
        return total_boardings / max(total_steps, 1)
        
    def _estimate_satisfaction(self):
        """Estimate visitor satisfaction based on wait times and ride completions."""
        if not self.visitor_metrics:
            return 0
            
        satisfaction_scores = []
        for visitor_data in self.visitor_metrics.values():
            rides_completed = len(visitor_data['ride_completions'])
            wait_time = visitor_data['total_wait_time']
            abandonment_count = visitor_data['abandonment_count']
            
            # Simple satisfaction model
            satisfaction = 50  # Base satisfaction
            satisfaction += rides_completed * 20  # +20 per ride completed
            satisfaction -= wait_time * 0.5  # -0.5 per minute waited
            satisfaction -= abandonment_count * 15  # -15 per abandonment
            
            satisfaction_scores.append(max(0, min(100, satisfaction)))
            
        return statistics.mean(satisfaction_scores) if satisfaction_scores else 0
        
    def _calculate_capacity_utilization(self):
        """Calculate how well park capacity is being utilized."""
        total_possible_boardings = sum(
            ride_data['total_cycles'] * 15  # Assume average capacity of 15
            for ride_data in self.ride_metrics.values()
        )
        
        actual_boardings = self.park_metrics['total_boarding_events']
        
        if total_possible_boardings == 0:
            return 0
            
        return (actual_boardings / total_possible_boardings) * 100
        
    def get_detailed_visitor_report(self, visitor_id):
        """Get detailed report for a specific visitor."""
        if visitor_id not in self.visitor_metrics:
            return None
            
        visitor = self.visitor_metrics[visitor_id]
        return {
            'visitor_id': visitor_id,
            'type': visitor['type'],
            'total_events': len(visitor['events']),
            'rides_completed': len(visitor['ride_completions']),
            'queue_abandonments': visitor['abandonment_count'],
            'total_wait_time': visitor['total_wait_time'],
            'event_timeline': visitor['events']
        }
        
    def print_metrics_summary(self):
        """Imprime resumen de métricas en consola."""
        metrics = self.calculate_all_metrics()
        
        print("\n" + "="*80)
        print("🎯 ÉPICA 6: MÉTRICAS Y REPORTES COMPLETOS")
        print("="*80)
        
        # Park Performance Overview
        park_perf = metrics['park_performance']
        print(f"📊 RESUMEN DE RENDIMIENTO DEL PARQUE:")
        print(f"   👥 Visitantes totales: {park_perf['total_visitors']}")
        print(f"   🎢 Abordajes exitosos: {park_perf['total_successful_boardings']}")
        print(f"   🚶 Abandonos de cola: {park_perf['total_queue_abandonments']}")
        print(f"   📈 Tasa de éxito: {park_perf['boarding_success_rate']:.1f}%")
        print(f"   📉 Tasa de abandono: {park_perf['overall_abandonment_rate']:.1f}%")
        print(f"   🎠 Rides promedio por visitante: {park_perf['average_rides_per_visitor']:.2f}")
        
        # Visitor Analytics
        visitor_analytics = metrics['visitor_analytics']
        print(f"\n⏱️ ANÁLISIS DE TIEMPOS DE ESPERA:")
        print(f"   📊 Tiempo promedio de espera: {visitor_analytics['overall_avg_wait_time']:.1f} minutos")
        print(f"   📊 Tiempo mediano de espera: {visitor_analytics['median_wait_time']:.1f} minutos")
        print(f"   ⬆️ Tiempo máximo de espera: {visitor_analytics['max_wait_time']:.1f} minutos")
        
        print(f"\n👤 ANÁLISIS POR TIPO DE VISITANTE:")
        for vtype, stats in visitor_analytics['by_visitor_type'].items():
            print(f"   {vtype.title()}: {stats['count']} visitantes")
            print(f"      ⏰ Espera promedio: {stats['avg_wait_time']:.1f} min")
            print(f"      🎢 Rides promedio: {stats['avg_rides_completed']:.1f}")
            print(f"      🚶 Abandonos promedio: {stats['abandonment_rate']:.1f}")
        
        # Ride Analytics
        ride_analytics = metrics['ride_analytics']
        print(f"\n🎡 ANÁLISIS POR ATRACCIÓN:")
        for ride_name, stats in ride_analytics.items():
            print(f"   {ride_name}:")
            print(f"      👥 Total visitantes: {stats['total_riders']}")
            print(f"      🔄 Ciclos completados: {stats['total_cycles']}")
            print(f"      ⏰ Espera promedio: {stats['avg_wait_time']:.1f} min")
            print(f"      📊 Cola promedio: {stats['avg_queue_length']:.1f}")
            print(f"      ⭐ Puntuación eficiencia: {stats['efficiency_score']:.1f}/100")
        
        # Key Performance Indicators
        kpis = metrics['efficiency_kpis']
        print(f"\n🎯 INDICADORES CLAVE DE RENDIMIENTO (KPIs):")
        print(f"   🏆 Puntuación de eficiencia del parque: {kpis['park_efficiency_score']}/100")
        print(f"   📈 Throughput promedio: {kpis['avg_throughput_per_minute']:.2f} visitantes/min")
        print(f"   😊 Satisfacción estimada: {kpis['visitor_satisfaction_estimate']:.1f}/100")
        print(f"   🎪 Utilización de capacidad: {kpis['capacity_utilization']:.1f}%")
        
        print("="*80)
        
        return metrics
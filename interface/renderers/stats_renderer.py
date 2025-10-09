# -*- coding: utf-8 -*-
"""Render real-time statistics with dynamic charts."""

import matplotlib.pyplot as plt
import numpy as np

class StatsRenderer:
    """Render real-time statistics using line charts."""
    
    def __init__(self, ax_stats):
        self.ax_stats = ax_stats
        self.history = {
            'steps': [],
            'riders': [],
            'queued': [],
            'departed': [],
            'abandoned': []
        }
        self.max_history = 100  # Keep the most recent 100 steps
        
    def render(self, state, engine):
        """Render the current statistics with line charts."""
        if not self.ax_stats:
            return
            
        stats = state['statistics']
        current_step = state['step']
        
        # Update history
        self._update_history(current_step, stats)
        
        # Clear axes
        self.ax_stats.clear()
        
        # Draw charts if we have enough history
        if len(self.history['steps']) > 1:
            self._render_line_plots()
        else:
            self._render_text_stats(stats, current_step)
            
        self.ax_stats.set_title('Real-Time Statistics')
        
    def _update_history(self, step, stats):
        """Update the statistics history."""
        # Append new data
        self.history['steps'].append(step)
        self.history['riders'].append(stats['riders_now'])
        self.history['queued'].append(stats['queued_now'])
        self.history['departed'].append(stats['departed_total'])
        self.history['abandoned'].append(stats['abandoned_now'])
        
        # Trim to the most recent N values
        for key in self.history:
            if len(self.history[key]) > self.max_history:
                self.history[key] = self.history[key][-self.max_history:]
                
    def _render_line_plots(self):
        """Render line charts for the statistics."""
        steps = self.history['steps']
        
        # Main subplot
        ax1 = self.ax_stats
        
        # Primary line: active visitors (riding + queued)
        active_visitors = [r + q for r, q in zip(self.history['riders'], self.history['queued'])]
        line1 = ax1.plot(steps, active_visitors, 'b-', linewidth=2, label='Active (Total)')
        line2 = ax1.plot(steps, self.history['riders'], 'r-', linewidth=1.5, label='On Rides')
        line3 = ax1.plot(steps, self.history['queued'], 'orange', linewidth=1.5, label='In Queue')
        
        ax1.set_xlabel('Simulation Step')
        ax1.set_ylabel('Active Visitors', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.grid(True, alpha=0.3)
        
        # Secondary axis for visitors who departed
        ax2 = ax1.twinx()
        line4 = ax2.plot(steps, self.history['departed'], 'g-', linewidth=1.5, label='Departed')
        
        # Only show abandons when present
        if max(self.history['abandoned']) > 0:
            ax2.plot(steps, self.history['abandoned'], 'm--', linewidth=1, label='Left Queue')
            
        ax2.set_ylabel('Visitors Departed', color='green')
        ax2.tick_params(axis='y', labelcolor='green')
        
        # Combined legend
        lines = line1 + line2 + line3 + line4
        labels = [l.get_label() for l in lines]
        if max(self.history['abandoned']) > 0:
            lines += [ax2.get_lines()[-1]]  # Include abandon line
            labels.append('Left Queue')
            
        ax1.legend(lines, labels, loc='upper left', fontsize=8)
        
        # Mostrar valores actuales en texto
        current_stats = f"Current: {self.history['riders'][-1]} riders, {self.history['queued'][-1]} queued, {self.history['departed'][-1]} departed"
        if self.history['abandoned'][-1] > 0:
            current_stats += f", {self.history['abandoned'][-1]} left"
        ax1.text(0.02, 0.98, current_stats, transform=ax1.transAxes, 
                verticalalignment='top', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
    def _render_text_stats(self, stats, step):
        """Render statistics as text when history is short."""
        stats_text = [
            f"Riding: {stats['riders_now']}",
            f"Queued: {stats['queued_now']}", 
            f"Departed: {stats['departed_total']}",
            f"Abandoned: {stats['abandoned_now']}",
            f"Step: {step}",
            "",
            "Collecting data for charts..."
        ]
        
        for i, text in enumerate(stats_text):
            self.ax_stats.text(0.1, 0.9-i*0.12, text, fontsize=12, 
                             transform=self.ax_stats.transAxes,
                             verticalalignment='top')
        
        self.ax_stats.set_xlim(0, 1)
        self.ax_stats.set_ylim(0, 1)
        self.ax_stats.axis('off')
        
    def get_export_data(self):
        """Return statistics for export."""
        return {
            'steps': self.history['steps'].copy(),
            'riders_timeline': self.history['riders'].copy(),
            'queued_timeline': self.history['queued'].copy(),
            'departed_timeline': self.history['departed'].copy(),
            'abandoned_timeline': self.history['abandoned'].copy()
        }

#!/usr/bin/env python3
"""
Test visual rápido para verificar las nuevas visualizaciones de rides
"""

import sys
import os

# Agregar la ruta del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

def test_pirate_ship_visual():
    """Test visual del barco pirata"""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Simular diferentes estados
    states = [
        ('idle', 0, 'Barco Pirata - Inactivo'),
        ('loading', 0, 'Barco Pirata - Cargando'),
        ('running', 45, 'Barco Pirata - En Movimiento')
    ]
    
    for ax, (state, step_counter, title) in zip([ax1, ax2, ax3], states):
        x, y = 5, 3
        
        # Calcular ángulo de balanceo
        if state == 'running':
            angle = math.sin(step_counter * 0.3) * 20
        else:
            angle = 0
        
        # Colores según estado
        if state == 'running':
            color = '#8B4513'
            alpha = 1.0
        elif state == 'loading':
            color = '#CD853F'
            alpha = 0.9
        else:
            color = '#A0522D'
            alpha = 0.7
        
        # Dibujar el barco
        ellipse = patches.Ellipse((x, y), 3, 1.5, angle=angle, 
                                 facecolor=color, alpha=alpha, 
                                 edgecolor='black', linewidth=2)
        ax.add_patch(ellipse)
        
        # Dibujar mástil
        mast_x = x + 0.5 * math.cos(math.radians(angle)) if state == 'running' else x + 0.5
        mast_y = y
        ax.plot([mast_x, mast_x], [mast_y-0.5, mast_y+1.5], 'k-', linewidth=3)
        
        # Bandera pirata si está funcionando
        if state == 'running':
            ax.text(mast_x+0.2, mast_y+1.2, '🏴‍☠️', fontsize=12)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('test_pirate_visual.png', dpi=150, bbox_inches='tight')
    plt.show()

def test_ferris_wheel_visual():
    """Test visual de la rueda de la fortuna"""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Simular diferentes estados
    states = [
        ('idle', 0, 'Rueda de la Fortuna - Inactiva'),
        ('loading', 0, 'Rueda de la Fortuna - Cargando'),
        ('running', 36, 'Rueda de la Fortuna - Girando')
    ]
    
    for ax, (state, step_counter, title) in zip([ax1, ax2, ax3], states):
        x, y = 5, 3
        
        # Calcular rotación
        if state == 'running':
            rotation = step_counter * 10
        else:
            rotation = 0
        
        # Colores según estado
        if state == 'running':
            color = '#FF6347'
            alpha = 1.0
        elif state == 'loading':
            color = '#FFA500'
            alpha = 0.9
        else:
            color = '#FF8C00'
            alpha = 0.7
        
        # Dibujar rueda principal
        wheel = patches.Circle((x, y), 1.8, facecolor=color, alpha=alpha,
                              edgecolor='darkred', linewidth=3)
        ax.add_patch(wheel)
        
        # Dibujar radios de la rueda
        for i in range(8):
            angle = math.radians(i * 45 + rotation)
            x_end = x + 1.6 * math.cos(angle)
            y_end = y + 1.6 * math.sin(angle)
            ax.plot([x, x_end], [y, y_end], 'darkred', linewidth=2)
        
        # Dibujar cabinas de pasajeros
        for i in range(6):
            angle = math.radians(i * 60 + rotation)
            cab_x = x + 1.4 * math.cos(angle)
            cab_y = y + 1.4 * math.sin(angle)
            cabin = patches.Rectangle((cab_x-0.15, cab_y-0.1), 0.3, 0.2,
                                    facecolor='yellow', edgecolor='black', linewidth=1)
            ax.add_patch(cabin)
        
        # Símbolo si está funcionando
        if state == 'running':
            ax.text(x, y+2.5, '🎡', fontsize=16, ha='center')
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('test_ferris_visual.png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("🎨 Generando pruebas visuales de las atracciones...")
    print("🏴‍☠️ Probando Barco Pirata...")
    test_pirate_ship_visual()
    print("🎡 Probando Rueda de la Fortuna...")
    test_ferris_wheel_visual()
    print("✅ Pruebas visuales completadas!")
    print("📁 Revisa los archivos test_pirate_visual.png y test_ferris_visual.png")
# -*- coding: utf-8 -*-
"""Renderizador de botones de control visual."""

import matplotlib.patches as patches

class ButtonRenderer:
    """Maneja la creación y actualización visual de botones."""
    
    def __init__(self, ax_controls):
        self.ax_controls = ax_controls
        self.buttons = {}
        
    def create_layout(self, engine):
        """Crea el diseño completo de botones."""
        # Configurar área de controles
        self.ax_controls.set_xlim(0, 10)
        self.ax_controls.set_ylim(0, 1.6)
        self.ax_controls.axis('off')
        
        # Dimensiones de botones
        btn_width = 1.4
        btn_height = 0.45
        
        # Fila 1: Botones de control
        self._create_button('pause', 0.5, 1.0, btn_width, btn_height, 'lightgreen')
        self._create_button('reset', 2.0, 1.0, btn_width, btn_height, 'orange')  
        self._create_button('exit', 3.5, 1.0, btn_width, btn_height, 'red')
        
        # Fila 2: Botones de velocidad
        self._create_button('speed1', 0.5, 0.3, btn_width, btn_height, 'lightblue')
        self._create_button('speed5', 2.0, 0.3, btn_width, btn_height, 'orange')
        self._create_button('speed10', 3.5, 0.3, btn_width, btn_height, 'red')
        
        # Botón de estadísticas opcional
        if engine.show_stats:
            self._create_button('stats', 5.0, 0.3, btn_width, btn_height, 'lightgray')
        
        # Etiquetas de sección
        self.ax_controls.text(2.5, 1.55, 'CONTROL', ha='center', va='center', 
                            fontsize=10, weight='bold', color='darkblue')
        self.ax_controls.text(2.5, 0.05, 'VELOCIDAD', ha='center', va='center', 
                            fontsize=10, weight='bold', color='darkred')
                            
        # Instrucciones
        self.ax_controls.text(7.5, 1.3, '👆 CLICK', ha='center', va='center', 
                            fontsize=10, weight='bold', color='blue')
        self.ax_controls.text(7.5, 1.1, 'para controlar', ha='center', va='center', 
                            fontsize=8, style='italic', color='gray')
        
    def _create_button(self, name, x, y, width, height, color):
        """Crea un botón individual."""
        rect = patches.Rectangle((x, y), width, height, 
                               facecolor=color, edgecolor='black', linewidth=2)
        self.ax_controls.add_patch(rect)
        
        self.buttons[name] = {
            'rect': rect,
            'x': x, 'y': y, 'width': width, 'height': height,
            'default_color': color,
            'area': (x, x+width, y, y+height),
            'current_text': '',
            'text_pos': (x + width/2, y + height/2)
        }
        
    def update_button_texts(self, engine):
        """Actualiza todos los textos de botones según el estado actual."""
        # Limpiar textos de botones previos (preservar etiquetas de sección)
        for text in list(self.ax_controls.texts):
            if not any(keyword in text.get_text() for keyword in ['👆', 'CONTROL', 'VELOCIDAD', 'para controlar']):
                text.remove()
        
        # Textos de botones según estado actual
        texts = {
            'pause': 'PLAY' if engine.paused else 'PAUSE',
            'reset': 'RESET',
            'exit': 'EXIT',
            'speed1': '✓1x' if engine.speed_multiplier == 1 else '1x',
            'speed5': '✓5x' if engine.speed_multiplier == 5 else '5x',
            'speed10': '✓10x' if engine.speed_multiplier == 10 else '10x'
        }
        
        # Agregar botón de estadísticas si está disponible
        if 'stats' in self.buttons:
            texts['stats'] = 'STATS'
            
        # Agregar textos de botones
        for btn_name, text in texts.items():
            if btn_name in self.buttons:
                self._add_button_text(btn_name, text)
                
    def _add_button_text(self, btn_name, text):
        """Agrega texto a un botón específico."""
        btn = self.buttons[btn_name]
        x, y = btn['text_pos']
        
        # Tamaño de fuente basado en longitud del texto
        fontsize = 12 if len(text) <= 4 else (10 if len(text) <= 8 else 9)
        
        # Color de texto basado en el botón
        if btn_name == 'exit':
            text_color = 'white'
        elif btn_name == 'pause':
            text_color = 'darkgreen'
        elif btn_name == 'reset':
            text_color = 'darkorange'
        elif 'speed' in btn_name:
            text_color = 'white'
        else:
            text_color = 'black'
            
        self.ax_controls.text(x, y, text, ha='center', va='center', 
                            fontsize=fontsize, weight='bold', color=text_color)
        
        btn['current_text'] = text
        
    def get_button_area(self, button_name):
        """Obtiene el área de un botón para detección de clicks."""
        if button_name in self.buttons:
            return self.buttons[button_name]['area']
        return None
        
    def set_final_mode(self):
        """Configura botones para modo final."""
        # Cambiar botón de salida a OK
        if 'exit' in self.buttons:
            self.buttons['exit']['rect'].set_facecolor('lightgreen')
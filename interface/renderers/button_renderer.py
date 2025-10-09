# -*- coding: utf-8 -*-
"""Renderer for visual control buttons."""

import matplotlib.patches as patches

class ButtonRenderer:
    """Create and update the visual control buttons."""
    
    def __init__(self, ax_controls):
        self.ax_controls = ax_controls
        self.buttons = {}
        
    def create_layout(self, engine):
        """Create the full button layout."""
        # Configure control area
        self.ax_controls.set_xlim(0, 10)
        self.ax_controls.set_ylim(0, 1.6)
        self.ax_controls.axis('off')
        
        # Button dimensions
        btn_width = 1.4
        btn_height = 0.45
        
        # Row 1: main controls
        self._create_button('pause', 0.5, 1.0, btn_width, btn_height, 'lightgreen')
        self._create_button('reset', 2.0, 1.0, btn_width, btn_height, 'orange')  
        self._create_button('exit', 3.5, 1.0, btn_width, btn_height, 'red')
        
        # Row 2: speed controls
        self._create_button('speed1', 0.5, 0.3, btn_width, btn_height, 'lightblue')
        self._create_button('speed5', 2.0, 0.3, btn_width, btn_height, 'orange')
        self._create_button('speed10', 3.5, 0.3, btn_width, btn_height, 'red')
        
        # Optional stats button
        if engine.show_stats:
            self._create_button('stats', 5.0, 0.3, btn_width, btn_height, 'lightgray')
        
        # Section labels
        self.ax_controls.text(2.5, 1.55, 'CONTROL', ha='center', va='center', 
                            fontsize=10, weight='bold', color='darkblue')
        self.ax_controls.text(2.5, 0.05, 'SPEED', ha='center', va='center', 
                            fontsize=10, weight='bold', color='darkred')
                            
        # Instructions
        self.ax_controls.text(7.5, 1.3, 'CLICK', ha='center', va='center', 
                            fontsize=10, weight='bold', color='blue')
        self.ax_controls.text(7.5, 1.1, 'to control', ha='center', va='center', 
                            fontsize=8, style='italic', color='gray')
        
    def _create_button(self, name, x, y, width, height, color):
        """Create a single button."""
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
        """Update button labels based on current state."""
        # Clear previous dynamic button texts (preserve section labels)
        for text in list(self.ax_controls.texts):
            if not any(keyword in text.get_text() for keyword in ['CLICK', 'CONTROL', 'SPEED', 'to control']):
                text.remove()
        
        # Button text for the current state
        texts = {
            'pause': 'PLAY' if engine.paused else 'PAUSE',
            'reset': 'RESET',
            'exit': 'EXIT',
            'speed1': '1x*' if engine.speed_multiplier == 1 else '1x',
            'speed5': '5x*' if engine.speed_multiplier == 5 else '5x',
            'speed10': '10x*' if engine.speed_multiplier == 10 else '10x'
        }
        
        # Add stats button if available
        if 'stats' in self.buttons:
            texts['stats'] = 'STATS'
            
        # Apply button texts
        for btn_name, text in texts.items():
            if btn_name in self.buttons:
                self._add_button_text(btn_name, text)
                
    def _add_button_text(self, btn_name, text):
        """Add text to a specific button."""
        btn = self.buttons[btn_name]
        x, y = btn['text_pos']
        
        # Font size based on text length
        fontsize = 12 if len(text) <= 4 else (10 if len(text) <= 8 else 9)
        
        # Choose text color per button type
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
        """Return the clickable area for a button."""
        if button_name in self.buttons:
            return self.buttons[button_name]['area']
        return None
        
    def set_final_mode(self):
        """Adjust buttons for final mode."""
        # Turn exit button into OK
        if 'exit' in self.buttons:
            self.buttons['exit']['rect'].set_facecolor('lightgreen')

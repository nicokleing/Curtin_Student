#!/usr/bin/env python3
"""
Controls Manager - User Input Module
==================================
Handles all user controls: buttons, keyboard, mouse events
"""
import matplotlib.patches as patches


class ControlsManager:
    """
    Manages all user interaction controls
    Handles visual buttons, keyboard shortcuts, and mouse events
    """
    
    def __init__(self, engine, ax_controls, fig):
        """Initialize controls manager"""
        self.engine = engine
        self.ax_controls = ax_controls
        self.fig = fig
        
        # Button storage
        self.buttons = {}
        
    def setup(self):
        """Setup visual controls and event handlers"""
        self._create_button_layout()
        self._connect_events()
        self._show_controls_help()
        
    def _create_button_layout(self):
        """Create compact visual button layout"""
        # Configure controls area
        self.ax_controls.set_xlim(0, 10)
        self.ax_controls.set_ylim(0, 1.6)
        self.ax_controls.axis('off')
        
        # Button dimensions
        btn_width = 1.4
        btn_height = 0.45
        
        # Row 1: Control buttons
        self._create_button('pause', 0.5, 1.0, btn_width, btn_height, 'lightgreen')
        self._create_button('reset', 2.0, 1.0, btn_width, btn_height, 'orange')  
        self._create_button('exit', 3.5, 1.0, btn_width, btn_height, 'red')
        
        # Row 2: Speed buttons
        self._create_button('speed1', 0.5, 0.3, btn_width, btn_height, 'lightblue')
        self._create_button('speed5', 2.0, 0.3, btn_width, btn_height, 'orange')
        self._create_button('speed10', 3.5, 0.3, btn_width, btn_height, 'red')
        
        # Optional stats toggle if available
        if self.engine.show_stats:
            self._create_button('stats', 5.0, 0.3, btn_width, btn_height, 'lightgray')
        
        # Section labels
        self.ax_controls.text(2.5, 1.55, 'CONTROL', ha='center', va='center', 
                            fontsize=10, weight='bold', color='darkblue')
        self.ax_controls.text(2.5, 0.05, 'VELOCIDAD', ha='center', va='center', 
                            fontsize=10, weight='bold', color='darkred')
                            
        # Instructions
        self.ax_controls.text(7.5, 1.3, '👆 CLICK', ha='center', va='center', 
                            fontsize=10, weight='bold', color='blue')
        self.ax_controls.text(7.5, 1.1, 'para controlar', ha='center', va='center', 
                            fontsize=8, style='italic', color='gray')
        
        # Update button texts
        self._update_button_texts()
        
    def _create_button(self, name, x, y, width, height, color):
        """Create individual button"""
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
        
    def _update_button_texts(self):
        """Update all button texts based on current state"""
        # Clear previous button texts (preserve section labels)
        for text in list(self.ax_controls.texts):
            if not any(keyword in text.get_text() for keyword in ['👆', 'CONTROL', 'VELOCIDAD', 'para controlar']):
                text.remove()
        
        # Button texts based on current state
        texts = {
            'pause': '▶️ PLAY' if self.engine.paused else '⏸️ PAUSA',
            'reset': '🔄 RESET',
            'exit': '❌ SALIR',
            'speed1': '✓1x' if self.engine.speed_multiplier == 1 else '1x',
            'speed5': '✓5x' if self.engine.speed_multiplier == 5 else '5x',
            'speed10': '✓10x' if self.engine.speed_multiplier == 10 else '10x'
        }
        
        # Add stats button if available
        if 'stats' in self.buttons:
            texts['stats'] = 'STATS'
            
        # Add button texts
        for btn_name, text in texts.items():
            if btn_name in self.buttons:
                self._add_button_text(btn_name, text)
                
    def _add_button_text(self, btn_name, text):
        """Add text to specific button"""
        btn = self.buttons[btn_name]
        x, y = btn['text_pos']
        
        # Font size based on text length
        fontsize = 12 if len(text) <= 4 else (10 if len(text) <= 8 else 9)
        
        # Text color based on button
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
        
    def _connect_events(self):
        """Connect mouse and keyboard events"""
        if self.fig:
            self.fig.canvas.mpl_connect('button_press_event', self._on_click)
            self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
            
    def _on_click(self, event):
        """Handle mouse click events"""
        if event.inaxes != self.ax_controls:
            return
            
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
            
        print(f"🖱️ Click detectado en ({x:.2f}, {y:.2f})")
        
        # Check which button was clicked
        for btn_name, btn_data in self.buttons.items():
            x1, x2, y1, y2 = btn_data['area']
            if x1 <= x <= x2 and y1 <= y <= y2:
                print(f"🎮 Botón clickeado: {btn_name}")
                self._handle_button_click(btn_name)
                break
                
    def _handle_button_click(self, button_name):
        """Handle button click actions"""
        if button_name == 'pause':
            self.engine.toggle_pause()
        elif button_name == 'reset':
            self.engine.reset_simulation()
        elif button_name == 'exit':
            self.engine.exit_simulation()
        elif button_name == 'speed1':
            self.engine.set_speed(1)
        elif button_name == 'speed5':
            self.engine.set_speed(5)
        elif button_name == 'speed10':
            self.engine.set_speed(10)
        elif button_name == 'stats':
            self._toggle_stats()
            
        # Update button display
        self._update_button_texts()
        if self.fig:
            self.fig.canvas.draw_idle()
            
    def _on_key_press(self, event):
        """Handle keyboard shortcuts"""
        key_actions = {
            ' ': self.engine.toggle_pause,    # Spacebar
            '1': lambda: self.engine.set_speed(1),
            '5': lambda: self.engine.set_speed(5),
            '0': lambda: self.engine.set_speed(10),
            'r': self.engine.reset_simulation,
            'q': self.engine.exit_simulation,
            'h': self._show_controls_help
        }
        
        if event.key in key_actions:
            print(f"⌨️ Tecla presionada: {event.key}")
            key_actions[event.key]()
            self._update_button_texts()
            if self.fig:
                self.fig.canvas.draw_idle()
                
    def _toggle_stats(self):
        """Toggle statistics display (placeholder)"""
        print("📊 Toggle estadísticas (funcionalidad placeholder)")
        
    def update_display(self, state):
        """Update control display based on simulation state"""
        self._update_button_texts()
        
    def set_final_mode(self):
        """Set controls for final mode"""
        # Change exit button to OK
        if 'exit' in self.buttons:
            self.buttons['exit']['rect'].set_facecolor('lightgreen')
            
        # Update button texts
        self._update_button_texts()
        
        # Force refresh
        if self.fig:
            self.fig.canvas.draw_idle()
            
    def _show_controls_help(self):
        """Show controls help information"""
        print("\n" + "="*60)
        print("🎮 CONTROLES DE SIMULACIÓN - ÉPICA 4")
        print("="*60)
        print("🖱️  CONTROLES POR CLICK:")
        print("   ⏸️/▶️  - Pausar/Reanudar simulación")
        print("   🐌 1x  - Velocidad normal")
        print("   🏃 5x  - Velocidad rápida") 
        print("   🚀 10x - Velocidad muy rápida")
        print("   📊     - Toggle estadísticas")
        print("   🔄     - Reiniciar simulación")
        print("   ❌     - Salir")
        print()
        print("⌨️  CONTROLES POR TECLADO (alternativo):")
        print("   ESPACIO - Pausar/Reanudar")
        print("   1,5,0   - Cambiar velocidad")
        print("   R       - Reiniciar")
        print("   Q       - Salir")
        print("   H       - Mostrar esta ayuda")
        print("="*60)
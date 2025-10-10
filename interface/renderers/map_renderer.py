# -*- coding: utf-8 -*-
"""Renderer for the main simulation map."""

import math
import numpy as np
import matplotlib.patches as patches

class MapRenderer:
    """Render the main map with terrain, patrons, and rides."""
    
    def __init__(self, ax_map):
        self.ax_map = ax_map
        
    def render(self, state):
        """Render the full map."""
        terrain = state['terrain']
        patrons = state['patrons']
        rides = state['rides']
        time = state['time']
        step = state['step']
        paused = state['paused']
        speed = state['speed']
        
        # Clear and setup map bounds
        self.ax_map.clear()
        self.ax_map.set_xlim(0, terrain.width)
        self.ax_map.set_ylim(0, terrain.height)
        
        # Draw terrain background
        self._draw_terrain(terrain)
        
        # Draw simulation elements (patrons first, then rides for visibility)
        self._draw_patrons(patrons)
        self._draw_rides(rides)
        
        # Update title with current status
        status = "Paused" if paused else f"Running at {speed}x"
        self.ax_map.set_title(f'AdventureWorld - Step: {step} | {status}')
        
    def _draw_terrain(self, terrain):
        """Draw terrain background."""
        terrain_map = np.array(terrain.grid)
        self.ax_map.imshow(terrain_map, cmap='terrain', alpha=0.5, 
                          extent=[0, terrain.width, 0, terrain.height], origin='lower')
    
    def _draw_patrons(self, patrons):
        """Draw every visitor."""
        for patron in patrons:
            self._draw_patron(patron)
            
    def _draw_patron(self, patron):
        """Draw a single visitor."""
        type_colors = {
            'adventurer': 'red',
            'family': 'blue', 
            'impatient': 'orange',
            'explorer': 'green'
        }
        
        color = type_colors.get(patron.patron_type.value, 'gray')
        x, y = patron.position
        self.ax_map.scatter(x, y, c=color, s=15, alpha=0.8)
        
    def _draw_rides(self, rides):
        """Draw all rides."""
        for ride in rides:
            self._draw_ride(ride)
            
    def _draw_ride(self, ride):
        """Draw a single ride with animation."""
        x, y, bbox_w, bbox_h = self._get_bbox_geometry(ride)
        # Determine ride type
        ride_type = self._get_ride_type(ride)

        # Draw depending on type
        if ride_type == 'pirate':
            self._draw_pirate_ship(ride, x, y, bbox_w, bbox_h)
        elif ride_type == 'ferris':
            self._draw_ferris_wheel(ride, x, y, bbox_w, bbox_h)
        else:
            self._draw_generic_ride(ride, x, y, bbox_w, bbox_h)

        # Information about the ride
        info = f"{ride.name}\n{ride.state}\n{len(ride.riders)}/{ride.capacity}"
        label_offset = max(bbox_h * 0.15, 2.0)
        label_font = max(8, min(bbox_w, bbox_h) * 0.35)
        self.ax_map.text(x, y - (bbox_h / 2) - label_offset, info,
                        ha='center', va='top', fontsize=label_font,
                        weight='bold', color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))

        # Draw queue if present
        self._draw_ride_queue(ride)

    def _get_bbox_geometry(self, ride):
        """Return center and size for a ride, falling back to defaults."""
        if hasattr(ride, 'bbox') and ride.bbox:
            x, y, w, h = ride.bbox
            cx = x + w / 2.0
            cy = y + h / 2.0
            return cx, cy, max(w, 1.0), max(h, 1.0)
        # Fallback to a sensible default footprint
        cx, cy = ride.center()
        return cx, cy, 6.0, 6.0
    
    def _get_ride_type(self, ride):
        """Determine a ride type using attributes and name."""
        # Prefer explicit ride_type when present
        if hasattr(ride, 'ride_type'):
            ride_type = ride.ride_type.lower()
            if 'pirate' in ride_type:
                return 'pirate'
            elif 'ferris' in ride_type:
                return 'ferris'
        
        # Fallback to name if ride_type not present
        name_lower = ride.name.lower()
        if 'pirate' in name_lower or 'ship' in name_lower:
            return 'pirate'
        elif 'ferris' in name_lower or 'wheel' in name_lower:
            return 'ferris'
        else:
            return 'generic'
    
    def _draw_pirate_ship(self, ride, x, y, width, height):
        """Draw the pirate ship with a swinging animation."""
        # Compute swing angle based on state
        if ride.state == 'running':
            # Swing animation uses step counter for motion
            angle = math.sin(getattr(ride, 'step_counter', 0) * 0.3) * 20  # +/- 20 degrees
        else:
            angle = 0
        
        # Choose colors based on state
        if ride.state == 'running':
            color = '#8B4513'  # Dark brown when active
            alpha = 1.0
        elif ride.state == 'loading':
            color = '#CD853F'  # Lighter brown while loading
            alpha = 0.9
        else:
            color = '#A0522D'  # Medium brown when idle
            alpha = 0.7
        
        ship_length = max(width * 0.8, 3.0)
        ship_height = max(height * 0.35, 1.5)

        # Draw the ship as a tilted ellipse scaled to the bbox
        ellipse = patches.Ellipse((x, y), ship_length, ship_height, angle=angle,
                                 facecolor=color, alpha=alpha, 
                                 edgecolor='black', linewidth=2)
        self.ax_map.add_patch(ellipse)
        
        # Draw mast scaled to ride footprint
        mast_offset = ship_length * 0.15
        mast_height = max(height * 0.6, ship_height * 1.2)
        if ride.state == 'running':
            mast_x = x + mast_offset * math.cos(math.radians(angle))
        else:
            mast_x = x + mast_offset
        mast_bottom = y - ship_height / 2
        mast_top = mast_bottom + mast_height
        self.ax_map.plot([mast_x, mast_x], [mast_bottom, mast_top], 'k-', linewidth=3)
        
        # Pirate flag if running
        if ride.state == 'running':
            flag_size = max(12, min(width, height) * 0.8)
            self.ax_map.text(mast_x + mast_offset * 0.2, mast_top - mast_height * 0.1,
                             'P', fontsize=flag_size, weight='bold')
    
    def _draw_ferris_wheel(self, ride, x, y, width, height):
        """Draw the ferris wheel with rotating cabins."""
        # Rotation depends on state
        if ride.state == 'running':
            rotation = getattr(ride, 'step_counter', 0) * 10  # Continuous rotation
        else:
            rotation = 0
        
        # Colors vary by state
        if ride.state == 'running':
            color = '#FF6347'  # Tomato red when active
            alpha = 1.0
        elif ride.state == 'loading':
            color = '#FFA500'  # Orange while loading
            alpha = 0.9
        else:
            color = '#FF8C00'  # Dark orange when idle
            alpha = 0.7
        
        # Draw outer wheel scaled to bbox
        radius = max(min(width, height) * 0.45, 1.8)
        spoke_length = radius * 0.9
        wheel = patches.Circle((x, y), radius, facecolor=color, alpha=alpha,
                              edgecolor='darkred', linewidth=3)
        self.ax_map.add_patch(wheel)
        
        # Draw wheel spokes
        for i in range(8):  # 8 spokes
            angle = math.radians(i * 45 + rotation)
            x_end = x + spoke_length * math.cos(angle)
            y_end = y + spoke_length * math.sin(angle)
            self.ax_map.plot([x, x_end], [y, y_end], 'darkred', linewidth=2)
        
        # Draw cabins
        cabin_distance = radius * 0.8
        cabin_width = max(radius * 0.18, 0.3)
        cabin_height = cabin_width * 0.7
        for i in range(6):  # 6 cabins
            angle = math.radians(i * 60 + rotation)
            cab_x = x + cabin_distance * math.cos(angle)
            cab_y = y + cabin_distance * math.sin(angle)
            cabin = patches.Rectangle((cab_x - cabin_width / 2, cab_y - cabin_height / 2),
                                    cabin_width, cabin_height,
                                    facecolor='yellow', edgecolor='black', linewidth=1)
            self.ax_map.add_patch(cabin)
        
        # Ferris wheel symbol if running
        if ride.state == 'running':
            symbol_size = max(16, radius * 6)
            self.ax_map.text(x, y + radius + cabin_height * 1.5, 'F',
                             fontsize=symbol_size, ha='center', weight='bold')
    
    def _draw_generic_ride(self, ride, x, y, width, height):
        """Draw a generic ride."""
        # Adjust appearance by state
        if ride.state == 'running':
            alpha = 1.0
            edge_color = 'red'
            edge_width = 3
        elif ride.state == 'loading':
            alpha = 0.8
            edge_color = 'orange'
            edge_width = 2
        else:  # idle
            alpha = 0.6
            edge_color = 'black' 
            edge_width = 1
        
        # Draw ride as a large circle scaled to bbox
        radius = max(min(width, height) * 0.4, 1.5)
        circle = patches.Circle((x, y), radius, facecolor='magenta', alpha=alpha, 
                               edgecolor=edge_color, linewidth=edge_width)
        self.ax_map.add_patch(circle)
        
        label_size = max(16, radius * 4)
        self.ax_map.text(x, y, 'R', fontsize=label_size, ha='center', va='center', weight='bold')
        
    def _draw_ride_queue(self, ride):
        """Draw the first part of a ride queue when present."""
        if hasattr(ride, 'queue') and ride.queue:
            queue_positions = [patron.position for patron in ride.queue[:5]]
            if queue_positions:
                queue_x, queue_y = zip(*queue_positions)
                self.ax_map.scatter(queue_x, queue_y, c='orange', s=20, alpha=0.7)

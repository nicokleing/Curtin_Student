# -*- coding: utf-8 -*-
"""Ride visualization and rendering helpers."""

import matplotlib.patches as patches

class RideVisuals:
    """Handle all ride visualization tasks."""
    
    @staticmethod
    def draw_bbox(ride, ax):
        """Render ride bounding box with state colors."""
        x, y, w, h = ride.bbox
        
        state_colors = {
            "idle": "#4c78a8",      # Blue - idle
            "loading": "#54a24b",   # Green - loading
            "running": "#f58518",   # Orange - running
            "unloading": "#e377c2"  # Pink - unloading
        }
        
        color = state_colors.get(ride.state, "#7f7f7f")
        
        # Draw rectangle with a thicker border for readability
        rect = patches.Rectangle((x, y), w, h, fill=False, ec=color, lw=3)
        ax.add_patch(rect)
        
        # Label the ride state above the box
        state_text = ride.state.upper()
        ax.text(x + w/2, y - 2, state_text, ha='center', va='top', 
                fontsize=8, color=color, weight='bold')

    @staticmethod
    def draw_queue(ride, ax):
        """Draw the current queue next to the ride."""
        if not ride.queue:
            return
            
        x, y, w, h = ride.bbox
        
        # Position queue as a vertical line next to the ride
        queue_start_x = x + w + 2  # Offset queue slightly to the right
        queue_start_y = y + h/2    # Center queue vertically
        
        # Draw each person in the queue
        for i, patron in enumerate(ride.queue):
            # Each person takes 0.8 units vertically
            patron_x = queue_start_x
            patron_y = queue_start_y + i * 0.8
            
            # Choose color by visitor type when available
            patron_color = RideVisuals._get_patron_queue_color(patron)
            
            # Plot the visitor marker
            ax.plot([patron_x], [patron_y], marker='o', ms=4, 
                   color=patron_color, alpha=0.8)
                   
            # Number the first few queue positions
            if i < 10:
                # NOTE: lightweight labels help spot long queues when tuning the sim.
                ax.text(patron_x + 0.3, patron_y, f"{i+1}", 
                       fontsize=6, va='center', alpha=0.7)
        
        # Draw a queue guide line when there is more than one person
        if len(ride.queue) > 1:
            queue_end_y = queue_start_y + (len(ride.queue) - 1) * 0.8
            ax.plot([queue_start_x - 0.2, queue_start_x - 0.2], 
                   [queue_start_y - 0.2, queue_end_y + 0.2], 
                   'k--', alpha=0.3, lw=1)

    @staticmethod
    def _get_patron_queue_color(patron):
        """Return the color used to draw a visitor in the queue."""
        if hasattr(patron, 'patron_type'):
            type_colors = {
                "adventurer": "#d62728",   # Red - adventurer
                "family": "#2ca02c",      # Green - family
                "impatient": "#ff7f0e",   # Orange - impatient
                "explorer": "#1f77b4"     # Blue - explorer
            }
            return type_colors.get(patron.patron_type.value, "#7f7f7f")
        else:
            return "#ff7f0e"  # Default queue color

    @staticmethod
    def draw_capacity_info(ride, ax):
        """Display capacity, queue, and state details."""
        x, y, w, h = ride.bbox
        
        # Current capacity info
        current_riders = len(ride.riders)
        queue_length = len(ride.queue)
        
        # Compose info text with state details
        info_text = f"RIDE {current_riders}/{ride.capacity} | Queue {queue_length}"
            
        # Append remaining-time info while active
        if ride.state in ["loading", "running", "unloading"] and hasattr(ride.timer_manager, 'timer'):
            if ride.state == "loading":
                info_text += f" | Loading ({ride.timer_manager.timer}s)"
            elif ride.state == "running":
                info_text += f" | RUNNING ({ride.timer_manager.timer}s)"
            elif ride.state == "unloading":
                info_text += f" | Unloading ({ride.timer_manager.timer}s)"
        
        # Use a background color tied to the state
        state_bg_colors = {
            "idle": "lightblue",
            "loading": "lightgreen", 
            "running": "orange",
            "unloading": "pink"
        }
        bg_color = state_bg_colors.get(ride.state, "white")
            
        # Show info above the ride
        ax.text(x + w/2, y + h + 6, info_text, ha='center', va='bottom',
               fontsize=8, bbox=dict(boxstyle="round,pad=0.3", 
               facecolor=bg_color, alpha=0.9, edgecolor='gray'))

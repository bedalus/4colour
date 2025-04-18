"""
Boundary Manager for the 4colour project.

This module handles the identification of outer boundary nodes and enclosure status.
"""

import math

class BoundaryManager:
    """Manages the identification of outer boundary nodes and their enclosure status."""
    
    def __init__(self, app):
        """Initialize with a reference to the main application.
        
        Args:
            app: The main CanvasApplication instance
        """
        self.app = app
        
    def update_enclosure_status(self):
        """Updates the 'enclosed' status for all circles by traversing the outer boundary."""
        # Handle empty or small graphs (no enclosure possible)
        if len(self.app.circles) <= 3:
            for circle in self.app.circle_lookup.values():
                circle['enclosed'] = False
            return

        # Define the starting point and connecting edge of fixed nodes (A-B)
        start_node_id = self.app.FIXED_NODE_A_ID
        next_id = self.app.FIXED_NODE_B_ID
        ab_edge = tuple(sorted([start_node_id, next_id]))
        complete = 0

        # Initialize boundary tracking
        boundary_nodes = set()
        boundary_nodes.add(start_node_id)

        # --- Start of Traversal Logic ---
        current_id = start_node_id
        previous_id = start_node_id

        # We start by conceptually moving from start_node to next_id
        while next_id:
            # If we're back at the starting point (Fixed Node A), only stop if it's not the first return
            if next_id == start_node_id and complete == 1:
                break

            current_id = next_id
            current_node = self.app.circle_lookup.get(current_id)
            
            # Only add if not already seen
            if current_id not in boundary_nodes:
                boundary_nodes.add(current_id)
            # Safety break to prevent infinite loops in case of graph inconsistency
            if len(boundary_nodes) >= len(self.app.circles):
                print(f"Warning: Boundary nodes {len(boundary_nodes)} matched total circle count ({len(self.app.circles)}). Breaking loop.")
                # Mark all as not enclosed as boundary is likely incorrect
                for circle in self.app.circle_lookup.values():
                    circle['enclosed'] = False
                if self.app.debug_enabled:
                    self.app.ui_manager.show_debug_info()
                return
        
            # Find the edge we arrived from (previous_id) in the current node's ordered list.
            # The next edge to follow is the one immediately clockwise from the arrival edge.
            # Use modulo arithmetic to wrap around the list correctly.
            prev_idx = current_node['ordered_connections'].index(previous_id)
            next_idx = (prev_idx + 1) % len(current_node['ordered_connections'])
            next_id = current_node['ordered_connections'][next_idx]

            # Handle possible scenario, there may be only one possible route from A->B
            if current_id == start_node_id and complete == 0:
                if (tuple(sorted([next_id, current_id])) == ab_edge):
                    complete = 1

            # Update previous_id for the next iteration.
            previous_id = current_id
        # --- End of Traversal Logic ---

        # Update enclosed status for all circles based on whether they were visited during traversal.
        for circle in self.app.circles:
            # Check if circle ID exists in lookup before accessing
            if circle['id'] in self.app.circle_lookup:
                self.app.circle_lookup[circle['id']]['enclosed'] = circle['id'] not in boundary_nodes
            else:
                # Handle case where circle might be in self.circles but not lookup (should not happen ideally)
                print(f"Warning: Circle ID {circle['id']} found in self.circles but not in self.circle_lookup during enclosure update.")

        # Update debug info if enabled.
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()

    def _calculate_corrected_angle(self, circle, neighbor_id):
        """Delegates angle calculation to the connection manager."""
        return self.app.connection_manager.calculate_corrected_angle(circle, neighbor_id)
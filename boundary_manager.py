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
        if len(self.app.circles) <= 2:
            for circle in self.app.circle_lookup.values():
                circle['enclosed'] = False
            return # No boundary to traverse

        # Initialize boundary tracking
        boundary_nodes = set()

        # --- Get the fixed start node (Node A) ---
        start_node = self.app.circle_lookup.get(self.app.FIXED_NODE_A_ID)

        # This will be the ID of the first node to visit *after* start_node
        next_id = self.app.circle_lookup.get(self.app.FIXED_NODE_B_ID)

        # Define the edge connecting fixed nodes (A-B)
        ab_edge = tuple(sorted([self.app.FIXED_NODE_A_ID, self.app.FIXED_NODE_B_ID]))

        # Define boundary start point
        boundary_nodes.add(start_node['id'])

        # --- Start of Traversal Logic ---
        current_id = start_node['id']
        current_node = start_node

        # Remember the very first edge we walk out on
        return_count = 0
        previous_id = start_node['id']  # We start by conceptually moving from start_node to next_id

        while next_id:
            # if we're back at A, only stop if it's not the AB‑edge first return
            if next_id == start_node['id']:
                if (tuple(sorted(next_id, current_id)) == ab_edge) and return_count == 0:
                    return_count = 1
                else:
                    break
            # Safety break to prevent infinite loops in case of graph inconsistency
            if len(boundary_nodes) > len(self.app.circles) + 1: # Allow one extra for safety margin
                 print(f"Warning: Boundary traversal exceeded expected length ({len(boundary_nodes)} > {len(self.app.circles)}). Breaking loop.")
                 # Mark all as not enclosed as boundary is likely incorrect
                 for circle in self.app.circle_lookup.values():
                     circle['enclosed'] = False
                 if self.app.debug_enabled:
                     self.app.ui_manager.show_debug_info()
                 return # Exit traversal

            # Create an edge identifier (ordered pair of node IDs)
            edge = tuple(sorted([previous_id, next_id]))

            current_id = next_id
            boundary_nodes.add(current_id) # Mark the current node as part of the boundary

            current_node = self.app.circle_lookup.get(current_id)
            # If the current node is missing or has no connections, the boundary is broken.
            if not current_node or not current_node.get('ordered_connections'):
                print(f"Warning: Boundary traversal stopped at node {current_id} (missing or no connections).")
                # Mark all as not enclosed as boundary is incomplete
                for circle in self.app.circle_lookup.values():
                    circle['enclosed'] = False
                if self.app.debug_enabled:
                    self.app.ui_manager.show_debug_info()
                return # Exit traversal

            # Find the edge we arrived from (previous_id) in the current node's ordered list.
            try:
                # Ensure ordered_connections is not empty before trying to find index
                if not current_node['ordered_connections']:
                    raise ValueError("Node has no ordered connections")

                prev_idx = current_node['ordered_connections'].index(previous_id)

                # The next edge to follow is the one immediately clockwise from the arrival edge.
                # Use modulo arithmetic to wrap around the list correctly.
                next_idx = (prev_idx + 1) % len(current_node['ordered_connections'])
                next_id = current_node['ordered_connections'][next_idx]

            except ValueError:
                 # This indicates an inconsistency in the graph data (e.g., previous_id not found).
                 print(f"Warning: Could not find previous node {previous_id} in connections of {current_id}. Boundary traversal incomplete.")
                 # Mark all as not enclosed as boundary is broken
                 for circle in self.app.circle_lookup.values():
                     circle['enclosed'] = False
                 if self.app.debug_enabled:
                     self.app.ui_manager.show_debug_info()
                 return # Exit traversal

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
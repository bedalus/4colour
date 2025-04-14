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

        # --- Get the fixed start node (Node A) ---
        start_node = self.app.circle_lookup.get(self.app.FIXED_NODE_A_ID)
        if not start_node:
            # If we can't find the fixed node, something is wrong
            # Mark all circles as not enclosed
            for circle in self.app.circle_lookup.values():
                circle['enclosed'] = False
            return
            
        # Initialize boundary tracking
        boundary_nodes = set()
        boundary_nodes.add(start_node['id'])

        # --- Start of Traversal Logic ---
        current_id = start_node['id']
        current_node = start_node

        # Find the initial outgoing edge from the start_node.
        # This is the edge with the smallest angle when measured clockwise from North (0 degrees).
        min_angle = float('inf')
        next_id = None # This will be the ID of the first node to visit *after* start_node

        for neighbor_id in current_node['ordered_connections']:
            # Calculate angle of the connection vector leaving current_node towards neighbor_id
            angle = self._calculate_corrected_angle(current_node, neighbor_id)
            if angle < min_angle:
                min_angle = angle
                next_id = neighbor_id # The neighbor connected by the edge with the minimum angle

        # Traverse the outer boundary clockwise.
        # Start from the 'next_id' found above, keeping track of the node we came from ('previous_id').
        previous_id = start_node['id'] # We start by conceptually moving from start_node to next_id
        visited_edges = set()  # Track visited edges to handle edges that appear twice in boundary
        
        while next_id and next_id != start_node['id']:
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
            
            # Check if we've already visited this node AND this specific edge
            if next_id in boundary_nodes and edge in visited_edges:
                print(f"Warning: Boundary traversal revisited node {next_id} and edge {edge} unexpectedly. Breaking loop.")
                # Mark all as not enclosed as boundary is likely incorrect
                for circle in self.app.circle_lookup.values():
                    circle['enclosed'] = False
                if self.app.debug_enabled:
                    self.app.ui_manager.show_debug_info()
                return # Exit traversal
                
            # Track this edge as visited
            visited_edges.add(edge)

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
        """Calculate angle between circles with correction for inverted y-axis.
        
        Args:
            circle: Dictionary containing the source circle's data
            neighbor_id: ID of the neighboring circle
            
        Returns:
            float: Corrected angle in degrees (0-360)
        """
        neighbor = self.app.circle_lookup.get(neighbor_id)
        if not neighbor:
            return 0
            
        # Get vector components
        dx = neighbor['x'] - circle['x']
        dy = neighbor['y'] - circle['y']
        
        # Account for any curve offset
        curve_x, curve_y = self.app.connection_manager.get_connection_curve_offset(
            circle['id'], 
            neighbor_id
        )
        
        # Adjust vector by half the curve offset
        dx += curve_x / 2
        dy += curve_y / 2
        
        # Calculate angle with correction for inverted y-axis
        # atan2 with -dy to flip the y-axis back to mathematical convention
        angle_rad = math.atan2(dx, -dy)  # Note: swapped order and negated dy
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360 range, maintaining clockwise orientation
        return (angle_deg) % 360
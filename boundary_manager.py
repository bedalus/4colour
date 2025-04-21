"""
Boundary Manager for the 4colour project.

This module handles the identification of outer boundary nodes and enclosure status.
"""

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

        # Get boundary nodes through traversal
        boundary_nodes = self._traverse_boundary()
        if boundary_nodes is None:
            # Traversal failed, mark all as not enclosed
            for circle in self.app.circle_lookup.values():
                circle['enclosed'] = False
            return

        # Update enclosed status for all circles based on whether they were visited during traversal
        for circle in self.app.circles:
            if circle['id'] in self.app.circle_lookup:
                self.app.circle_lookup[circle['id']]['enclosed'] = circle['id'] not in boundary_nodes
            else:
                print(f"Warning: Circle ID {circle['id']} found in self.circles but not in self.circle_lookup during enclosure update.")

        # Update debug info if enabled
        if self.app.debug_enabled:
            self.app.ui_manager.show_debug_info()

    def get_border_node_ids(self):
        """Returns a list of IDs for all nodes currently on the boundary (not enclosed)."""
        border_ids = []
        for circle_id, circle_data in self.app.circle_lookup.items():
            # A node is on the border if it's not enclosed
            if not circle_data.get('enclosed'):
                border_ids.append(circle_id)
        return border_ids

    def _traverse_boundary(self):
        """Traverse the outer boundary of the graph in clockwise order.
        
        Returns:
            set: Set of node IDs that form the boundary, or None if traversal failed.
        """
        # Define the starting point and connecting edge of fixed nodes (A-B)
        start_node_id = self.app.FIXED_NODE_A_ID
        next_id = self.app.FIXED_NODE_B_ID
        ab_edge = tuple(sorted([start_node_id, next_id]))
        complete = 0

        # Initialize boundary tracking
        boundary_nodes = set([start_node_id])
        
        # Traversal variables
        current_id = start_node_id
        previous_id = start_node_id

        # We start by conceptually moving from start_node to next_id
        while next_id:
            # If we're back at the starting point (Fixed Node A), only stop if it's not the first return
            if next_id == start_node_id and complete == 1:
                break

            current_id = next_id
            current_node = self.app.circle_lookup.get(current_id)
            
            # Add current node to boundary if not already seen
            if current_id not in boundary_nodes:
                boundary_nodes.add(current_id)
                
            # Safety check: prevent infinite loops
            if len(boundary_nodes) >= len(self.app.circles):
                print(f"Warning: Boundary nodes {len(boundary_nodes)} matched total circle count ({len(self.app.circles)}). Breaking loop.")
                return None
            
            # Find next node in clockwise order
            try:
                prev_idx = current_node['ordered_connections'].index(previous_id)
                next_idx = (prev_idx + 1) % len(current_node['ordered_connections'])
                next_id = current_node['ordered_connections'][next_idx]
            except (ValueError, KeyError) as e:
                print(f"Error during boundary traversal: {e}")
                return None

            # Handle possible scenario, there may be only one possible route from A->B
            if current_id == start_node_id and complete == 0:
                if tuple(sorted([next_id, current_id])) == ab_edge:
                    complete = 1

            # Update previous_id for the next iteration
            previous_id = current_id
            
        return boundary_nodes

    def _calculate_corrected_angle(self, circle, neighbor_id):
        """Delegates angle calculation to the connection manager."""
        return self.app.connection_manager.calculate_corrected_angle(circle, neighbor_id)
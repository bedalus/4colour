from color_utils import get_color_from_priority, find_lowest_available_priority
from app_enums import ApplicationMode

class RedNodeManager:
    """Manages red nodes that need attention in the graph."""
    def __init__(self):
        self.red_node_queue = []
        self.red_node_reasons = {}
        self.current_red_node_id = None

    def add_red_node(self, node_id, reason="Color conflict"):
        if node_id in self.red_node_queue:
            print(f"DEBUG: Red node {node_id} already in queue")
            return False
        self.red_node_queue.append(node_id)
        self.red_node_reasons[node_id] = reason
        if self.current_red_node_id is None:
            self.current_red_node_id = node_id
        print(f"DEBUG: Added red node {node_id} to queue with reason: {reason}")
        return True

    def get_current_red_node(self):
        return self.current_red_node_id

    def advance_to_next_red_node(self):
        if self.current_red_node_id in self.red_node_queue:
            self.red_node_queue.remove(self.current_red_node_id)
        self.red_node_reasons.pop(self.current_red_node_id, None)
        if self.red_node_queue:
            self.current_red_node_id = self.red_node_queue[0]
            print(f"DEBUG: Advanced to next red node: {self.current_red_node_id}")
        else:
            self.current_red_node_id = None
            print("DEBUG: No more red nodes in queue")
        return self.current_red_node_id

    def has_red_nodes(self):
        return len(self.red_node_queue) > 0

    def get_red_node_reason(self, node_id=None):
        if node_id is None:
            node_id = self.current_red_node_id
        return self.red_node_reasons.get(node_id, "Unknown reason")

    def clear(self):
        self.red_node_queue = []
        self.red_node_reasons = {}
        self.current_red_node_id = None
        print("DEBUG: Red node queue cleared")

class FixRedManager:
    """
    Centralizes all logic and state for red node (priority 4) handling.
    This includes detection, state management, UI triggers, and resolution.
    """
    def __init__(self, app):
        self.app = app
        self.red_node_manager = RedNodeManager()

    def check_and_resolve_color_conflicts(self, circle_id):
        """Checks for color conflicts after connections are made and resolves them."""
        # Get the current circle's data
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            return None

        current_priority = circle_data["color_priority"]

        # Get all directly connected circles
        connected_circles = circle_data.get("connected_to", [])

        # If no connections, no conflicts to resolve
        if not connected_circles:
            return current_priority

        # Check for conflicts
        has_conflict = False
        used_priorities = set()

        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if not connected_circle:
                continue

            connected_priority = connected_circle["color_priority"]
            used_priorities.add(connected_priority)
            if connected_priority == current_priority:
                has_conflict = True

        # If no conflict, keep the current priority
        if not has_conflict:
            return current_priority

        # Find the lowest priority that isn't used by any connected circle
        available_priority = find_lowest_available_priority(used_priorities)

        # If there are available priorities, use the lowest one
        if available_priority is not None:
            new_priority = available_priority
        else:
            # If all lower priorities are used, tag this node for manual fixing
            new_priority = 4
            self.app.color_manager.update_circle_color(circle_id, new_priority)
            # Updated to use RedNodeManager
            self.red_node_manager.add_red_node(circle_id, "Color conflict")
            print(f"DEBUG: Red node {circle_id} created in check_and_resolve_color_conflicts")
            self.handle_red_node_creation(circle_id)
            return new_priority

        # Update the circle with the new priority and visual appearance
        self.app.color_manager.update_circle_color(circle_id, new_priority)
        return new_priority

    def reassign_color_network(self, circle_id):
        """Reassigns colors when a circle is assigned priority 4 (red)."""
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            return 4 # Should not happen if called correctly

        original_circle_priority = 4 # This circle was just assigned red

        swap_target_id = None
        swap_target_original_priority = None

        # Find an enclosed neighbor to swap color with
        enclosed_neighbors = []
        
        for connected_id in circle_data.get("connected_to", []):
            connected_circle_data = self.app.circle_lookup.get(connected_id)
            if connected_circle_data and connected_circle_data.get("enclosed") is True:
                enclosed_neighbors.append((connected_id, connected_circle_data))
        
        # If no enclosed neighbors found, this is unexpected according to Four Color Theorem logic
        if not enclosed_neighbors:
            print(f"WARNING: Node {circle_id} has no enclosed neighbors for swapping red priority!")
            # Ensure the circle is visually red and return priority 4
            self.app.color_manager.update_circle_color(circle_id, original_circle_priority)
            return original_circle_priority
        
        # Try each enclosed neighbor until we find one that works
        for neighbor_id, neighbor_data in enclosed_neighbors:
            swap_target_id = neighbor_id
            swap_target_original_priority = neighbor_data["color_priority"]
            
            # Perform the swap
            print(f"DEBUG: Swapping red node (ID:{circle_id}) with enclosed {get_color_from_priority(swap_target_original_priority)} node (ID:{swap_target_id})")
            self.app.color_manager.update_circle_color(circle_id, swap_target_original_priority)
            self.app.color_manager.update_circle_color(swap_target_id, original_circle_priority) # Assign red (4) to the target

            # Check for conflicts after the swap
            final_priority_original = self.check_and_resolve_color_conflicts(circle_id)
            final_priority_target = self.check_internal_red_conflict(swap_target_id)
            return final_priority_original
        
        # If we get here, no viable swaps were found
        raise RuntimeError(f"ERROR: No viable enclosed neighbor found for node {circle_id} to swap with.")

    def fix_red_node(self):
        """Manually triggered function to fix a red node by swapping with an enclosed neighbor."""
        circle_id = self.red_node_manager.get_current_red_node()
        if circle_id is None:
            return False
            
        # Store the ID and advance in the queue
        self.red_node_manager.advance_to_next_red_node()
        
        # Now perform the actual swap using reassign_color_network
        new_priority = self.reassign_color_network(circle_id)
        
        # Hide the fix button and transition back to CREATE mode
        self.handle_red_node_fixed()
        
        return new_priority != 4  # Return True if we successfully changed from red

    def handle_red_node_creation(self, circle_id):
        """Handle the creation of a red node by showing the fix button and entering adjust mode."""
        print(f"DEBUG: handle_red_node_creation called for circle {circle_id}")
        
        # Store the circle ID for ADJUST mode
        self.app.last_circle_id = circle_id
        
        # Delegate mode switching to interaction handler
        self.app.interaction_handler.switch_to_red_fix_mode()
        
        # Add a small delay to ensure all UI updates are processed
        self.app.root.after(100, lambda: print("DEBUG: Mode transition complete"))

    def handle_red_node_fixed(self):
        """Handle operations after a red node has been fixed."""
        print("DEBUG: Red node fixed")
        
        # Restore the mode toggle button's original functionality
        if hasattr(self.app, 'mode_button') and hasattr(self.app, '_stored_mode_button_command'):
            # Restore the original command
            self.app.mode_button.config(command=self.app._stored_mode_button_command)
            delattr(self.app, '_stored_mode_button_command')
            print("DEBUG: Restored mode button's original command")
        
        # Check if we have a pending red node to fix
        if self.red_node_manager.has_red_nodes():
            # We have another red node that needs fixing
            next_red_node = self.red_node_manager.get_current_red_node()
            print(f"DEBUG: Found pending red node {next_red_node} to fix")
            # Handle the new red node (stays in ADJUST mode)
            self.handle_red_node_creation(next_red_node)
        else:
            # No pending red nodes, return to CREATE mode
            print("DEBUG: Auto transitioning back to CREATE mode")
            self.app._set_application_mode(ApplicationMode.CREATE)
            # Button text will be updated by the mode transition

    def check_internal_red_conflict(self, circle_id):
        """Check if a circle has any adjacent red nodes and log a warning if found."""
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return None
            
        current_priority = circle["color_priority"]
        connected_circles = circle.get("connected_to", [])
        adjacent_red_nodes = []
        
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle and connected_circle["color_priority"] == 4:
                adjacent_red_nodes.append(connected_id)
                
        if adjacent_red_nodes:
            warning_msg = f"UNHANDLED INTERNAL RED CONFLICT: Red node {circle_id} is adjacent to other red nodes: {adjacent_red_nodes}"
            print(warning_msg)
            # Add these nodes to the red node queue too
            for node_id in adjacent_red_nodes:
                self.red_node_manager.add_red_node(node_id, "Adjacent to another red node")
        
        return current_priority

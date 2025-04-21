import sys
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

    def swap_kempe_chain(self, node_id):
        """
        Performs a Kempe chain color swap for the given red node.
        Returns True if successful, False otherwise.
        """
        print(f"DEBUG: Beginning Kempe chain swap for node {node_id}")
        
        # Ensure the node exists
        node = self.app.circle_lookup.get(node_id)
        if not node:
            print(f"ERROR: Node {node_id} not found in circle_lookup")
            return False
        
        # Get connected nodes to check which colors are already adjacent
        connected_circles = node.get("connected_to", [])
        adjacent_priorities = set()
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle:
                adjacent_priorities.add(connected_circle["color_priority"])
        
        print(f"DEBUG: Node {node_id} has adjacent priorities: {adjacent_priorities}")
        
        # Try each non-red color priority that isn't adjacent to our node
        swap_priority = None
        for priority in [1, 2, 3]:
            if priority not in adjacent_priorities:
                swap_priority = priority
                print(f"DEBUG: Selected priority {swap_priority} for Kempe chain swap (not adjacent)")
                break
        
        # If all colors are adjacent, simply default to priority 1
        if swap_priority is None:
            swap_priority = 1
            print(f"DEBUG: All priorities are adjacent, defaulting to priority {swap_priority}")
        
        # Find all nodes in the Kempe chain
        kempe_chain = self.find_kempe_chain(node_id, 4, swap_priority)
        if not kempe_chain:
            print(f"ERROR: Failed to find Kempe chain for node {node_id}")
            return False
            
        print(f"DEBUG: Found Kempe chain with {len(kempe_chain)} nodes: {kempe_chain}")
        
        # Perform the swap on all nodes in the chain
        for chain_node_id in kempe_chain:
            chain_node = self.app.circle_lookup.get(chain_node_id)
            current_priority = chain_node["color_priority"]
            if current_priority == 4:  # Red
                self.app.color_manager.update_circle_color(chain_node_id, swap_priority)
                print(f"DEBUG: Changed node {chain_node_id} from red to priority {swap_priority}")
            elif current_priority == swap_priority:
                self.app.color_manager.update_circle_color(chain_node_id, 4)  # Red
                print(f"DEBUG: Changed node {chain_node_id} from priority {swap_priority} to red")
        
        print(f"DEBUG: Kempe chain swap completed successfully for node {node_id}")
        return True

    def find_kempe_chain(self, start_node_id, priority1, priority2):
        """
        Finds all nodes in a Kempe chain starting from the given node.
        A Kempe chain is a connected component where all nodes are one of the two specified priorities.
        
        Returns:
            A list of node IDs in the Kempe chain
        """
        print(f"DEBUG: Finding Kempe chain from node {start_node_id} with priorities {priority1} and {priority2}")
        
        kempe_chain = []
        visited = set()
        queue = [start_node_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            
            visited.add(current_id)
            current_node = self.app.circle_lookup.get(current_id)
            if not current_node:
                continue
            
            current_priority = current_node["color_priority"]
            if current_priority == priority1 or current_priority == priority2:
                kempe_chain.append(current_id)
                
                # Add all connected nodes to the queue
                for connected_id in current_node.get("connected_to", []):
                    if connected_id not in visited:
                        connected_node = self.app.circle_lookup.get(connected_id)
                        if connected_node and (connected_node["color_priority"] == priority1 or 
                                               connected_node["color_priority"] == priority2):
                            queue.append(connected_id)
        
        print(f"DEBUG: Kempe chain contains {len(kempe_chain)} nodes")
        return kempe_chain

    def reassign_color_network(self, circle_id):
        """MAIN ALGORITHM ENTRY POINT: Graph color reassignment when a new node is assigned priority 4 (red)."""
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            try:
                raise Exception(f"reassign_color_network: Circle {circle_id} not found in circle_lookup - invalid state")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        # Checks if the new red node is adjacent to another
        has_conflicts = self.check_internal_red_conflict(circle_id)

        if not has_conflicts:
            print(f"reassign_color_network: Red node {circle_id} has no conflicts")
            return

        # NOTE: Reaching this point means the latest red is adjacent to at least one other
        #       Start fixing the graph!
        #       Function Notes:
        #          has_red_nodes is True if we've queued any
        #          add_red_node is PUSH
        #          advance_to_next_red_node is POP
        #          self.app.color_manager.update_circle_color(circle_id, priority) sets node color. Will be needed for swapping.
        #       PUSH will only be used if our algorithm must move a red next to another red. Watch out for infinite loops.
        print(f"reassign_color_network: Called for red node: {circle_id}")
        while self.red_node_manager.has_red_nodes():
            print(f"reassign_color_network: Handling current_red_node_id: {self.red_node_manager.current_red_node_id}")
            print(f"reassign_color_network:  - reason: {self.red_node_manager.get_red_node_reason(self.red_node_manager.current_red_node_id)}")
            # Deal with the red node identified as 'current'
            current_red_node_id = self.red_node_manager.current_red_node_id
            red_circle = self.app.circle_lookup.get(current_red_node_id)

            # Get all connected nodes and their colors
            connected_circles = red_circle.get("connected_to", [])
            used_priorities = {self.app.circle_lookup.get(cid)["color_priority"] for cid in connected_circles}

            # Find available color (not used by neighbors)
            available_priority = find_lowest_available_priority(used_priorities)

            if available_priority:
                # Simple case - can directly change color
                self.app.color_manager.update_circle_color(current_red_node_id, available_priority)
            else:
                # Complex case - need to swap colors in a chain (Kempe chain)
                self.swap_kempe_chain(current_red_node_id)

            print(f"reassign_color_network: Advancing to next red node ID")
            self.red_node_manager.advance_to_next_red_node()

        # Finally, count every color being used. If red is the most, swap it with the least (using lowest priority for ties)
        # Count how many circles are using each color priority
        color_counts = {1: 0, 2: 0, 3: 0, 4: 0}  # Initialize counts for each priority
        
        # Count circles by color priority
        for circle_id, circle_data in self.app.circle_lookup.items():
            priority = circle_data.get("color_priority")
            color_counts[priority] += 1
        
        print(f"DEBUG: Color usage counts: {color_counts}")
        
        # Check if red (priority 4) is the most used color
        red_count = color_counts[4]
        max_count = max(color_counts.values())
        max_colors = [p for p, count in color_counts.items() if count == max_count]
        
        # Only proceed if red is the most used color (or tied for most) and there are red nodes
        if 4 in max_colors and red_count > 0:
            # Find the least used color, favoring lower priorities for ties
            least_used_priority = None
            least_used_count = float('inf')
            
            # Check priorities 1, 2, 3 (excluding red which is priority 4)
            for priority in [1, 2, 3]:
                count = color_counts[priority]
                if count < least_used_count:
                    least_used_count = count
                    least_used_priority = priority
            
            print(f"DEBUG: Swapping all red nodes (count: {red_count}) to priority {least_used_priority} (count: {least_used_count})")
            
            # Perform a true swap: red nodes become least_used_priority, and least_used_priority nodes become red
            red_node_ids = []
            least_used_node_ids = []
            
            # First identify all nodes of both colors (to avoid changing a node twice)
            for circle_id, circle_data in self.app.circle_lookup.items():
                priority = circle_data.get("color_priority")
                if priority == 4:  # Red
                    red_node_ids.append(circle_id)
                elif priority == least_used_priority:
                    least_used_node_ids.append(circle_id)
            
            # Now perform the swap
            for circle_id in red_node_ids:
                self.app.color_manager.update_circle_color(circle_id, least_used_priority)
                
            for circle_id in least_used_node_ids:
                self.app.color_manager.update_circle_color(circle_id, 4)

    def check_and_resolve_color_conflicts(self, circle_id):
        """Checks for color conflicts after connections are made and resolves them."""
        # Get the current circle's data
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            try:
                raise Exception(f"Circle {circle_id} not found in circle_lookup - invalid state in check_and_resolve_color_conflicts")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        current_priority = circle_data["color_priority"]

        # Get all directly connected circles
        connected_circles = circle_data.get("connected_to", [])

        # Check for conflicts
        has_conflict = False
        used_priorities = set()

        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if not connected_circle:
                try:
                    raise Exception(f"Circle {connected_id} not found in circle_lookup - invalid state in check_and_resolve_color_conflicts #2")
                except Exception as e:
                    print(f"Error: {e}")
                    sys.exit(1)

            connected_priority = connected_circle["color_priority"]
            used_priorities.add(connected_priority)
            if connected_priority == current_priority:
                has_conflict = True

        # If no conflict, keep the current priority
        if not has_conflict:
            return current_priority

        # Find the lowest priority that isn't used by any connected circle
        available_priority = find_lowest_available_priority(used_priorities)

        # Update the circle with the new priority and visual appearance
        if available_priority is None:
            print(f"DEBUG: Red node {circle_id} created in check_and_resolve_color_conflicts")
            self.app.color_manager.update_circle_color(circle_id, 4)
            # Initial entry point into the Red Node Manager
            # Push the red node id
            self.red_node_manager.add_red_node(circle_id, "No lower priorities available. Create RED")
            # Call Handler
            self.handle_red_node_creation(circle_id)
        else:
            self.app.color_manager.update_circle_color(circle_id, available_priority)

    def fix_red_node(self):
        """Manually triggered function to check any new red node."""
        circle_id = self.red_node_manager.get_current_red_node()
        if circle_id is None:
            return False
            
        # Store the ID and advance in the queue
        self.red_node_manager.advance_to_next_red_node()
        
        # Now perform the actual swap using reassign_color_network
        self.reassign_color_network(circle_id)
        
        # Hide the fix button and transition back to CREATE mode
        self.handle_red_node_fixed()

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
        print("DEBUG: Red nodes fixed")
        
        # Restore the mode toggle button's original functionality
        if hasattr(self.app, 'mode_button') and hasattr(self.app, '_stored_mode_button_command'):
            # Restore the original command
            self.app.mode_button.config(command=self.app._stored_mode_button_command)
            delattr(self.app, '_stored_mode_button_command')
            print("DEBUG: Restored mode button's original command")
        
        # Since we deal with these as they arise, this should never be true
        if self.red_node_manager.has_red_nodes():
            # This 'if' was previously:
            # # We have another red node that needs fixing
            # next_red_node = self.red_node_manager.get_current_red_node()
            # print(f"DEBUG: Found pending red node {next_red_node} to fix")
            # # Handle the new red node (stays in ADJUST mode)
            # self.handle_red_node_creation(next_red_node)
            try:
                raise Exception(f"Still have red nodes. Should be fixed already: handle_red_node_fixed")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        else:
            # No pending red nodes, return to CREATE mode
            print("DEBUG: Auto transitioning back to CREATE mode")
            self.app._set_application_mode(ApplicationMode.CREATE)

    def check_internal_red_conflict(self, circle_id):
        """Check if a circle has any adjacent red nodes and log a warning if found."""
        circle = self.app.circle_lookup.get(circle_id)
        if not circle:
            return None
            
        connected_circles = circle.get("connected_to", [])
        adjacent_red_nodes = []
        
        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle and connected_circle["color_priority"] == 4:
                adjacent_red_nodes.append(connected_id)
                
        if adjacent_red_nodes:
            for rednode in adjacent_red_nodes:
                print(f"Pushing Red node: {circle_id} is adjacent to other red node: {rednode}")
                self.red_node_manager.add_red_node(rednode, "Adjacent to another red node")
            return True
        
        return False

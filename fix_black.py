import sys
from color_utils import get_color_from_priority, find_lowest_available_priority
from app_enums import ApplicationMode

class BlackNodeManager:
    """Manages black nodes that need attention in the graph."""
    def __init__(self):
        self._black_node_queue = []
        self._black_node_reasons = {}
        self.current_black_node_id = None

    def add_black_node_(self, node_id, reason="Color conflict"):
        if node_id in self._black_node_queue:
            print(f"DEBUG: Black node {node_id} already in queue")
            return False
        self._black_node_queue.append(node_id)
        self._black_node_reasons[node_id] = reason
        if self.current_black_node_id is None:
            self.current_black_node_id = node_id
        print(f"DEBUG: Added black node {node_id} to queue with reason: {reason}")
        return True

    def get_current_black_node_(self):
        return self.current_black_node_id

    def advance_to_next_black_node_(self):
        if self.current_black_node_id in self._black_node_queue:
            self._black_node_queue.remove(self.current_black_node_id)
        self._black_node_reasons.pop(self.current_black_node_id, None)
        if self._black_node_queue:
            self.current_black_node_id = self._black_node_queue[0]
            print(f"DEBUG: Advanced to next black node: {self.current_black_node_id}")
        else:
            self.current_black_node_id = None
            print("DEBUG: No more black nodes in queue")
        return self.current_black_node_id

    def has_black_nodes(self):
        return len(self._black_node_queue) > 0

    def get_black_node_reason(self, node_id=None):
        if node_id is None:
            node_id = self.current_black_node_id
        return self._black_node_reasons.get(node_id, "Unknown reason")

    def clear(self):
        self._black_node_queue = []
        self._black_node_reasons = {}
        self.current_black_node_id = None
        print("DEBUG: Black node queue cleared")

class FixBlackManager:
    """
    Centralizes all logic and state for black node (priority 5) handling.
    This includes detection, state management, UI triggers, and resolution.
    """
    def __init__(self, app):
        self.app = app
        self._black_node_manager = BlackNodeManager()

    def swap_kempe_chain(self, node_id):
        """
        Performs a Kempe chain color swap for the given black node.
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
        
        # Try each non-black color priority that isn't adjacent to our node
        swap_priority = None
        for priority in [1, 2, 3, 4]:
            if priority not in adjacent_priorities:
                swap_priority = priority
                print(f"DEBUG: Selected priority {swap_priority} for Kempe chain swap (not adjacent)")
                break
        
        # If all colors are adjacent, simply default to priority 1
        if swap_priority is None:
            swap_priority = 1  # This can introduce conflicts!
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
            if current_priority == 5:  # Black
                self.app.color_manager.update_circle_color(chain_node_id, swap_priority)
                print(f"DEBUG: Changed node {chain_node_id} from black to priority {swap_priority}")
            elif current_priority == swap_priority:
                self.app.color_manager.update_circle_color(chain_node_id, 4)  # Black
                print(f"DEBUG: Changed node {chain_node_id} from priority {swap_priority} to black")
        
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
        """MAIN ALGORITHM ENTRY POINT: Graph color reassignment when a new node is assigned priority 5 (black)."""
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            try:
                raise Exception(f"reassign_color_network: Circle {circle_id} not found in circle_lookup - invalid state")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        # NOTE: Reaching this point means a black placeholder node needs assigning a color from 1-4
        #       Start fixing the graph!
        #       Function Notes:
        #          has_black_nodes is True if we've queued any
        #          add_black_node_ is PUSH
        #          advance_to_next_black_node_ is POP
        #          self.app.color_manager.update_circle_color(circle_id, priority) sets node color. Will be needed for swapping.
        #       PUSH will only be used if our algorithm must move a black next to another black (impossible?).
        #        - If creating something recursive, watch out for infinite loops.
        print(f"reassign_color_network: Called for black node: {circle_id}")
        while self._black_node_manager.has_black_nodes():
            print(f"reassign_color_network: Handling current_black_node_id: {self._black_node_manager.current_black_node_id}")
            print(f"reassign_color_network:  - reason: {self._black_node_manager.get_black_node_reason(self._black_node_manager.current_black_node_id)}")
            # Deal with the black node identified as 'current'
            current_black_node_id = self._black_node_manager.current_black_node_id
            black_circle = self.app.circle_lookup.get(current_black_node_id)

            # Get all connected nodes and their colors
            connected_circles = black_circle.get("connected_to", [])
            # Ensure connected_circles is not None before proceeding
            if connected_circles is None: connected_circles = []
            
            used_priorities = set()
            for cid in connected_circles:
                connected_circle = self.app.circle_lookup.get(cid)
                if connected_circle:
                    used_priorities.add(connected_circle["color_priority"])

            # Find available color (not used by neighbors)
            # Check priorities 1-4 only
            available_priority = find_lowest_available_priority(used_priorities)

            if available_priority:
                # Simple case - can directly change color
                print("DEBUG: No conflicting nodes found, skipping Kempe chain.")
                self.app.color_manager.update_circle_color(current_black_node_id, available_priority)
            else:
                # Complex case - need to swap colors in a chain (Kempe chain)
                # TODO: Add recursion if necessary - based on False being returned or still impossible to change black to another color
                self.swap_kempe_chain(current_black_node_id)

            print(f"reassign_color_network: Advancing to next black node ID")
            self._black_node_manager.advance_to_next_black_node_()

        # Finally, perform the border/overall color swap        
        # Get Border Nodes
        border_node_ids = self.app.boundary_manager.get_border_node_ids()
        if not border_node_ids:
            print("DEBUG: No border nodes found, skipping final swap.")
            return
            
        # Count Border Colors
        border_color_counts = {p: 0 for p in range(1, 5)} # Initialize counts for priorities 1-4
        for node_id in border_node_ids:
            circle_data = self.app.circle_lookup.get(node_id)
            if circle_data:
                priority = circle_data.get("color_priority")
                if priority in border_color_counts:
                    border_color_counts[priority] += 1
        print(f"DEBUG: Border color counts: {border_color_counts}")

        # Find Most Used Border Color (lowest priority wins ties)
        most_used_border_priority = -1
        max_border_count = -1
        for priority in range(1, 5): # Check priorities 1-4
            count = border_color_counts.get(priority, 0)
            if count > max_border_count:
                max_border_count = count
                most_used_border_priority = priority
            
        if most_used_border_priority == -1:
            print("DEBUG: Could not determine most used border color, skipping final swap.")
            return

        # Count Overall Colors
        overall_color_counts = {p: 0 for p in range(1, 5)} # Initialize counts for priorities 1-4
        for node_id, circle_data in self.app.circle_lookup.items():
            priority = circle_data.get("color_priority")
            if priority in overall_color_counts:
                overall_color_counts[priority] += 1
        print(f"DEBUG: Overall color counts: {overall_color_counts}")

        # Find LEAST Used Overall Color (lowest priority wins ties)
        least_used_overall_priority = -1
        lowest_overall_count = -1
        for priority in range(1, 5): # Check priorities 1-4
            count = overall_color_counts.get(priority, 0)
            if count < lowest_overall_count:
                lowest_overall_count = count
                least_used_overall_priority = priority

        if least_used_overall_priority == -1:
            print("DEBUG: Could not determine most used overall color, skipping final swap.")
            return
             
        print(f"DEBUG: Most used border color: {most_used_border_priority} (Count: {max_border_count})")
        print(f"DEBUG: LEAST used overall color: {least_used_overall_priority} (Count: {lowest_overall_count})")

        # Conditional Swap
        if most_used_border_priority == least_used_overall_priority:
            print("DEBUG: Most used border and overall colors are the same, no swap needed.")
            return

        # Perform Swap
        print(f"DEBUG: Swapping priority {most_used_border_priority} with {least_used_overall_priority}")
        border_priority_nodes = []
        overall_priority_nodes = []

        # Identify nodes for swapping
        for node_id, circle_data in self.app.circle_lookup.items():
            priority = circle_data.get("color_priority")
            if priority == most_used_border_priority:
                border_priority_nodes.append(node_id)
            elif priority == least_used_overall_priority:
                overall_priority_nodes.append(node_id)

        # Perform the swap using ColorManager
        for node_id in border_priority_nodes:
            self.app.color_manager.update_circle_color(node_id, least_used_overall_priority)
        for node_id in overall_priority_nodes:
            self.app.color_manager.update_circle_color(node_id, most_used_border_priority)

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

        # Find the lowest priority that isn't used by any connected circle (1-4)
        available_priority = find_lowest_available_priority(used_priorities)

        # Update the circle with the new priority and visual appearance
        if available_priority is None:
            print(f"DEBUG: Black node {circle_id} created in check_and_resolve_color_conflicts")
            self.app.color_manager.update_circle_color(circle_id, 5) # Assign priority 5 (Black)
            # Initial entry point into the Black Node Manager
            # Push the black node id
            self._black_node_manager.add_black_node_(circle_id, "No lower priorities available. Create BLACK")
            # Call Handler
            self.handle_black_node_creation(circle_id)
        else:
            self.app.color_manager.update_circle_color(circle_id, available_priority)

    def fix_black_node_(self):
        """Manually triggered function to check any new black node."""
        circle_id = self._black_node_manager.get_current_black_node_()
        if circle_id is None:
            return False
            
        # Store the ID and advance in the queue
        self._black_node_manager.advance_to_next_black_node_()
        
        # Now perform the actual swap using reassign_color_network
        self.reassign_color_network(circle_id)
        
        # Hide the fix button and transition back to CREATE mode
        self.handle_black_node_fixed()

    def handle_black_node_creation(self, circle_id):
        """Handle the creation of a black node by showing the fix button and entering adjust mode."""
        print(f"DEBUG: handle_black_node_creation called for circle {circle_id}")
        
        # Store the circle ID for ADJUST mode
        self.app.last_circle_id = circle_id
        
        # Delegate mode switching to interaction handler
        self.app.interaction_handler.switch_to_black_fix_mode()
        
        # Add a small delay to ensure all UI updates are processed
        self.app.root.after(100, lambda: print("DEBUG: Mode transition complete"))

    def handle_black_node_fixed(self):
        """Handle operations after a black node has been fixed."""
        print("DEBUG: Black nodes fixed")
        
        # Restore the mode toggle button's original functionality
        if hasattr(self.app, 'mode_button') and hasattr(self.app, '_stored_mode_button_command'):
            # Restore the original command
            self.app.mode_button.config(command=self.app._stored_mode_button_command)
            delattr(self.app, '_stored_mode_button_command')
            print("DEBUG: Restored mode button's original command")
        
        # Since we deal with these as they arise, this should never be true
        if self._black_node_manager.has_black_nodes():
            # This 'if' was previously:
            # # We have another black node that needs fixing
            # next_black_node_ = self._black_node_manager.get_current_black_node_()
            # print(f"DEBUG: Found pending black node {next_black_node_} to fix")
            # # Handle the new black node (stays in ADJUST mode)
            # self.handle_black_node_creation(next_black_node_)
            try:
                raise Exception(f"Still have black nodes. Should be fixed already: handle_black_node_fixed")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        else:
            # No pending black nodes, return to CREATE mode
            print("DEBUG: Auto transitioning back to CREATE mode")
            self.app._set_application_mode(ApplicationMode.CREATE)


    # We're not rotating a black node into the graph, so this isn't possible 
    # def check_internal_black_conflict(self, circle_id):
    #     """Check if a circle has any adjacent black nodes (priority 5) and queue them."""
    #     circle = self.app.circle_lookup.get(circle_id)
    #     if not circle:
    #         return False # Indicate no conflict if circle doesn't exist
            
    #     connected_circles = circle.get("connected_to", [])
    #     # Ensure connected_circles is not None before proceeding
    #     if connected_circles is None: connected_circles = []
        
    #     has_conflict = False
    #     for connected_id in connected_circles:
    #         connected_circle = self.app.circle_lookup.get(connected_id)
    #         # Check if connected circle exists and is black (priority 5)
    #         if connected_circle and connected_circle.get("color_priority") == 5:
    #             print(f"Pushing Black node: {circle_id} is adjacent to black node: {connected_id}")
    #             # Add the *adjacent* black node to the queue for processing
    #             self._black_node_manager.add_black_node_(connected_id, f"Adjacent to newly created black node {circle_id}")
    #             has_conflict = True
                
    #     return has_conflict # Return True if any adjacent black node was found and queued

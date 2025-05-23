import sys
import itertools # Import itertools for combinations
from color_utils import get_color_from_priority, find_lowest_available_priority
from app_enums import ApplicationMode

class VCOLORNodeManager:
    """Manages 'V' Colour nodes that need attention in the graph."""
    def __init__(self):
        self._VCOLOR_node_queue = []
        self._VCOLOR_node_reasons = {}
        self.current_VCOLOR_node_id = None

    def add_VCOLOR_node_(self, node_id, reason="Colour conflict"):
        if node_id in self._VCOLOR_node_queue:
            print(f"DEBUG: VCOLOR node {node_id} already in queue")
            return False
        self._VCOLOR_node_queue.append(node_id)
        self._VCOLOR_node_reasons[node_id] = reason
        if self.current_VCOLOR_node_id is None:
            self.current_VCOLOR_node_id = node_id
        print(f"DEBUG: Added VCOLOR node {node_id} to queue with reason: {reason}")
        return True

    def get_current_VCOLOR_node_(self):
        return self.current_VCOLOR_node_id

    def advance_to_next_VCOLOR_node_(self):
        if self.current_VCOLOR_node_id in self._VCOLOR_node_queue:
            self._VCOLOR_node_queue.remove(self.current_VCOLOR_node_id)
        self._VCOLOR_node_reasons.pop(self.current_VCOLOR_node_id, None)
        if self._VCOLOR_node_queue:
            self.current_VCOLOR_node_id = self._VCOLOR_node_queue[0]
            print(f"DEBUG: Advanced to next VCOLOR node: {self.current_VCOLOR_node_id}")
        else:
            self.current_VCOLOR_node_id = None
            print("DEBUG: VCOLOR node queue empty")
        return self.current_VCOLOR_node_id

    def has_VCOLOR_nodes(self):
        return len(self._VCOLOR_node_queue) > 0

    def get_VCOLOR_node_reason(self, node_id=None):
        if node_id is None:
            node_id = self.current_VCOLOR_node_id
        return self._VCOLOR_node_reasons.get(node_id, "Unknown reason")

    def clear(self):
        self._VCOLOR_node_queue = []
        self._VCOLOR_node_reasons = {}
        self.current_VCOLOR_node_id = None
        print("DEBUG: VCOLOR node queue cleared")

class FixVCOLORManager:
    """
    Centralises all logic and state for VCOLOR node (priority 5) handling.
    This includes detection, state management, UI triggers, and resolution.
    """
    def __init__(self, app):
        self.app = app
        self._VCOLOR_node_manager = VCOLORNodeManager()

    def swap_kempe_chain(self, node_id):
        """
        Performs a Kempe chain colour swap to resolve the colour node.
        Tries different pairs of adjacent colours until one allows the colour node to be coloured.
        Returns True if successful, False otherwise.
        """
        print(f"DEBUG: Beginning Kempe chain swap for VCOLOR node {node_id}")

        node = self.app.circle_lookup.get(node_id)
        if not node:
            print(f"ERROR: Node {node_id} not found in circle_lookup")
            return False
        if node.get("color_priority") != 5:
            print(f"ERROR: Node {node_id} is not a VCOLOR node (priority 5)")
            return False # Should only be called for colour nodes

        # Get adjacent nodes and their priorities (1-4)
        connected_circles = node.get("connected_to", [])
        adjacent_nodes_by_priority = {p: [] for p in range(1, 5)}
        adjacent_priorities = set()

        for connected_id in connected_circles:
            connected_circle = self.app.circle_lookup.get(connected_id)
            if connected_circle:
                priority = connected_circle.get("color_priority")
                if 1 <= priority <= 4: # Only consider standard colours
                    adjacent_priorities.add(priority)
                    adjacent_nodes_by_priority[priority].append(connected_id)

        print(f"DEBUG: VCOLOR Node {node_id} has adjacent priorities: {adjacent_priorities}")
        print(f"DEBUG: Adjacent nodes by priority: {adjacent_nodes_by_priority}")

        # We need at least two different adjacent colours to attempt a swap
        if len(adjacent_priorities) < 2:
             print(f"ERROR: Cannot perform Kempe swap for node {node_id}. Needs at least 2 different adjacent colours.")
             # This case might indicate an issue elsewhere or a very simple graph structure
             # Try assigning the lowest available if possible (though this method is usually called when none are available)
             available_priority = find_lowest_available_priority(adjacent_priorities)
             if available_priority:
                 print(f"DEBUG: Found simple available priority {available_priority} for node {node_id}")
                 self.app.color_manager.update_circle_color(node_id, available_priority)
                 return True
             else:
                 print(f"ERROR: Node {node_id} has < 2 adjacent colours and no simple available priority.")
                 return False # Cannot resolve

        # Iterate through pairs of adjacent priorities (c1, c2)
        # Sort priorities to ensure consistent pair generation (e.g., (1, 2) not (2, 1))
        sorted_priorities = sorted(list(adjacent_priorities))
        for c1, c2 in itertools.combinations(sorted_priorities, 2):
            print(f"\nDEBUG: Attempting Kempe swap with priorities ({c1}, {c2}) for node {node_id}")

            # Get a starting neighbor node for each color
            # We only need one neighbor of each colour to start the chain check
            neighbor_c1_id = adjacent_nodes_by_priority[c1][0] if adjacent_nodes_by_priority[c1] else None
            neighbor_c2_id = adjacent_nodes_by_priority[c2][0] if adjacent_nodes_by_priority[c2] else None

            if not neighbor_c1_id or not neighbor_c2_id:
                 print(f"WARN: Missing neighbor for priority {c1} or {c2}. Skipping pair.")
                 continue # Should not happen if adjacent_priorities was populated correctly

            print(f"DEBUG: Starting chain search from neighbor {neighbor_c1_id} (priority {c1})")
            # Find the Kempe chain starting from the neighbor with priority c1
            kempe_chain_nodes = self.find_kempe_chain(neighbor_c1_id, c1, c2)

            if not kempe_chain_nodes:
                print(f"WARN: No Kempe chain found starting from {neighbor_c1_id} with ({c1}, {c2}). This might be okay.")
                # If the chain is empty, it means neighbor_c1 is isolated regarding c1/c2,
                # which implies neighbor_c2 cannot be in this non-existent chain.
                # However, find_kempe_chain should at least return [neighbor_c1_id].
                # Let's treat this as if n2 is not in the chain.
                pass # Proceed to check if n2 is in the (empty) chain set

            kempe_chain_set = set(kempe_chain_nodes)
            print(f"DEBUG: Found ({c1}, {c2}) chain: {kempe_chain_nodes}")

            # Check if the neighbor with priority c2 is in the *same* chain
            if neighbor_c2_id not in kempe_chain_set:
                print(f"DEBUG: Success! Neighbor {neighbor_c2_id} (priority {c2}) is NOT in the chain starting from {neighbor_c1_id}.")
                print(f"DEBUG: Swapping colours {c1} <-> {c2} in the chain: {kempe_chain_nodes}")

                # Perform the colour swap for all nodes in this chain
                for chain_node_id in kempe_chain_nodes:
                    chain_node = self.app.circle_lookup.get(chain_node_id)
                    if not chain_node: continue # Should exist

                    current_priority = chain_node["color_priority"]
                    new_priority = -1
                    if current_priority == c1:
                        new_priority = c2
                    elif current_priority == c2:
                        new_priority = c1
                    else:
                        # This should not happen if find_kempe_chain is correct
                        print(f"ERROR: Node {chain_node_id} in ({c1},{c2}) chain has unexpected priority {current_priority}!")
                        continue

                    self.app.color_manager.update_circle_color(chain_node_id, new_priority)
                    # print(f"DEBUG: Swapped node {chain_node_id} from {current_priority} to {new_priority}") # Verbose

                # Now that the c1 neighbor has changed color, c1 is available for the VCOLOR node
                print(f"DEBUG: Assigning freed priority {c1} to VCOLOR node {node_id}")
                self.app.color_manager.update_circle_color(node_id, c1)
                print(f"DEBUG: Kempe chain swap completed successfully for node {node_id}.")
                return True # Successfully resolved the VCOLOR node
            else:
                print(f"DEBUG: Neighbor {neighbor_c2_id} (priority {c2}) IS in the chain. Trying next pair.")

        # If loop finishes, no suitable Kempe chain swap was found
        print(f"ERROR: Exhausted all Kempe chain pairs for node {node_id}. Could not resolve VCOLOR.")
        # According to the theorem, for planar graphs, this shouldn't happen if the graph had a valid 4-colouring before the conflict.
        # This might indicate a non-planar graph segment or an issue in the graph state.
        return False

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
        """MAIN ALGORITHM ENTRY POINT: Graph colour reassignment when a new node is assigned priority 5 ('V' colour)."""
        circle_data = self.app.circle_lookup.get(circle_id)
        if not circle_data:
            try:
                raise Exception(f"reassign_color_network: Circle {circle_id} not found in circle_lookup - invalid state")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        # NOTE: Reaching this point means a colour placeholder node needs assigning a colour from 1-4
        #       Start fixing the graph!
        #       Function Notes:
        #          has_VCOLOR_nodes is True if we've queued any
        #          add_VCOLOR_node_ is PUSH
        #          advance_to_next_VCOLOR_node_ is POP
        #          self.app.color_manager.update_circle_color(circle_id, priority) sets node color. Will be needed for swapping.
        #       PUSH will only be used if our algorithm must move a VCOLOR next to another VCOLOR (impossible?).
        #        - If creating something recursive, watch out for infinite loops.
        print(f"reassign_color_network: Called for VCOLOR node: {circle_id}")
        while self._VCOLOR_node_manager.has_VCOLOR_nodes():
            print(f"reassign_color_network: Handling current_VCOLOR_node_id: {self._VCOLOR_node_manager.current_VCOLOR_node_id}")
            print(f"reassign_color_network:  - reason: {self._VCOLOR_node_manager.get_VCOLOR_node_reason(self._VCOLOR_node_manager.current_VCOLOR_node_id)}")
            # Deal with the VCOLOR node identified as 'current'
            current_VCOLOR_node_id = self._VCOLOR_node_manager.current_VCOLOR_node_id
            VCOLOR_circle = self.app.circle_lookup.get(current_VCOLOR_node_id)

            # Get all connected nodes and their colours
            connected_circles = VCOLOR_circle.get("connected_to", [])
            # Ensure connected_circles is not None before proceeding
            if connected_circles is None: connected_circles = []
            
            used_priorities = set()
            for cid in connected_circles:
                connected_circle = self.app.circle_lookup.get(cid)
                if connected_circle:
                    used_priorities.add(connected_circle["color_priority"])

            # Find available colour (not used by neighbors)
            # Check priorities 1-4 only
            available_priority = find_lowest_available_priority(used_priorities)

            if available_priority:
                # Simple case - can directly change color
                print("DEBUG: No conflicting nodes found, skipping Kempe chain.")
                self.app.color_manager.update_circle_color(current_VCOLOR_node_id, available_priority)
            else:
                # Complex case - need to swap colours in a chain (Kempe chain)
                self.swap_kempe_chain(current_VCOLOR_node_id)

            # Loop until queue is empty. Queue system may be overkill depending on solution, but haven't ruled out recursion yet.
            if not self._VCOLOR_node_manager.has_VCOLOR_nodes():
                break

            print(f"reassign_color_network: Advancing to next VCOLOR node ID")
            self._VCOLOR_node_manager.advance_to_next_VCOLOR_node_()

        # Finally, perform the border/overall colour swap
        # Get Border Nodes
        border_node_ids = self.app.boundary_manager.get_border_node_ids()
        if not border_node_ids:
            print("DEBUG: No border nodes found, skipping final swap.")
            return

        # Count Border Colours
        border_color_counts = {p: 0 for p in range(1, 5)} # Initialize counts for priorities 1-4
        for node_id in border_node_ids:
            circle_data = self.app.circle_lookup.get(node_id)
            if circle_data:
                priority = circle_data.get("color_priority")
                if priority in border_color_counts:
                    border_color_counts[priority] += 1
        print(f"DEBUG: Border colour counts: {border_color_counts}")

        # Find Most Used Border Colour (lowest priority wins ties)
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

        # Count Overall Colours
        overall_color_counts = {p: 0 for p in range(1, 5)} # Initialize counts for priorities 1-4
        for node_id, circle_data in self.app.circle_lookup.items():
            priority = circle_data.get("color_priority")
            if priority in overall_color_counts:
                overall_color_counts[priority] += 1
        print(f"DEBUG: Overall colour counts: {overall_color_counts}")

        # Find LEAST Used Overall Colour (lowest priority wins ties)
        least_used_overall_priority = -1
        lowest_overall_count = float('inf') # Initialize with infinity to correctly find the minimum
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
            print("DEBUG: Most used border and overall colours are the same, no swap needed.")
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
        """Checks for colour conflicts after connections are made and resolves them."""
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
            print(f"DEBUG: VCOLOR node {circle_id} created in check_and_resolve_color_conflicts")
            self.app.color_manager.update_circle_color(circle_id, 5) # Assign priority 5 ('V' colour)
            # Initial entry point into the colour Node Manager
            # Push the colour node id
            self._VCOLOR_node_manager.add_VCOLOR_node_(circle_id, "No lower priorities available. Create VCOLOR")
            # Call Handler
            self.handle_VCOLOR_node_creation(circle_id)
        else:
            self.app.color_manager.update_circle_color(circle_id, available_priority)

    def fix_VCOLOR_node_(self):
        """Manually triggered function to check any new VCOLOR node."""
        circle_id = self._VCOLOR_node_manager.get_current_VCOLOR_node_()
        if circle_id is None:
            return False
        
        # Now perform the actual swap using reassign_color_network
        self.reassign_color_network(circle_id)
        
        # Hide the fix button and transition back to CREATE mode
        self.handle_VCOLOR_node_fixed()

    def handle_VCOLOR_node_creation(self, circle_id):
        """Handle the creation of a VCOLOR node by showing the fix button and entering adjust mode."""
        print(f"DEBUG: handle_VCOLOR_node_creation called for node {circle_id}")
        
        # Store the circle ID for ADJUST mode
        self.app.last_circle_id = circle_id
        
        # Delegate mode switching to interaction handler
        self.app.interaction_handler.switch_to_VCOLOR_fix_mode()
        
        # Add a small delay to ensure all UI updates are processed
        self.app.root.after(100, lambda: print("DEBUG: Mode transition complete"))

    def handle_VCOLOR_node_fixed(self):
        """Handle operations after a VCOLOR node has been fixed."""
        print("DEBUG: VCOLOR nodes fixed")
        
        # Restore the mode toggle button's original functionality
        if hasattr(self.app, 'mode_button') and hasattr(self.app, '_stored_mode_button_command'):
            # Restore the original command
            self.app.mode_button.config(command=self.app._stored_mode_button_command)
            delattr(self.app, '_stored_mode_button_command')
            print("DEBUG: Restored mode button's original command")
        
        # Since we deal with these as they arise, this should never be true
        if self._VCOLOR_node_manager.has_VCOLOR_nodes():
            try:
                raise Exception(f"Still have VCOLOR nodes. Should be fixed already: handle_VCOLOR_node_fixed")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            # No pending VCOLOR nodes, return to CREATE mode
            print("DEBUG: Auto transitioning back to CREATE mode")
            self.app._set_application_mode(ApplicationMode.CREATE)

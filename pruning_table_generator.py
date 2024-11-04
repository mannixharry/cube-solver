import json
import os
import cube
from collections import defaultdict

class Pruning_Table_Generator:
    MAX_DEPTH = 12  # Maximum depth for cube exploration

    def __init__(self, regenerate_tables=False):
        generate_g1_pruning_table = not os.path.isfile('g1_pruning_table') or regenerate_tables
        
        if generate_g1_pruning_table:
            with open('g1_pruning_table.json', 'w') as g1_pruning_file:
                data = self.generate_g1_pruning_table()
                json.dump(data, g1_pruning_file, indent=4)

    def generate_g1_pruning_table(self):
        # Initialize pruning table as a dictionary
        g1_pruning_table = defaultdict(lambda: -1)  # -1 indicates unvisited states
        initial_state = cube.CoordCube()  # Start with default state [0, 0, 0]

        # Iteratively deepen until reaching the desired max number of states
        while len(g1_pruning_table) < 10000:  # Set the desired number of states to explore
            visited = set()  # Track visited states at each new depth
            self.iddfs(initial_state, g1_pruning_table, visited)
            print(f'Explored states at depth {self.MAX_DEPTH}: {len(g1_pruning_table)}')

        return dict(g1_pruning_table)  # Convert to regular dict for JSON output

    def iddfs(self, initial_state, g1_pruning_table, visited):
        # Explore states up to the maximum depth
        for depth_limit in range(self.MAX_DEPTH + 1):
            self.dfs(initial_state, g1_pruning_table, visited, 0, depth_limit)

    def dfs(self, current_state, g1_pruning_table, visited, current_depth, max_depth):
        coord_tuple = (
            current_state.corner_orientation_coordinate,
            current_state.edge_orientation_coordinate,
            current_state.UD_slice_coordinate
        )

        coord_key = str(coord_tuple)  # Convert tuple to string for JSON serialization

        # If this state has been visited or if it’s beyond the depth limit, return
        if coord_key in visited or current_depth > max_depth:
            return

        # Mark this state as visited
        visited.add(coord_key)

        # If this state hasn't been added to the pruning table, add it with the current depth
        if g1_pruning_table[coord_key] == -1:
            g1_pruning_table[coord_key] = current_depth

        # Explore further if we're not yet at the maximum depth
        if current_depth < max_depth:
            for move in range(18):  # Assuming 18 possible moves
                next_state = cube.CoordCube(current_state)  # Copy current state
                next_state.rotate_clockwise(move)  # Apply the move

                # Recursively explore the next state
                self.dfs(next_state, g1_pruning_table, visited, current_depth + 1, max_depth)

# Create an instance of the pruning table generator
pruning_table = Pruning_Table_Generator(regenerate_tables=True)
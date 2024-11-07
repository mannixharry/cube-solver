import json
import os
import cube
from collections import deque

class PruningTableGenerator:
    def __init__(self, regenerate_tables=False):
        # Flags for regenerating tables
        generate_udslice_corner_table = not os.path.isfile('udslice_corner_table.json') or regenerate_tables
        generate_udslice_edge_table = not os.path.isfile('udslice_edge_table.json') or regenerate_tables
        generate_corner_udslice_edge_table = not os.path.isfile('corner_udslice_edge_table.json') or regenerate_tables
        generate_mainedge_udslice_edge_table = not os.path.isfile('main_edge_udslice_edge_table.json') or regenerate_tables

        # Generate tables as needed
        if generate_udslice_corner_table:
            with open('udslice_corner_table.json', 'w') as corner_file:
                corner_table = self.generate_udslice_corner_table()
                json.dump(corner_table, corner_file, indent=4)

        if generate_udslice_edge_table:
            with open('udslice_edge_table.json', 'w') as edge_file:
                edge_table = self.generate_udslice_edge_table()
                json.dump(edge_table, edge_file, indent=4)
        
        if generate_corner_udslice_edge_table:
            with open('corner_udslice_edge_table.json', 'w') as corner_udslice_file:
                corner_udslice_table = self.generate_corner_udslice_edge_table()
                json.dump(corner_udslice_table, corner_udslice_file, indent=4)

        if generate_mainedge_udslice_edge_table:
            with open('main_edge_udslice_edge_table.json', 'w') as mainedge_udslice_file:
                mainedge_udslice_table = self.generate_mainedge_udslice_edge_table()
                json.dump(mainedge_udslice_table, mainedge_udslice_file, indent=4)

    def generate_udslice_corner_table(self):
        """Generates the pruning table for UD Slice and Corner Orientation."""
        udslice_corner_table = {}
        initial_state = cube.CoordCube()  # Assuming default state [0, 0, 0]

        queue = deque([(initial_state, 0)])  # (cube_state, depth)
        visited = set()

        while queue and len(udslice_corner_table) < 10395:
            current_state, depth = queue.popleft()
            coord_tuple = (
                current_state.UD_slice_coordinate,
                current_state.corner_orientation_coordinate
            )

            if coord_tuple in visited:
                continue

            visited.add(coord_tuple)
            udslice_corner_table[str(coord_tuple)] = depth

            for move in range(18):  # Assuming 18 possible moves
                next_state = cube.CoordCube(current_state)  # Copy current state
                next_state.rotate_clockwise(move)  # Apply move

                next_coord_tuple = (
                    next_state.UD_slice_coordinate,
                    next_state.corner_orientation_coordinate
                )

                if next_coord_tuple not in visited:
                    queue.append((next_state, depth + 1))

        return udslice_corner_table

    def generate_udslice_edge_table(self):
        """Generates the pruning table for UD Slice and Edge Orientation."""
        udslice_edge_table = {}
        initial_state = cube.CoordCube()  # Assuming default state [0, 0, 0]

        queue = deque([(initial_state, 0)])  # (cube_state, depth)
        visited = set()

        while queue and len(udslice_edge_table) < 1013760:
            current_state, depth = queue.popleft()
            coord_tuple = (
                current_state.UD_slice_coordinate,
                current_state.edge_orientation_coordinate
            )

            if coord_tuple in visited:
                continue

            visited.add(coord_tuple)
            udslice_edge_table[str(coord_tuple)] = depth

            for move in range(18):  # Assuming 18 possible moves
                next_state = cube.CoordCube(current_state)  # Copy current state
                next_state.rotate_clockwise(move)  # Apply move

                next_coord_tuple = (
                    next_state.UD_slice_coordinate,
                    next_state.edge_orientation_coordinate
                )

                if next_coord_tuple not in visited:
                    queue.append((next_state, depth + 1))

        return udslice_edge_table

    def generate_corner_udslice_edge_table(self):
        """Generates the pruning table for Corner Permutation and UD Slice Edge Permutation."""
        corner_udslice_edge_table = {}
        initial_state = cube.CoordCube()  # Default state [0, 0, 0]

        queue = deque([(initial_state, 0)])  # (cube_state, depth)
        visited = set()

        while queue and len(corner_udslice_edge_table) < 40320 * 24:  # Max states for corner and UD slice edge permutations
            current_state, depth = queue.popleft()
            coord_tuple = (
                current_state.corner_permutation_coordinate,
                current_state.UD_slice_edge_permutation_coordinate
            )

            if coord_tuple in visited:
                continue

            visited.add(coord_tuple)
            corner_udslice_edge_table[str(coord_tuple)] = depth

            for move in [0,3,7,8,10,11,12,15]:  # Assuming 18 possible moves
                next_state = cube.CoordCube(current_state)  # Copy current state
                next_state.rotate_clockwise(move)  # Apply move

                next_coord_tuple = (
                    next_state.corner_permutation_coordinate,
                    next_state.UD_slice_edge_permutation_coordinate
                )

                if next_coord_tuple not in visited:
                    queue.append((next_state, depth + 1))

        return corner_udslice_edge_table

    def generate_mainedge_udslice_edge_table(self):
        """Generates the pruning table for Main Edge Permutation and UD Slice Edge Permutation."""
        mainedge_udslice_edge_table = {}
        initial_state = cube.CoordCube()  # Default state [0, 0, 0]

        queue = deque([(initial_state, 0)])  # (cube_state, depth)
        visited = set()

        while queue and len(mainedge_udslice_edge_table) < 40320 * 24:  # Max states for main edge and UD slice edge permutations
            current_state, depth = queue.popleft()
            coord_tuple = (
                current_state.main_edge_permutation_coordinate,
                current_state.UD_slice_edge_permutation_coordinate
            )

            if coord_tuple in visited:
                continue

            visited.add(coord_tuple)
            mainedge_udslice_edge_table[str(coord_tuple)] = depth

            for move in [0,3,7,8,10,11,12,15]:  # Assuming 18 possible moves
                next_state = cube.CoordCube(current_state)  # Copy current state
                next_state.rotate_clockwise(move)  # Apply move

                next_coord_tuple = (
                    next_state.main_edge_permutation_coordinate,
                    next_state.UD_slice_edge_permutation_coordinate
                )

                if next_coord_tuple not in visited:
                    queue.append((next_state, depth + 1))

        return mainedge_udslice_edge_table

# Create an instance of the pruning table generator with regeneration enabled
pruning_table_generator = PruningTableGenerator(regenerate_tables=True)

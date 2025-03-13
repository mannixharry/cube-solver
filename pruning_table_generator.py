import json
import os
import cube
from collections import deque
from data import Data
from datetime import datetime

class PruningTableGenerator:
    def __init__(self, regenerate_tables=False):

        # File paths for the pruning tables
        udslice_corner_table_path = 'pruning_tables/udslice_corner_table.json'
        udslice_edge_table_path = 'pruning_tables/udslice_edge_table.json'
        corner_udslice_edge_table_path = 'pruning_tables/corner_udslice_edge_table.json'
        mainedge_udslice_edge_table_path = 'pruning_tables/main_edge_udslice_edge_table.json'

        # Flags for regenerating tables
        generate_udslice_corner_table = not os.path.isfile(udslice_corner_table_path) or regenerate_tables
        generate_udslice_edge_table = not os.path.isfile(udslice_edge_table_path) or regenerate_tables
        generate_corner_udslice_edge_table = not os.path.isfile(corner_udslice_edge_table_path) or regenerate_tables
        generate_mainedge_udslice_edge_table = not os.path.isfile(mainedge_udslice_edge_table_path) or regenerate_tables

        # Generate tables as needed
        if generate_udslice_corner_table:
            with open(udslice_corner_table_path, 'w') as corner_file:
                corner_table = self.generate_udslice_corner_table()
                json.dump(corner_table, corner_file, indent=4)

        if generate_udslice_edge_table:
            with open(udslice_edge_table_path, 'w') as edge_file:
                edge_table = self.generate_udslice_edge_table()
                json.dump(edge_table, edge_file, indent=4)
        
        if generate_corner_udslice_edge_table:
            with open(corner_udslice_edge_table_path, 'w') as corner_udslice_file:
                corner_udslice_table = self.generate_corner_udslice_edge_table()
                json.dump(corner_udslice_table, corner_udslice_file, indent=4)

        if generate_mainedge_udslice_edge_table:
            with open(mainedge_udslice_edge_table_path, 'w') as mainedge_udslice_file:
                mainedge_udslice_table = self.generate_mainedge_udslice_edge_table()
                json.dump(mainedge_udslice_table, mainedge_udslice_file, indent=4)

    def generate_general_pruning_table(self, pruning_coordinates, allowed_moves, table_size):
        
        pruning_coordinate_1, pruning_coordinate_2 = pruning_coordinates
        general_table = {}
        initial_state = cube.CoordCube()  # Assuming default state [0, 0, 0]

        queue = deque([(initial_state, 0)])  # (cube_state, depth)
        visited = set()

        while queue and len(general_table) <= table_size:
            current_state, depth = queue.popleft()
            coord_tuple = (
                getattr(current_state, pruning_coordinate_1),
                getattr(current_state, pruning_coordinate_2)
            )

            if coord_tuple in visited:
                continue

            visited.add(coord_tuple)
            general_table[str(coord_tuple)] = depth

            for move in allowed_moves:  # Moves for G1 or moves for G2
                next_state = cube.CoordCube(current_state)  # Copy current state
                next_state.rotate_clockwise(move)  # Apply move

                next_coord_tuple = (
                    getattr(next_state, pruning_coordinate_1),
                    getattr(next_state, pruning_coordinate_2)
                )

                if next_coord_tuple not in visited:
                    queue.append((next_state, depth + 1))

        return general_table
    


    def generate_udslice_corner_table(self):
        return self.generate_general_pruning_table(('UD_slice_coordinate','corner_orientation_coordinate'), Data.g1_allowed_moves, 2048 * 495)
    
    def generate_udslice_edge_table(self):
        return self.generate_general_pruning_table(('UD_slice_coordinate', 'edge_orientation_coordinate'), Data.g1_allowed_moves, 2187 * 495)
    
    def generate_corner_udslice_edge_table(self):
        return self.generate_general_pruning_table(('corner_permutation_coordinate', 'four_edge_permutation_coordinate'), Data.g2_allowed_moves, 40320 * 24)
    
    def generate_mainedge_udslice_edge_table(self):
        return self.generate_general_pruning_table(('eight_edge_permutation_coordinate', 'four_edge_permutation_coordinate'), Data.g2_allowed_moves, 40320 * 24)
   
class Pruning_Tables:
    
    def load(self):
        try:
            with open('pruning_tables/udslice_corner_table.json', 'r') as file:
                self.udslice_corner_table = json.load(file)
            with open('pruning_tables/udslice_edge_table.json', 'r') as file:
                self.udslice_edge_table = json.load(file)
            with open('pruning_tables/corner_udslice_edge_table.json', 'r') as file:
                self.corner_udslice_edge_table = json.load(file)
            with open('pruning_tables/main_edge_udslice_edge_table.json', 'r') as file:
                self.mainedge_udslice_edge_table = json.load(file)
        except:
            print('Generating pruning tables...')
            start_time = datetime.now()
            pruning_table_generator = PruningTableGenerator(regenerate_tables=True)
            print('Pruning table generation complete')
            print(f"Time to generate: {datetime.now() - start_time}")

            self.load()

    def __init__(self):
        self.load()

pruning_tables = Pruning_Tables()
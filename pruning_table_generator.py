import json
import multiprocessing.process
import os
from collections import deque
from data import Data
from datetime import datetime
import multiprocessing

import cube
cube.import_tables()

class PruningTableGenerator:
    def __init__(self):

        # File paths for the pruning tables
        self.__path_function_pairs = [
            ('pruning_tables/udslice_corner_table.json', self.generate_udslice_corner_table),
            ('pruning_tables/udslice_edge_table.json', self.generate_udslice_edge_table),
            ('pruning_tables/corner_udslice_edge_table.json', self.generate_corner_udslice_edge_table),
            ('pruning_tables/main_edge_udslice_edge_table.json', self.generate_mainedge_udslice_edge_table)
        ]
        
    def generate_table(self, path, function):
        table = function()
        with open(path, 'w') as file:
            json.dump(table, file, indent=4)
        
    def parallel_table_generation(self):
        
        print('Generating pruning tables...')
        start_time = datetime.now()
    
        processes = []
        for path, function in self.__path_function_pairs:
            if os.path.exists(path):
                continue # skip existing tables
            process = multiprocessing.Process(target=self.generate_table, args=(path,function))
            process.start()
            processes.append(process)
            
        for process in processes:
            process.join()
            
        print(f"Time to generate: {datetime.now() - start_time}")
                               
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

if __name__ == '__main__':
    pruning_tables = PruningTableGenerator()
    pruning_tables.parallel_table_generation()
else:
    pruning_tables = PruningTableGenerator()

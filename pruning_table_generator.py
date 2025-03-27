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
    '''Generates and saves pruning table files. 
    '''
    def __init__(self):
        '''Defines path_function_pairs dictionary. 
        '''
        # File paths for the pruning tables
        self.__path_function_pairs = [
            ('pruning_tables/UD_slice_corner_table.json', self.generate_UD_slice_corner_table),
            ('pruning_tables/UD_slice_edge_table.json', self.generate_UD_slice_edge_table),
            ('pruning_tables/corner_four_edge_table.json', self.generate_corner_four_edge_table),
            ('pruning_tables/eight_edge_four_edge_table.json', self.generate_eight_edge_four_edge_table)
        ]
        
    def generate_table(self, path, generating_function):
        '''Calls generating function, and saves output to path.
        
        Args:
            path (str): Save path.
            generating_function (function): function to generate pruning table.
        '''
        table = generating_function()
        with open(path, 'w') as file:
            json.dump(table, file, indent=4)
        
    def parallel_table_generation(self):
        '''Calls generating methods for each table not already present.
        Performs multiprocessing. Each generating function runs on a different process. 
        Decreases pruning table generating time significantly. 
        '''
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
        '''Generates a pruning table, taking the pruning coordinates, allowed moves and table size as input.
        Each table stores two coordinates, used as an index, and an integer value.
        The integer is an underestimate of the minimum number of moves required to solve the cube to either g1 or g2. 
        This is called an admissible heuristic. 
        The purpose of the pruning tables is to precompute the values of an admissible heuristic function,
        in order to allow for efficient pruning of the IDA* search tree through the use of a lookup table. --> see solver.py
        Args:
            pruning_coordinates (Tuple[str, str]): Coordinate pair to index table with.
            allowed_move (List[Move]): Set of allowed moves for stage. ie: g1 or g2. 
            table_size (int): Maximum pruning table size. 

        Returns:
            dict: Pruning table.
        '''
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
                next_state.move(move)  # Apply move

                next_coord_tuple = (
                    getattr(next_state, pruning_coordinate_1),
                    getattr(next_state, pruning_coordinate_2)
                )

                if next_coord_tuple not in visited:
                    queue.append((next_state, depth + 1))

        return general_table
    
    def generate_UD_slice_corner_table(self):
        '''Generates UD slice coordinate and corner orientation coordinate pruning table for g1 heuristic.
        (2048 * 485 entries)
        Returns:
            dict: udslice_corner pruning table
        '''
        return self.generate_general_pruning_table(('UD_slice_coordinate','corner_orientation_coordinate'), Data.g1_allowed_moves, 2048 * 495)
    
    def generate_UD_slice_edge_table(self):
        '''Generates UD slice coordinate and edge orientation coordinate pruning table for g1 heuristic.
        (2187 * 495 entries)
        Returns:
            dict: udslice_edge pruning table
        '''
        return self.generate_general_pruning_table(('UD_slice_coordinate', 'edge_orientation_coordinate'), Data.g1_allowed_moves, 2187 * 495)
    
    def generate_corner_four_edge_table(self):
        '''Generates corner permutation coordinate and four edge permutation coordinate pruning table for g2 heuristic.
        (40320 * 24 entries)
        Returns:
            dict: corner_udslice_edge pruning table
        '''
        return self.generate_general_pruning_table(('corner_permutation_coordinate', 'four_edge_permutation_coordinate'), Data.g2_allowed_moves, 40320 * 24)
    
    def generate_eight_edge_four_edge_table(self):
        '''Generates eight edge permutation coordinate and four edge permutation coordinate pruning table for g2 heuristic.
        (40320 * 24 entries)
        Returns:
            dict: mainedge_udslice_edge pruning table
        '''
        return self.generate_general_pruning_table(('eight_edge_permutation_coordinate', 'four_edge_permutation_coordinate'), Data.g2_allowed_moves, 40320 * 24)

if __name__ == '__main__':
    pruning_tables = PruningTableGenerator()
    pruning_tables.parallel_table_generation()
else:
    pruning_tables = PruningTableGenerator()

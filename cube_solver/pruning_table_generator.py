import json
import multiprocessing
import os
from collections import deque
from datetime import datetime

from . import cube
cube.import_tables()
from .data import Data
from .paths import PRUNING_TABLES_DIR

class PruningTableGenerator:
    '''Generates and saves the pruning table files used as admissible heuristics by the IDA*
    search in solver.py.
    '''
    def __init__(self):
        self.__path_function_pairs = [
            (PRUNING_TABLES_DIR / 'UD_slice_corner_table.json', self.generate_UD_slice_corner_table),
            (PRUNING_TABLES_DIR / 'UD_slice_edge_table.json', self.generate_UD_slice_edge_table),
            (PRUNING_TABLES_DIR / 'corner_four_edge_table.json', self.generate_corner_four_edge_table),
            (PRUNING_TABLES_DIR / 'eight_edge_four_edge_table.json', self.generate_eight_edge_four_edge_table)
        ]

    def generate_table(self, path, generating_function):
        '''Calls generating_function and saves its output to path as JSON.'''
        table = generating_function()
        with open(path, 'w') as file:
            json.dump(table, file, indent=4)

    def parallel_table_generation(self):
        '''Generates and saves each table not already present on disk, one process per table
        (this is what makes generation fast enough to run at startup).
        '''
        print('Generating pruning tables...')
        start_time = datetime.now()

        PRUNING_TABLES_DIR.mkdir(parents=True, exist_ok=True)
        processes = []
        for path, function in self.__path_function_pairs:
            if os.path.exists(path):
                continue  # Skip existing tables.
            process = multiprocessing.Process(target=self.generate_table, args=(path, function))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

        print(f"Time to generate: {datetime.now() - start_time}")

    def generate_general_pruning_table(self, pruning_coordinates, allowed_moves, dim2, table_size):
        '''Builds one pruning table by breadth-first search outward from the solved state: for
        every reachable (coordinate_1, coordinate_2) pair, the minimum number of moves to reach it,
        which is an admissible heuristic for the number of moves needed to solve back to it.

        Args:
            pruning_coordinates (Tuple[str, str]): the pair of CoordCube coordinates to index by.
            allowed_moves (List[Move]): moves allowed for this stage (g1 or g2).
            dim2 (int): number of distinct values coordinate_2 can take, used to flatten the pair
                into a single index: coordinate_1 * dim2 + coordinate_2.
            table_size (int): size of the table (dim1 * dim2).

        Returns:
            list: table indexed by coordinate_1 * dim2 + coordinate_2.
        '''
        pruning_coordinate_1, pruning_coordinate_2 = pruning_coordinates
        general_table = [None] * table_size
        initial_state = cube.CoordCube()  # Solved cube: all coordinates 0.

        queue = deque([(initial_state, 0)])  # (cube_state, depth)
        visited = set()

        while queue and len(visited) < table_size:
            current_state, depth = queue.popleft()
            index = (
                getattr(current_state, pruning_coordinate_1) * dim2
                + getattr(current_state, pruning_coordinate_2)
            )

            if index in visited:
                continue

            visited.add(index)
            general_table[index] = depth

            for move in allowed_moves:
                next_state = cube.CoordCube(current_state)
                next_state.move(move)

                next_index = (
                    getattr(next_state, pruning_coordinate_1) * dim2
                    + getattr(next_state, pruning_coordinate_2)
                )

                if next_index not in visited:
                    queue.append((next_state, depth + 1))

        return general_table

    def generate_UD_slice_corner_table(self):
        '''Generates the UD slice / corner orientation pruning table for the g1 heuristic (495 * 2187 entries).'''
        return self.generate_general_pruning_table(('UD_slice_coordinate', 'corner_orientation_coordinate'), Data.g1_allowed_moves, 2187, 495 * 2187)

    def generate_UD_slice_edge_table(self):
        '''Generates the UD slice / edge orientation pruning table for the g1 heuristic (495 * 2048 entries).'''
        return self.generate_general_pruning_table(('UD_slice_coordinate', 'edge_orientation_coordinate'), Data.g1_allowed_moves, 2048, 495 * 2048)

    def generate_corner_four_edge_table(self):
        '''Generates the corner / four-edge permutation pruning table for the g2 heuristic (40320 * 24 entries).'''
        return self.generate_general_pruning_table(('corner_permutation_coordinate', 'four_edge_permutation_coordinate'), Data.g2_allowed_moves, 24, 40320 * 24)

    def generate_eight_edge_four_edge_table(self):
        '''Generates the eight-edge / four-edge permutation pruning table for the g2 heuristic (40320 * 24 entries).'''
        return self.generate_general_pruning_table(('eight_edge_permutation_coordinate', 'four_edge_permutation_coordinate'), Data.g2_allowed_moves, 24, 40320 * 24)

if __name__ == '__main__':
    pruning_tables = PruningTableGenerator()
    pruning_tables.parallel_table_generation()
else:
    pruning_tables = PruningTableGenerator()

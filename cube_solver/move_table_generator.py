import itertools
import json
import os
from datetime import datetime

from . import cube
from .paths import MOVE_TABLES_DIR

class MoveTableGenerator:
    '''Generates and saves the move table files used by CoordCube to apply moves via lookup
    instead of simulating them on a CubieCube.
    '''
    def __init__(self):
        self.__path_function_pairs = [
            (MOVE_TABLES_DIR / "corner_orientation_table.json", self.__generate_corner_orientation_table),
            (MOVE_TABLES_DIR / "edge_orientation_table.json", self.__generate_edge_orientation_table),
            (MOVE_TABLES_DIR / "UD_slice_permutation_table.json", self.__generate_UD_slice_permutation_table),
            (MOVE_TABLES_DIR / "corner_permutation_table.json", self.__generate_corner_permutation_table),
            (MOVE_TABLES_DIR / "eight_edge_permutation_table.json", self.__generate_eight_edge_permutation_table),
            (MOVE_TABLES_DIR / "four_edge_permutation_table.json", self.__generate_four_edge_permutation_table),
        ]

    def move_table_generation(self):
        '''Generates and saves each table that isn't already present on disk.'''
        print('Generating move tables...')
        start_time = datetime.now()

        MOVE_TABLES_DIR.mkdir(parents=True, exist_ok=True)
        for path, function in self.__path_function_pairs:
            if os.path.exists(path):
                continue  # Skip existing tables.
            table = function()
            with open(path, 'w') as file:
                json.dump(table, file, indent=4)
        print(f"Time to generate: {datetime.now() - start_time}")

    def __decimal_to_ternary(self, n, digits=8):
        '''Converts n to a ternary number, zero-padded to digits.

        Returns:
            List[int]: ternary digits, most significant first.
        '''
        if n == 0:
            return [0] * digits
        ternary = []
        while n > 0:
            ternary.insert(0, n % 3)
            n //= 3
        return [0] * (digits - len(ternary)) + ternary

    def __decimal_to_binary(self, n, bits=12):
        '''Converts n to a binary number, zero-padded to bits.

        Returns:
            List[int]: binary digits, most significant first.
        '''
        if n == 0:
            return [0] * bits
        binary = []
        while n > 0:
            binary.insert(0, n % 2)
            n //= 2
        return [0] * (bits - len(binary)) + binary

    def __generate_general_table(self, iterator, coordinate_type, configuration_type, table_size):
        '''Builds one move table: for every possible value of a coordinate, the resulting
        coordinate after each of the 18 moves.

        Args:
            iterator (Iterable): yields every possible value of the CubieCube attribute
                configuration_type, one per coordinate value.
            coordinate_type (str): CoordCube coordinate property to read.
            configuration_type (str): CubieCube attribute the iterator produces values for.
            table_size (int): number of distinct coordinate values (size of the table).

        Returns:
            list: table indexed by coordinate, each entry a list of 18 resulting coordinates (one per move).
        '''
        general_table = [None] * table_size

        for configuration_component in iterator:
            parent_cube = cube.CubieCube()
            setattr(parent_cube, configuration_type, configuration_component)
            parent_general_coordinate = getattr(cube.CoordCube(parent_cube), coordinate_type)

            child_general_coordinates = [''] * 18
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.R, cube.Move.B, cube.Move.D]:
                temp_cube = cube.CubieCube()
                setattr(temp_cube, configuration_type, configuration_component)
                for turns in range(3):
                    temp_cube.move(move_type)
                    child_coordinate = getattr(cube.CoordCube(temp_cube), coordinate_type)
                    child_general_coordinates[move_type + 6 * turns] = child_coordinate

            general_table[parent_general_coordinate] = child_general_coordinates
        return general_table

    def __generate_corner_orientation_table(self):
        '''Generates the corner orientation table (2187 entries).'''
        def iterator():
            for generating_orientation_coordinate in range(3 ** 7):
                ternary_form = self.__decimal_to_ternary(generating_orientation_coordinate, digits=7)
                yield ternary_form + [(-sum(ternary_form)) % 3]  # 8th corner makes the total divisible by 3.
        return self.__generate_general_table(iterator(), 'corner_orientation_coordinate', 'corner_orientations', 2187)

    def __generate_edge_orientation_table(self):
        '''Generates the edge orientation table (2048 entries).'''
        def iterator():
            for generating_orientation_coordinate in range(2 ** 11):
                binary_form = self.__decimal_to_binary(generating_orientation_coordinate, bits=11)
                yield binary_form + [sum(binary_form) % 2]  # 12th edge makes the total even.
        return self.__generate_general_table(iterator(), 'edge_orientation_coordinate', 'edge_orientations', 2048)

    def __generate_UD_slice_permutation_table(self):
        '''Generates the UD slice permutation table (495 entries).'''
        def iterator():
            for index_combination in itertools.combinations(range(12), 4):
                cubie_UD_permutations = [0] * 12
                for i, index in enumerate(index_combination):
                    cubie_UD_permutations[index] = [8, 9, 10, 11][i]
                counter = 0
                for i in range(12):
                    if cubie_UD_permutations[i] == 0:
                        cubie_UD_permutations[i] = counter
                        counter += 1
                yield cubie_UD_permutations
        return self.__generate_general_table(iterator(), 'UD_slice_coordinate', 'edge_permutations', 495)

    def __generate_corner_permutation_table(self):
        '''Generates the corner permutation table (40320 entries).'''
        def iterator():
            yield from itertools.permutations(range(8), 8)
        return self.__generate_general_table(iterator(), 'corner_permutation_coordinate', 'corner_permutations', 40320)

    def __generate_eight_edge_permutation_table(self):
        '''Generates the eight (non-UD-slice) edge permutation table (40320 entries).'''
        def iterator():
            for main_edge_combination in itertools.permutations(range(8), 8):
                yield list(main_edge_combination) + [8, 9, 10, 11]  # UD slice edges fixed.
        return self.__generate_general_table(iterator(), 'eight_edge_permutation_coordinate', 'edge_permutations', 40320)

    def __generate_four_edge_permutation_table(self):
        '''Generates the four UD slice edge permutation table (24 entries).'''
        def iterator():
            for UD_slice_combination in itertools.permutations(range(8, 12), 4):
                yield list(range(8)) + list(UD_slice_combination)  # Main edges fixed.
        return self.__generate_general_table(iterator(), 'four_edge_permutation_coordinate', 'edge_permutations', 24)

if __name__ == '__main__':
    move_tables = MoveTableGenerator()
    move_tables.move_table_generation()
else:
    move_tables = MoveTableGenerator()

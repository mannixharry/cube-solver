import os 
import json
import itertools
from data import * 
from datetime import datetime 
import cube

class MoveTableGenerator:
    '''Generates and saves move table files. 
    '''
    def __init__(self):
        '''Defines path_function_pairs dictionary. 
        '''
        self.__path_function_pairs = [
            ("move_tables/corner_orientation_table.json", self.__generate_corner_orientation_table),
            ("move_tables/edge_orientation_table.json", self.__generate_edge_orientation_table),
            ("move_tables/UD_slice_permutation_table.json", self.__generate_UD_slice_permutation_table),
            ("move_tables/corner_permutation_table.json", self.__generate_corner_permutation_table),
            ("move_tables/eight_edge_permutation_table.json", self.__generate_eight_edge_permutation_table),
            ("move_tables/four_edge_permutation_table.json", self.__generate_four_edge_permutation_table),
        ]
    
    def move_table_generation(self):
        '''Calls generating function for each table that is not present, and saves output.
        '''
        print('Generating move tables...')
        start_time = datetime.now()
     
        for path, function in self.__path_function_pairs:
            if os.path.exists(path):
                continue # skip existing tables
            table = function()
            with open(path, 'w') as file:
                json.dump(table, file, indent=4)
        print(f"Time to generate: {datetime.now() - start_time}")
        
                 
    def __decimal_to_ternary(self, n, digits=8):
        '''Converts from a decimal number to a ternary number. 

        Args:
            n (int): decimal input
            digits (int, optional): number of digits in output. Defaults to 8.

        Returns:
            List[int]: ternary number.
        '''
        if n == 0:
            return [0] * digits
        ternary = []
        while n > 0:
            ternary.insert(0, n % 3)
            n //= 3
        return [0] * (digits - len(ternary)) + ternary  # Pad with 0's to the required bit length

    def __decimal_to_binary(self, n, bits=12):
        '''Converts from a decimal number to a binary number. 

        Args:
            n (int): decimal input
            bits (int, optional): number of digits in output. Defaults to 8.

        Returns:
            List[int]: binary number.
        '''
        if n == 0:
            return [0] * bits
        binary = []
        while n > 0:
            binary.insert(0, n % 2)
            n //= 2
        return [0] * (bits - len(binary)) + binary  # Pad with 0's to the required bit length

    def __generate_general_table(self, iterator, coordinate_type, configuration_type, table_size):
        '''Generates a move table, taking an iterator function, coordinate_type and configuration_type as input.
        The purpose of the move tables are to act as a look up for applying moves to a CoordCube representation.
        Rather than converting the representation to a CubieCube, peforming a turn, and converting back,
        the result of every possible move on every possible coordinate for every type of coordinate
        is stored in move tables.

        Args:
            iterator (function): Generator function to iterate over all possible coordinates.
            coordinate_type (str): Coordinate attribute of interest.
            configuration_type (str): CubieCube attribute of interest.
            table_size (int): Number of distinct values the coordinate can take (size of the array).

        Returns:
            list: Move table. Indexed by coordinate, each entry is a list of 18 child coordinates (one per move).
        '''
        general_table = [None] * table_size

        for configuration_component in iterator:

            parent_cube = cube.CubieCube()
            setattr(parent_cube, configuration_type, configuration_component)
            parent_general_coordinate = getattr(cube.CoordCube(parent_cube), coordinate_type)

            child_general_coordinates = [''] * 18 # Placeholder for 18 moves.
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.R, cube.Move.B, cube.Move.D]:

                temp_cube = cube.CubieCube()
                setattr(temp_cube, configuration_type, configuration_component)
                for turns in range(3):
                    temp_cube.move(move_type)
                    child_coordinate = getattr(cube.CoordCube(temp_cube), coordinate_type)
                    child_general_coordinates[move_type + 6*turns] = child_coordinate

            general_table[parent_general_coordinate] = child_general_coordinates
        return general_table
    
    def __generate_corner_orientation_table(self):
        '''Generates the corner orientation table.
        (2187 entries)
        '''
        def iterator():
            '''Iterates over corner orientation coordinates.

            Yields:
                List[int]: corner_orientations.
            '''
            for generating_orientation_coordinate in range(3**7):  # Iterate over the first 7 corners
                ternary_form = self.__decimal_to_ternary(generating_orientation_coordinate, digits=7)
                # Compute the 8th corner orientation to make the total sum divisible by 3
                yield ternary_form + [(-sum(ternary_form)) % 3]  # Ensure valid corner orientation
        itr = iterator()
        return self.__generate_general_table(itr, 'corner_orientation_coordinate', 'corner_orientations', 2187)

    def __generate_edge_orientation_table(self):
        '''Generates the edge orientation table.
        (2048 entries)
        '''
        def iterator():
            '''Iterates over edge orientation coordinates. 

            Yields:
                List[int]: edge_orientations
            '''
            for generating_orientation_coordinate in range(2**11):  # Iterate over the first 11 edges
                binary_form = self.__decimal_to_binary(generating_orientation_coordinate, bits=11)
                # Compute the 12th edge flip to make the total sum even
                yield binary_form + [(sum(binary_form) % 2)]  # Add the parity bit to enforce valid edge orientation
        itr = iterator()
        return self.__generate_general_table(itr, 'edge_orientation_coordinate', 'edge_orientations', 2048)

    def __generate_UD_slice_permutation_table(self):
        '''Generates the UD slice permutation table. 
        (495 entries)
        '''
        def iterator():
            '''Iterates over UD slice permutation coordinates. 

            Yields:
                List[int]: edge_permutations
            '''
            indices = itertools.combinations(range(12), 4)

            for index_combination in indices:
                cubie_UD_permutations = [0] * 12
                for i, index in enumerate(index_combination):
                    cubie_UD_permutations[index] = [8,9,10,11][i]
                counter = 0 
                for i in range(12):
                    if cubie_UD_permutations[i] == 0:
                        cubie_UD_permutations[i] = counter
                        counter += 1 
                yield cubie_UD_permutations
        itr = iterator()
        return self.__generate_general_table(itr, 'UD_slice_coordinate', 'edge_permutations', 495)
   
    def __generate_corner_permutation_table(self):
        '''Generates the corner permutation table.
        (40320 entries)
        '''
        def iterator():
            '''Iterates over corner permutation coordinates. 

            Yields:
                List[int]: corner_permutations
            '''
            indices = list(itertools.permutations(list(range(8)), 8)) # All possible ways of picking 8 items from a list of 8 where order matters
            for index_combination in indices:
                yield index_combination
        itr = iterator()
        return self.__generate_general_table(itr, 'corner_permutation_coordinate', 'corner_permutations', 40320)
    

    def __generate_eight_edge_permutation_table(self):
        '''Generates the eight edge permutation table.
        (40320 entries)
        '''
        def iterator():
            '''Iterates over eight edge permutation coordinates.

            Yields:
                List[int]: edge_permutations
            '''
            indices = list(itertools.permutations(range(8), 8))  # All possible arrangements of the 8 main edges
            for main_edge_combination in indices:
                # Set up the cubie cube with the specific main edge permutation
                yield list(main_edge_combination) + [8, 9, 10, 11]  # Fixed UD edges
        itr = iterator()
        return self.__generate_general_table(itr, 'eight_edge_permutation_coordinate', 'edge_permutations', 40320)

    def __generate_four_edge_permutation_table(self):
        '''Generates the four edge permutation table.
        (24 entries)
        '''
        def iterator():
            '''Iterates over four edge permutation coordinates.

            Yields:
                List[int]: edge_permutations
            '''
            indices = list(itertools.permutations(range(8, 12), 4))  # All possible arrangements of the 4 UD slice edges        
            for UD_slice_combination in indices:
                # Set up the cubie cube with the specific UD slice edge permutation
                yield list(range(8)) + list(UD_slice_combination)  # Fixed main edges
        itr = iterator()
        return self.__generate_general_table(itr, 'four_edge_permutation_coordinate', 'edge_permutations', 24)
            
if __name__ == '__main__':
    move_tables = MoveTableGenerator()
    move_tables.move_table_generation()
else:
    move_tables = MoveTableGenerator()

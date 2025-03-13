import os 
import json
import itertools
import cube 
from data import * 
from datetime import datetime 

class MoveTableGenerator:
     
    def __init__(self, regenerate_tables=False):
        # Define the directory where the tables will be saved
        tables_directory = os.path.join(os.path.dirname(__file__), 'move_tables')
        
        # Define all tables with their respective file paths and generation methods
        tables = {
            "corner_orientation_table": ("corner_orientation_table.json", self.generate_corner_orientation_table),
            "edge_orientation_table": ("edge_orientation_table.json", self.generate_edge_orientation_table),
            "UD_slice_table": ("UD_slice_permutation_table.json", self.generate_UD_slice_permutation_table),
            "corner_permutation_table": ("corner_permutation_table.json", self.generate_corner_permutation_table),
            "eight_edge_permutation_table": ("eight_edge_permutation_table.json", self.generate_eight_edge_permutation_table),
            "four_edge_permutation_table": ("four_edge_permutation_table.json", self.generate_four_edge_permutation_table),
        }

        # Check if regeneration is required or the files already exist
        for table_name, (filename, generation_method) in tables.items():
            filepath = os.path.join(tables_directory, filename)  # Path within the tables directory
            if regenerate_tables or not os.path.isfile(filepath):
                # Generate and save the table if regeneration is forced or file doesn't exist
                data = generation_method()
                sorted_data = {k: data[k] for k in sorted(data)}
                with open(filepath, 'w') as file:
                    json.dump(sorted_data, file, indent=4)

    def decimal_to_ternary(self, n, bits=8):
        if n == 0:
            return [0] * bits
        ternary = []
        while n > 0:
            ternary.insert(0, n % 3)
            n //= 3
        return [0] * (bits - len(ternary)) + ternary  # Pad with 0's to the required bit length

    
    def decimal_to_binary(self, n, bits=12):
        if n == 0:
            return [0] * bits
        binary = []
        while n > 0:
            binary.insert(0, n % 2)
            n //= 2
        return [0] * (bits - len(binary)) + binary  # Pad with 0's to the required bit length

    
    def generate_general_table(self, iterator, coordinate_type, configuration_type):
        general_table = {}

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
    
    def generate_corner_orientation_table(self):
        def iterator():
            for generating_orientation_coordinate in range(3**7):  # Iterate over the first 7 corners
                ternary_form = self.decimal_to_ternary(generating_orientation_coordinate, bits=7)
                # Compute the 8th corner orientation to make the total sum divisible by 3
                yield ternary_form + [(-sum(ternary_form)) % 3]  # Ensure valid corner orientation
        itr = iterator()
        return self.generate_general_table(itr, 'corner_orientation_coordinate', 'corner_orientations')

    def generate_edge_orientation_table(self):
        def iterator():
            for generating_orientation_coordinate in range(2**11):  # Iterate over the first 11 edges
                binary_form = self.decimal_to_binary(generating_orientation_coordinate, bits=11)
                # Compute the 12th edge flip to make the total sum even
                yield binary_form + [(sum(binary_form) % 2)]  # Add the parity bit to enforce valid edge orientation
        itr = iterator()
        return self.generate_general_table(itr, 'edge_orientation_coordinate', 'edge_orientations')

    def generate_UD_slice_permutation_table(self):
        def iterator():
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
        return self.generate_general_table(itr, 'UD_slice_coordinate', 'edge_permutations')
   
    def generate_corner_permutation_table(self):
        def iterator():
            indices = list(itertools.permutations(list(range(8)), 8)) # All possible ways of picking 8 items from a list of 8 where order matters
            for index_combination in indices:
                yield index_combination
        itr = iterator()
        return self.generate_general_table(itr, 'corner_permutation_coordinate', 'corner_permutations')
    

    def generate_eight_edge_permutation_table(self):
        def iterator():
            indices = list(itertools.permutations(range(8), 8))  # All possible arrangements of the 8 main edges
            for main_edge_combination in indices:
                # Set up the cubie cube with the specific main edge permutation
                yield list(main_edge_combination) + [8, 9, 10, 11]  # Fixed UD edges
        itr = iterator()
        return self.generate_general_table(itr, 'eight_edge_permutation_coordinate', 'edge_permutations')

    def generate_four_edge_permutation_table(self):
        def iterator():
            indices = list(itertools.permutations(range(8, 12), 4))  # All possible arrangements of the 4 UD slice edges        
            for UD_slice_combination in indices:
                # Set up the cubie cube with the specific UD slice edge permutation
                yield list(range(8)) + list(UD_slice_combination)  # Fixed main edges
        itr = iterator()
        return self.generate_general_table(itr, 'four_edge_permutation_coordinate', 'edge_permutations')
            
class Move_Tables:

    def load(self):
        with open('move_tables/corner_orientation_table.json', 'r') as file:
            self.corner_orientation_table = json.load(file)
        with open('move_tables/edge_orientation_table.json', 'r') as file:
            self.edge_orientation_table = json.load(file)
        with open('move_tables/UD_slice_permutation_table.json', 'r') as file:
            self.UD_slice_permutation_table = json.load(file)
        with open('move_tables/four_edge_permutation_table.json', 'r') as file:
            self.four_edge_permutation_table = json.load(file)
        with open('move_tables/eight_edge_permutation_table.json', 'r') as file:
            self.eight_edge_permutation_table = json.load(file)
        with open('move_tables/corner_permutation_table.json', 'r') as file:
            self.corner_permutation_table = json.load(file)
    def __init__(self):
        try: 
            self.load()
        except: 
            print('Generating move tables...')
            start_time = datetime.now()
            MoveTableGenerator(regenerate_tables=True)
            print('Move table generation complete')
            print(f"Time to generate: {datetime.now() - start_time}")
            
            self.load()

if __name__ == '__main__':
    print('Generating move tables...')
    move_tables = MoveTableGenerator(regenerate_tables=True)
    print('Move table generation complete')
else:
    move_tables = Move_Tables()
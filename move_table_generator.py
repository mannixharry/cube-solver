import os 
import json
import itertools
import cube 

class MoveTableGenerator:
     
    def __init__(self, regenerate_tables=False):
        # Define the directory where the tables will be saved
        tables_dir = os.path.join(os.path.dirname(__file__), 'move_tables')
        os.makedirs(tables_dir, exist_ok=True)  # Ensure the directory exists

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
            filepath = os.path.join(tables_dir, filename)  # Path within the tables directory
            if regenerate_tables or not os.path.isfile(filepath):
                # Generate and save the table if regeneration is forced or file doesn't exist
                data = generation_method()
                sorted_data = {k: data[k] for k in sorted(data)}
                with open(filepath, 'w') as file:
                    json.dump(sorted_data, file, indent=4)

    def decimal_to_ternary(self, n):
        if n == 0:
            return [0] * 7
        ternary = []
        while n > 0: 
            ternary.insert(0,n%3)
            n //= 3
        return [0] * (7-len(ternary)) + ternary # Pad with 0's
    
    def decimal_to_binary(self, n):
        if n == 0:
            return [0] * 11
        binary = []
        while n > 0:
            binary.insert(0, n%2)
            n //= 2
        return [0] * (11-len(binary)) + binary
    
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
            for generating_orientation_coordinate in range(3**7):
                ternary_form = self.decimal_to_ternary(generating_orientation_coordinate)
                yield ternary_form + [-sum(ternary_form)%3] # Add a number to make the sum divisible by three (to have a valid orientation).
        itr = iterator()
        return self.generate_general_table(itr, 'corner_orientation_coordinate', 'corner_orientations')
    
    
    def generate_edge_orientation_table(self):
        def iterator():
            for generating_orientation_coordinate in range(3**7):
                binary_form = self.decimal_to_binary(generating_orientation_coordinate)
                yield binary_form + [-sum(binary_form)%2] # Add a number to make the sum divisible by two (to have a valid orientation).
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
            
if __name__ == '__main__':
    print('Generating move tables...')
    move_tables = MoveTableGenerator(regenerate_tables=True)
    print('Move table generation complete')

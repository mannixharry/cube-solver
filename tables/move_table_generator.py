import os 
import json
import itertools
import cube 

class MoveTableGenerator:
    def __init__(self, regenerate_tables=False):
        # Define all tables with their respective file paths and generation methods
        tables = {
            "corner_orientation_table": ("corner_orientation_table.json", self.generate_corner_orientation_table),
            "edge_orientation_table": ("edge_orientation_table.json", self.generate_edge_orientation_table),
            "UD_slice_table": ("UD_slice_permutation_table.json", self.generate_UD_slice_permutation_table),
            "corner_permutation_table": ("corner_permutation_table.json", self.generate_corner_permutation_table),
            "main_edge_permutation_table": ("main_edge_permutation_table.json", self.generate_main_edge_permutation_table),
            "UD_slice_edge_permutation_table": ("UD_slice_edge_permutation_table.json", self.generate_UD_slice_edge_permutation_table),
        }

        # Check if regeneration is required or the files already exist
        for table_name, (filename, generation_method) in tables.items():
            if regenerate_tables or not os.path.isfile(filename):
                # Generate and save the table if regeneration is forced or file doesn't exist
                data = generation_method()
                sorted_data = {k: data[k] for k in sorted(data)}
                with open(filename, 'w') as file:
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

    def generate_corner_orientation_table(self):
        
        corner_orientation_table = {}
        
        for generating_orientation_coordinate in range(3**7):
            ternary_form = self.decimal_to_ternary(generating_orientation_coordinate)
            cubie_corner_orientation = ternary_form + [-sum(ternary_form)%3] # Add a number to make the sum divisible by three (to have a valid orientation)
            
            parent_cube = cube.CubieCube()
            parent_cube.corner_orientations = cubie_corner_orientation
            
            parent_orientation_coordinate = cube.CoordCube(parent_cube).corner_orientation_coordinate

            child_orientation_coordinates = []
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.D, cube.Move.R, cube.Move.B]:
                
                base_cube = cube.CubieCube()
                base_cube.corner_orientations = cubie_corner_orientation
                for turns in range(3):
                    base_cube.rotate_clockwise(move_type)
                    child_coordinate = cube.CoordCube(base_cube).corner_orientation_coordinate
                    child_orientation_coordinates.append(child_coordinate)
                    
            corner_orientation_table[parent_orientation_coordinate] = child_orientation_coordinates
        
        return corner_orientation_table    
    
    def generate_edge_orientation_table(self):
        
        edge_orientation_table = {}
        
        for generating_orientation_coordinate in range(2**11):
            binary_form = self.decimal_to_binary(generating_orientation_coordinate)
            cubie_edge_orientation = binary_form + [-sum(binary_form)%2] # Add a number to make the sum divisible by two (to have a valid orientation)
            parent_cube = cube.CubieCube()
            parent_cube.edge_orientations = cubie_edge_orientation
            
            parent_orientation_coordinate = cube.CoordCube(parent_cube).edge_orientation_coordinate

            child_orientation_coordinates = []
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.D, cube.Move.R, cube.Move.B]:
                
                base_cube = cube.CubieCube()
                base_cube.edge_orientations = cubie_edge_orientation
                for turns in range(3):
                    base_cube.rotate_clockwise(move_type)
                    child_coordinate = cube.CoordCube(base_cube).edge_orientation_coordinate
                    child_orientation_coordinates.append(child_coordinate)
                    
            edge_orientation_table[parent_orientation_coordinate] = child_orientation_coordinates
        
        return edge_orientation_table   
    
    def generate_UD_slice_permutation_table(self):

        # UD slice is 8,9,10,11
        UD_slice_permutation_table = {}
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

            parent_cube = cube.CubieCube()
            parent_cube.edge_permutations = cubie_UD_permutations
            parent_UD_slice_coordinate = cube.CoordCube(parent_cube).UD_slice_coordinate
            print(parent_UD_slice_coordinate)

            child_UD_slice_coordinates = []
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.D, cube.Move.R, cube.Move.B]:

                base_cube = cube.CubieCube()
                base_cube.edge_permutations = cubie_UD_permutations
            
                for turns in range(3):
                    base_cube.rotate_clockwise(move_type)
                    child_coordinate = cube.CoordCube(base_cube).UD_slice_coordinate
                    child_UD_slice_coordinates.append(child_coordinate)
                    
            UD_slice_permutation_table[parent_UD_slice_coordinate] = child_UD_slice_coordinates
        
        return UD_slice_permutation_table
    
    def generate_corner_permutation_table(self):
        corner_permutation_table = {}
        indices = list(itertools.permutations(list(range(8)), 8)) # All possible ways of picking 8 items from a list of 8 where order matters
        print(indices)
        for index_combination in indices:
            cubie_corner_permutations = index_combination  
            parent_cube = cube.CubieCube()
            parent_cube.corner_permutations = cubie_corner_permutations
            parent_corner_permutation_coordinate = cube.CoordCube(parent_cube).calculate_corner_permutation_coordinate()
            print(parent_corner_permutation_coordinate)
            
            child_corner_permutation_coordinates = []
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.D, cube.Move.R, cube.Move.B]:
                base_cube = cube.CubieCube()
                base_cube.corner_permutations = cubie_corner_permutations
            
                for turns in range(3):
                    base_cube.rotate_clockwise(move_type)
                    child_coordinate = cube.CoordCube(base_cube).corner_permutation_coordinate
                    child_corner_permutation_coordinates.append(child_coordinate)
                    
            corner_permutation_table[parent_corner_permutation_coordinate] = child_corner_permutation_coordinates
        
        return corner_permutation_table
    
    def generate_main_edge_permutation_table(self):
        
        main_edge_permutation_table = {}
        indices = list(itertools.permutations(range(8), 8))  # All possible arrangements of the 8 main edges
        print(indices)
        
        for main_edge_combination in indices:
            # Set up the cubie cube with the specific main edge permutation
            cubie_main_edges = list(main_edge_combination) + [8, 9, 10, 11]  # Fixed UD edges
            
            parent_cube = cube.CubieCube()
            parent_cube.edge_permutations = cubie_main_edges
            
            # Calculate the coordinate for this main edge configuration
            parent_edge_permutation_coordinate = cube.CoordCube(parent_cube).calculate_main_edge_permutation_coordinate()
            print(parent_edge_permutation_coordinate)
            
            child_edge_permutation_coordinates = []
            
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.D, cube.Move.R, cube.Move.B]:
                # Create a new cube with the initial main edge configuration
                base_cube = cube.CubieCube()
                base_cube.edge_permutations = cubie_main_edges[:]
                
                for turns in range(3):  # Apply 1, 2, or 3 turns
                    base_cube.rotate_clockwise(move_type)
                    
                    # Calculate the new coordinate after the move
                    child_coordinate = cube.CoordCube(base_cube).main_edge_permutation_coordinate
                    child_edge_permutation_coordinates.append(child_coordinate)
            
            # Map the parent coordinate to the list of child coordinates
            main_edge_permutation_table[parent_edge_permutation_coordinate] = child_edge_permutation_coordinates
        
        return main_edge_permutation_table

    def generate_UD_slice_edge_permutation_table(self):
        UD_slice_edge_permutation_table = {}
        indices = list(itertools.permutations(range(8, 12), 4))  # All possible arrangements of the 4 UD slice edges
        print(indices)
        
        for UD_slice_combination in indices:
            # Set up the cubie cube with the specific UD slice edge permutation
            cubie_UD_edges = list(range(8)) + list(UD_slice_combination)  # Fixed main edges
            
            parent_cube = cube.CubieCube()
            parent_cube.edge_permutations = cubie_UD_edges
            
            # Calculate the coordinate for this UD slice configuration
            parent_UD_slice_edge_permutation_coordinate = cube.CoordCube(parent_cube).calculate_UD_slice_edge_permutation_coordinate()
            print(parent_UD_slice_edge_permutation_coordinate)
            
            child_UD_slice_edge_permutation_coordinates = []
            
            for move_type in [cube.Move.U, cube.Move.F, cube.Move.L, cube.Move.D, cube.Move.R, cube.Move.B]:
                # Create a new cube with the initial UD slice edge configuration
                base_cube = cube.CubieCube()
                base_cube.edge_permutations = cubie_UD_edges[:]
                
                for turns in range(3):  # Apply 1, 2, or 3 turns
                    base_cube.rotate_clockwise(move_type)
                    
                    # Calculate the new coordinate after the move
                    child_coordinate = cube.CoordCube(base_cube).UD_slice_edge_permutation_coordinate
                    child_UD_slice_edge_permutation_coordinates.append(child_coordinate)
            
            # Map the parent coordinate to the list of child coordinates
            UD_slice_edge_permutation_table[parent_UD_slice_edge_permutation_coordinate] = child_UD_slice_edge_permutation_coordinates
    
        return UD_slice_edge_permutation_table


move_tables = MoveTableGenerator(regenerate_tables=True)


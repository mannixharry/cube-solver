import os 
import json
import itertools
import cube 

class MoveTableGenerator:
    def __init__(self, regenerate_tables=False):
        
        generate_corner_orientation_table = True if os.path.isfile('corner_orientation_table') else False
        generate_edge_orientation_table = True if os.path.isfile('edge_orientation_table') else False
        generate_UD_slice_table = True if os.path.isfile('UD_slice_table') else False                
        
        if regenerate_tables == True:
            generate_corner_orientation_table = generate_edge_orientation_table = generate_UD_slice_table = False
        
        if not generate_corner_orientation_table:
            with open('corner_orientation_table.json', 'w') as corner_orientation_file:
                data = self.generate_corner_orientation_table()
                data =  {k: data[k] for k in sorted(data)}
                json.dump(data, corner_orientation_file, indent=4)

        if not generate_edge_orientation_table:
            with open('edge_orientation.json', 'w') as edge_orientation_file:
                data = self.generate_edge_orientation_table()
                data = {k: data[k] for k in sorted(data)}
                json.dump(data, edge_orientation_file, indent=4)

        if not generate_UD_slice_table:
            with open('UD_slice_permutation.json', 'w') as UD_slice_permutation_file:
                data = self.generate_UD_slice_permutation_table()
                data = {k: data[k] for k in sorted(data)}
                json.dump(data, UD_slice_permutation_file, indent=4)
  
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
            for move_type in [cube.Move.U, cube.Move.L, cube.Move.F, cube.Move.R, cube.Move.B, cube.Move.D]:
                
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
            for move_type in [cube.Move.U, cube.Move.L, cube.Move.F, cube.Move.R, cube.Move.B, cube.Move.D]:
                
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
            for move_type in [cube.Move.U, cube.Move.L, cube.Move.F, cube.Move.R, cube.Move.B, cube.Move.D]:

                base_cube = cube.CubieCube()
                base_cube.edge_permutations = cubie_UD_permutations
            
                for turns in range(3):
                    base_cube.rotate_clockwise(move_type)
                    child_coordinate = cube.CoordCube(base_cube).UD_slice_coordinate
                    child_UD_slice_coordinates.append(child_coordinate)
                    
            UD_slice_permutation_table[parent_UD_slice_coordinate] = child_UD_slice_coordinates
        
        return UD_slice_permutation_table

move_tables = MoveTableGenerator(regenerate_tables=True)


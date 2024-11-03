import os 
import json

import cube 


class MoveTableGenerator:
    def __init__(self, regenerate_tables=False):
        
        
        generate_corner_orientation_table = True if os.path.isfile('corner_orientation_table') else False
        generate_edge_orientation_table = True if os.path.isfile('edge_orientation_table') else False
        generate_UD_slice_table = True if os.path.isfile('UD_slice_table') else False                
        
        if regenerate_tables == True:
            generate_corner_orientation_table = generate_edge_orientation_table = generate_UD_slice_table = False
        
        if not generate_corner_orientation_table:
            with open('corner_orientation_table.json', 'w') as json_file:
                data = self.generate_corner_orientation_table()
                data =  {k: data[k] for k in sorted(data)}
                json.dump(data, json_file, indent=4)
         
    def decimal_to_ternary(self, n):
        if n == 0:
            return [0] * 7
        ternary = []
        while n > 0: 
            ternary.insert(0,n%3)
            n //= 3
        return [0] * (7-len(ternary)) + ternary # Pad with 0's

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
                    if parent_orientation_coordinate == 1521:
                        import main
                        main.main(str(cube.FaceletCube(parent_cube)))
                        print(parent_cube.corner_orientations)
                    child_coordinate = cube.CoordCube(base_cube).corner_orientation_coordinate
                    child_orientation_coordinates.append(child_coordinate)
                    
            corner_orientation_table[parent_orientation_coordinate] = child_orientation_coordinates
        
        return corner_orientation_table    
            

MoveTableGenerator = MoveTableGenerator(regenerate_tables=True)
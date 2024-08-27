class RubiksCube:
    def __init__(self):
       
        self.cube_string = list('WWWWWWWWWOOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY')

    def get_cube_string(self):
        return self.cube_string
                                    
    def __repr__(self):
        cube_string = self.cube_string
       
        return (f"               {cube_string[0:3]}\n"
                f"               {cube_string[3:6]}\n"
                f"               {cube_string[6:9]}\n"
                f"{cube_string[9:12]}{cube_string[18:21]}{cube_string[27:30]}{cube_string[36:39]}\n"
                f"{cube_string[12:15]}{cube_string[21:24]}{cube_string[30:33]}{cube_string[39:42]}\n"
                f"{cube_string[15:18]}{cube_string[24:27]}{cube_string[33:36]}{cube_string[42:45]}\n"
                f"               {cube_string[48:51]}\n"
                f"               {cube_string[45:48]}\n"
                f"               {cube_string[51:54]}\n")
    
class CubeRotations:

    def __init__(self):
        # Define the rotation tables for the edges around each face
        self.encoded_rotation_tables = {
            'U' : ['F0','F1', 'F2', 'L0', 'L1', 'L2', 'B0', 'B1', 'B2', 'R0', 'R1', 'R2'],
            'L' : ['F0', 'F3', 'F6', 'D0', 'D3', 'D6', 'B2', 'B5', 'B8', 'U0', 'U3', 'U6'],
            'F' : ['U6', 'U7', 'U8', 'R0', 'R3', 'R6', 'D2', 'D1', 'D0', 'L8', 'L5', 'L2'],
            'R' : ['F2', 'F5', 'F8', 'U2', 'U5', 'U8', 'B6', 'B3', 'B0', 'D2', 'D5', 'D8'],
            'B' : ['U0', 'U1', 'U2', 'L0', 'L3', 'L6', 'D6', 'D7', 'D8', 'R8', 'R5', 'R2'],
            'D' : ['F6', 'F7', 'F8', 'R6', 'R7', 'R8', 'B6', 'B7', 'B8', 'L6', 'L7', 'L8']


        }
        self.rotation_tables = {key: ['ULFRBD'.index(i[0])*9 + int(i[1]) for i in value] for (key, value) in self.encoded_rotation_tables.items()}
        
        #print(self.encoded_rotation_tables)
        #print(self.rotation_tables)
        
    def rotate(self, cube, face, is_clockwise=True):
        # Rotate the face itself, then rotate edges around the face 
        self._rotate_face(cube, face, is_clockwise)
        self._rotate_edges(cube, face, is_clockwise)
        
    def _rotate_face(self, cube, face, clockwise=True):
        face_start = 'ULFRBD'.index(face) * 9
        facelet_indices = [6, 3, 0, 7, 4, 1, 8, 5, 2]

        if clockwise:
            # Shift the facelet positions clockwise
            new_face = [cube.cube_string[face_start + facelet_indices[i]] for i in range(9)]
        else:
            # Shift the facelet positions anticlockwise
            new_face = [cube.cube_string[face_start + facelet_indices[i]] for i in range(9)]
            
        for i in range(9):
            cube.cube_string[face_start + i] = new_face[i]

    def _rotate_edges (self, cube, face, clockwise = True):
        rotation_table = self.rotation_tables[face]
        new_cube = cube.cube_string[:] #creates a new list rather than creating a reference
        if clockwise:
            for i, index in enumerate(rotation_table):
                new_cube[rotation_table[(i+3)%12]] = cube.cube_string[index]
                print(f"{index} ==> {rotation_table[(i+3)%12]}")
        else: 
            for i, index in enumerate(rotation_table):
                new_cube[index] = cube.cube_string[rotation_table[(i+3)%12]]
                print(f"{index} <== {rotation_table[(i+3)%12]}")
                
            
        for i in range(54):
            cube.cube_string[i] = new_cube[i]
        
                
def main():

    cube = RubiksCube()
    # Instantiate the rotation logic
    rotator = CubeRotations()

    rotator.rotate(cube, 'D')
    print(cube)
    print(cube.cube_string)
    engine.main(cube.cube_string)


import engine 

if __name__ == "__main__":
    main()
    
# take the colours on the face and rotate them clockwise
# cycle the edges in threes 
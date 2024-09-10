
from enum import IntEnum
import math 
import json

class Corner(IntEnum):
    UFL = 0  # Upper Front Left
    UFR = 1  # Upper Front Right
    UBL = 2  # Upper Back Left
    UBR = 3  # Upper Back Right
    DFL = 4  # Down Front Left
    DFR = 5  # Down Front Right
    DBL = 6  # Down Back Left
    DBR = 7  # Down Back Right

class Edge(IntEnum):
    UF = 0  # Upper Front
    UL = 1  # Upper Left
    UB = 2  # Upper Back
    UR = 3  # Upper Right
    DF = 4  # Down Front
    DL = 5  # Down Left
    DB = 6  # Down Back
    DR = 7  # Down Right
    FL = 8  # Front Left
    FR = 9  # Front Right
    BL = 10 # Back Left
    BR = 11 # Back Right

class Move(IntEnum):
    U = 0
    F = 1
    L = 2
    D = 3
    R = 4
    B = 5

class Facelet(IntEnum):
    #ULFRBD
    U0 = 0
    U1 = 1
    U2 = 2
    U3 = 3
    U4 = 4
    U5 = 5
    U6 = 6
    U7 = 7
    U8 = 8
    L0 = 9
    L1 = 10
    L2 = 11
    L3 = 12
    L4 = 13
    L5 = 14
    L6 = 15
    L7 = 16
    L8 = 17
    F0 = 18
    F1 = 19
    F2 = 20
    F3 = 21
    F4 = 22
    F5 = 23
    F6 = 24
    F7 = 25
    F8 = 26
    R0 = 27
    R1 = 28
    R2 = 29
    R3 = 30
    R4 = 31
    R5 = 32
    R6 = 33
    R7 = 34
    R8 = 35
    B0 = 36
    B1 = 37
    B2 = 38
    B3 = 39
    B4 = 40
    B5 = 41
    B6 = 42
    B7 = 43
    B8 = 44
    D0 = 45
    D1 = 46
    D2 = 47
    D3 = 48
    D4 = 49
    D5 = 50
    D6 = 51
    D7 = 52
    D8 = 53




class CubieCube:
    def __init__(self):
        #Initialize in solved position

        self.corner_permutations = [0,1,2,3,4,5,6,7] 
        self.corner_orientations = [0,0,0,0,0,0,0,0] 

        self.edge_permutations = [0,1,2,3,4,5,6,7,8,9,10,11]
        self.edge_orientations = [0,0,0,0,0,0,0,0,0,0,0,0]

        self.corner_permutation_tables = {
            Move.U : [1, 3, 0, 2, 4, 5, 6, 7],  # UFR -> UFL, UBR -> UFR, UFL -> UBL, UBL -> UBR
            Move.F : [4, 0, 2, 3, 5, 1, 6, 7],  # UFL -> DFL, UFR -> UFL, DFR -> UFR, DFL -> DFR
            Move.L : [2, 1, 6, 3, 0, 5, 4, 7],  # UFL -> DFL, DFL -> DBL, DBL -> UBL, UBL -> UFL
            Move.D : [0, 1, 2, 3, 6, 4, 7, 5],  # DFR -> DBR, DBR -> DBL, DBL -> DFL, DFL -> DFR 
            Move.R : [0, 5, 2, 1, 4, 7, 6, 3],  # DFR -> UFR, UFR -> UBR, UBR -> DBR, DBR -> DFR
            Move.B : [0, 1, 3, 7, 4, 5, 2, 6],  # UBR -> UBL, UBL -> DBL, DBL -> DBR, DBR -> UBR
        }
 
        
        self.corner_orientation_tables = {
            Move.U : [0, 0, 0, 0, 0, 0, 0, 0],  # U move doesn't change any orientation
            Move.F : [2, 1, 0, 0, 1, 2, 0, 0],  # UFL -> 2, UFR -> 1, DFR -> 2, DFL -> 1
            Move.L : [1, 0, 2, 0, 2, 0, 1, 0],  # UFL -> 2, UBL -> 1, DBL -> 2, DFL -> 1
            Move.D : [0, 0, 0, 0, 0, 0, 0, 0],  # D move doesn't change any orientation
            Move.R : [0, 2, 0, 1, 0, 1, 0, 2],  # UFR -> 2, UBR -> 1, DBR -> 2, DFR -> 1
            Move.B : [0, 0, 1, 2, 0, 0, 2, 1],  # UBR -> 1, UBR -> 1, DBR -> 2, DBL -> 1
        }

        self.edge_permutation_tables = {
            Move.U: [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],  # UR -> UF, UF -> UL, UL -> UB, UB -> UR
            Move.F: [8, 1, 2, 3, 9, 5, 6, 7, 4, 0, 10, 11],  # FL -> UF, UF -> FR, FR -> FD, FD -> FL
            Move.D: [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],  # DF -> DR, DR -> DB, DB -> DL, DL -> DF
            Move.R: [0, 1, 2, 9, 4, 5, 6, 11, 8, 7, 10, 3],  # UR -> BR, BR -> DR, DR -> FR, FR -> UR
            Move.L: [0, 10, 2, 3, 4, 8, 6, 7, 1, 9, 5, 11],  # UL -> FL, FL -> DL, DL -> BL, BL -> UL
            Move.B: [0, 1, 11, 3, 4, 5, 10, 7, 8, 9, 2, 6],  # UB -> BL, BL -> DB, DB -> BR, BR -> UB
        }

        
        self.edge_orientation_tables = {
            Move.U: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # U move does not flip any edges
            Move.F: [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],  # F move flips UF and DF edges
            Move.D: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # D move does not flip any edges
            Move.R: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # R move flips UR, DR, BR, FR edges
            Move.L: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # L move flips UL, DL, BL, FL edges
            Move.B: [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1],  # B move flips UB, DB, BR, BL edges
        }
        
    corner_facelet_indices = [
        [Facelet.U6, Facelet.L2, Facelet.F0],  # UFL
        [Facelet.U8, Facelet.F2, Facelet.R0],  # UFR
        [Facelet.U0, Facelet.B2, Facelet.L0],  # UBL
        [Facelet.U2, Facelet.R2, Facelet.B0],  # UBR
        [Facelet.D0, Facelet.F6, Facelet.L8],  # DFL
        [Facelet.D2, Facelet.R6, Facelet.F8],  # DFR
        [Facelet.D6, Facelet.L6, Facelet.B8],  # DBL
        [Facelet.D8, Facelet.B6, Facelet.R8]   # DBR
    ]

    edge_facelet_indices = [
        [Facelet.U7, Facelet.F1],  # UF: U, F
        [Facelet.U3, Facelet.L1],  # UL: U, L
        [Facelet.U1, Facelet.B1],  # UB: U, B
        [Facelet.U5, Facelet.R1],  # UR: U, R
        [Facelet.D1, Facelet.F7], # DF: D, F
        [Facelet.D3, Facelet.L7], # DL: D, L
        [Facelet.D7, Facelet.B7], # DB: D, B
        [Facelet.D5, Facelet.R7], # DR: D, R
        [Facelet.F3, Facelet.L5], # FL: F, L
        [Facelet.F5, Facelet.R3], # FR: F, R
        [Facelet.B5, Facelet.L3], # BL: B, L
        [Facelet.B3, Facelet.R5]  # BR: B, R
    ]

    def to_facelet_representation(self):
        facelet_array = ['x'] * 54

        # Define the colors associated with each corner and edge piece
        corner_colors = [
            ['W', 'O', 'G'],  # UFL
            ['W', 'G', 'R'],  # UFR
            ['W', 'B', 'O'],  # UBL
            ['W', 'R', 'B'],  # UBR
            ['Y', 'G', 'O'],  # DFL
            ['Y', 'R', 'G'],  # DFR
            ['Y', 'O', 'B'],  # DBL
            ['Y', 'B', 'R'],  # DBR
        ]

        edge_colors = [
            ['W', 'G'],  # UF
            ['W', 'O'],  # UL
            ['W', 'B'],  # UB
            ['W', 'R'],  # UR
            ['Y', 'G'],  # DF
            ['Y', 'O'],  # DL
            ['Y', 'B'],  # DB
            ['Y', 'R'],  # DR
            ['G', 'O'],  # FL
            ['G', 'R'],  # FR
            ['B', 'O'],  # BL
            ['B', 'R'],  # BR
        ]

        # Fill the corners
        for i in range(8):
            perm = self.corner_permutations[i]
            orient = self.corner_orientations[i]
            for j in range(3):
                facelet_array[self.corner_facelet_indices[i][j]] = (corner_colors[perm])[(j+orient)%3]

        # Fill the edges
        for i in range(12):
            perm = self.edge_permutations[i]
            orient = self.edge_orientations[i]
            for j in range(2):
                facelet_array[self.edge_facelet_indices[i][j]] = edge_colors[perm][(j + orient) % 2]

        # Fill the center pieces (fixed colors)
        center_colors = ['W', 'O', 'G', 'R', 'B', 'Y']
        center_indices = [Facelet.U4, Facelet.L4, Facelet.F4, Facelet.R4, Facelet.B4, Facelet.D4]

        for i in range(6):
            facelet_array[center_indices[i]] = center_colors[i]

        return ''.join(facelet_array)
    
    def __repr__(self):
        return (f"Corner Permutations: {self.corner_permutations}\n"
                f"Corner Orientations: {self.corner_orientations}\n"
                f"Edge Permutations: {self.edge_permutations}\n"
                f"Edge Orientations: {self.edge_orientations}\n\n")
    

    def rotate_clockwise(self, face):
    # Permute corers 
        corner_permutation_table = self.corner_permutation_tables[face]
        new_corner_permutations = [0] * 8
        new_corner_orientations = [0] * 8
        for i in range(8):
            new_corner_permutations[i] = self.corner_permutations[corner_permutation_table[i]]
            new_corner_orientations[i] = self.corner_orientations[corner_permutation_table[i]]

        self.corner_permutations = new_corner_permutations
        self.corner_orientations = new_corner_orientations


        corner_orientation_table = self.corner_orientation_tables[face]
        for i in range(8):
            new_corner_orientations[i] = (self.corner_orientations[i] + corner_orientation_table[i]) % 3 
        self.corner_orientations = new_corner_orientations

        edge_permutation_table = self.edge_permutation_tables[face]
        new_edge_permutations = [0] * 12
        new_edge_orientations = [0] * 12
        for i in range(12):
            new_edge_permutations[i] = self.edge_permutations[edge_permutation_table[i]]
            new_edge_orientations[i] = self.edge_orientations[edge_permutation_table[i]]

        self.edge_permutations = new_edge_permutations
        self.edge_orientations = new_edge_orientations

        edge_orientation_table = self.edge_orientation_tables[face]
        for i in range(12):
            new_edge_orientations[i] = (self.edge_orientations[i] + edge_orientation_table[i]) % 2 
        self.edge_orientations = new_edge_orientations

    def binomial_coefficient(self, n, k):
            return math.comb(n, k)
        
    def get_corner_orientation_coordinate(self):
        # Converts corner orientations to a unique integer in the range 0 - 3^7-1
        weight = 1
        corner_orientation_coordinate = 0
        for i in range(7): 
            corner_orientation_coordinate += self.corner_orientations[i] * weight
            weight *= 3
        return corner_orientation_coordinate

    def get_edge_orientation_coordinate(self):
        # Converts corner orientations to a unique integer in the range 0 - 2^11-1
        weight = 1
        edge_orientation_coordinate = 0
        for i in range(11):
            edge_orientation_coordinate += self.edge_orientations[i] * weight 
            weight *= 2
        return edge_orientation_coordinate 

    def get_UD_slice_coordinate(self):
        # Converts UD-slice-coordinates to a unique integer i the range 0-495
        slice_indices = [1 if i in [8, 9, 10, 11] else 0 for i in self.edge_permutations]
        UD_slice_coordinate = 0
        occupied_count = -1
    
        for i in range(12):  
            if occupied_count == -1:
                if slice_indices[i] == 1:
                    occupied_count = 0
            elif slice_indices[i] == 0:  
                UD_slice_coordinate += self.binomial_coefficient(i, occupied_count)
            else:
                occupied_count += 1
        return UD_slice_coordinate
    
    def get_g1_coordinates(self):
        return (self.get_corner_orientation_coordinate(), self.get_edge_orientation_coordinate(), self.get_UD_slice_coordinate())


def generate_edge_tables():
    edge_coordinate_dict = {}
    for i in range(4096):
        binary_str = bin(i)[2:].zfill(12)  # 'zfill(12)' ensures the string is 12 characters long
    
        edge_orientation = [int(digit) for digit in binary_str]
        cube = CubieCube()
        cube.edge_orientations = edge_orientation
        
        base_coordinate = cube.get_edge_orientation_coordinate()
        
        sub_coordinates = []
        for i in [Move.U, Move.L, Move.F, Move.R, Move.B, Move.D]:
            sub_cube = CubieCube()
            sub_cube.edge_orientations = edge_orientation
            for j in range(3):
                sub_cube.rotate_clockwise(i)
                sub_coordinates.append(sub_cube.get_edge_orientation_coordinate())
        edge_coordinate_dict[base_coordinate] = sub_coordinates
    data =  {k: edge_coordinate_dict[k] for k in sorted(edge_coordinate_dict)}
    # Write the data to a JSON file
    filename = "edge_table.json"
    with open(filename, 'w') as json_file:  # Open in append mode
        json.dump(data, json_file, indent=4)
        json_file.write('\n')  # Ensure each dictionary is on a new line

    print(f"Base coordinate {base_coordinate} and its sub-coordinates written to {filename}")
    return 

def main():
    cube = CubieCube()
    #cube.corner_orientations = [1,1,1,1,1,1,1,1,1]
   #cube.corner_permutations = [4,5,2,3,0,7,1,6]
    # fix the orientation for each face.
    # orienation depends on position???

    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.F)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.L)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.D)
    cube.rotate_clockwise(Move.D)
    cube.rotate_clockwise(Move.D)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.F)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.R)
    cube.rotate_clockwise(Move.L)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.B)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.U)
    cube.rotate_clockwise(Move.F)
    cube.rotate_clockwise(Move.F)
    
    print(cube)
    import main
    main.main(cube.to_facelet_representation())
    #generate_edge_tables()
    # write code that iterates through all possible edge_orientations 
    # for each of these, calculate the coordinate of that edge. 
    # also calculate the result of the 18 possible moves on that coordinate (using teh cubie to do these rotations )
    # store the results in a file called edge_table 
    return       

if __name__ == '__main__':
    main()
    
cube = CubieCube()
print(cube.get_g1_coordinates())

#if the piece is in any of UFR, UBR, DBR, DFR, flip the piece

'''
print(cube)
import engine
engine.main(cube.to_facelet_representation())'''


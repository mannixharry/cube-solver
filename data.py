from enum import IntEnum
    
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

class Face(IntEnum):
    U = 0
    F = 1 
    L = 2
    R = 3
    B = 4
    D = 5

class Move(IntEnum):
    U = 0 # U
    F = 1 # F
    L = 2 # L
    R = 3 # R
    B = 4 # B
    D = 5 # D
    U2 = 6 # U2
    F2 = 7 # F2
    L2 = 8 # L2
    R2 = 9 # R2
    B2 = 10 # B2
    D2 = 11 # D2
    U3 = 12 # U'
    F3 = 13 # F'
    L3 = 14 # L'
    R3 = 15 # R'
    B3 = 16 # B'
    D3 = 17 # D'

'''
Facelets are numbered going across, starting in the top left of the face.
'''
class Facelet(IntEnum):
    U0 = 0 
    U1 = 1
    U2 = 2
    U3 = 3
    U4 = 4
    U5 = 5
    U6 = 6
    U7 = 7
    U8 = 8
    F0 = 9
    F1 = 10
    F2 = 11
    F3 = 12
    F4 = 13
    F5 = 14
    F6 = 15
    F7 = 16
    F8 = 17
    L0 = 18
    L1 = 19
    L2 = 20
    L3 = 21
    L4 = 22
    L5 = 23
    L6 = 24
    L7 = 25
    L8 = 26
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

class Data:

    '''
    The following dictionaries define rotations for the CubieCube representation. 
    Corner permutation and edge permutation, and their respective orientations are all treated independently.
    The dictionaries are in an is-replaced-by format. The index of each item in an array represents a piece code, whilst the data value
    represents the code of the piece replacing it. 
    For example, in corner_permutation_map the first data item, at index 0, in Move.U = [1,3,0,2,4,5,6,7] means that the piece with code
    1 moves into the position 0 following a U move. 
    ie: UFR replaced UFL
    
    Position / Piece codes : [UFL, UFR, UBL, UBR, DFL, DFR, DBL, DBR]
                             [  0,   1,   2,   3,   4,   5,   6,   7]
    '''

    __corner_permutation_dict = {
            Move.U : [Corner.UFR, Corner.UBR, Corner.UFL, Corner.UBL, Corner.DFL, Corner.DFR, Corner.DBL, Corner.DBR], 
            Move.F : [Corner.DFL, Corner.UFL, Corner.UBL, Corner.UBR, Corner.DFR, Corner.UFR, Corner.DBL, Corner.DBR],
            Move.L : [Corner.UBL, Corner.UFR, Corner.DBL, Corner.UBR, Corner.UFL, Corner.DFR, Corner.DFL, Corner.DBR],  
            Move.D : [Corner.UFL, Corner.UFR, Corner.UBL, Corner.UBR, Corner.DBL, Corner.DFL, Corner.DBR, Corner.DFR], 
            Move.R : [Corner.UFL, Corner.DFR, Corner.UBL, Corner.UFR, Corner.DFL, Corner.DBR, Corner.DBL, Corner.UBR],  
            Move.B : [Corner.UFL, Corner.UFR, Corner.UBR, Corner.DBR, Corner.DFL, Corner.DFR, Corner.UBL, Corner.DBL], 
        }
    
    '''
    0 -> No twist
    1 -> Clockwise twist with respect to reference
    2 -> Anti-clockwise twist with respect to reference
    '''
    __corner_orientation_dict = {
                Move.U : [0, 0, 0, 0, 0, 0, 0, 0],  
                Move.F : [2, 1, 0, 0, 1, 2, 0, 0], 
                Move.L : [1, 0, 2, 0, 2, 0, 1, 0],  
                Move.D : [0, 0, 0, 0, 0, 0, 0, 0], 
                Move.R : [0, 2, 0, 1, 0, 1, 0, 2],  
                Move.B : [0, 0, 1, 2, 0, 0, 2, 1],  
            }

    '''
    Position / Piece codes : [UF, UL, UB, UR, DF, DL, DB, DR, FL, FR, BL, BR]
                             [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11]
    '''
    __edge_permutation_dict = {
                Move.U: [Edge.UR, Edge.UF, Edge.UL, Edge.UB, Edge.DF, Edge.DL, Edge.DB,  Edge.DR,  Edge.FL, Edge.FR, Edge.BL, Edge.BR],  
                Move.F: [Edge.FL, Edge.UL, Edge.UB, Edge.UR, Edge.FR, Edge.DL, Edge.DB,  Edge.DR,  Edge.DF, Edge.UF, Edge.BL, Edge.BR],  
                Move.L: [Edge.UF, Edge.BL, Edge.UB, Edge.UR, Edge.DF, Edge.FL, Edge.DB,  Edge.DR,  Edge.UL, Edge.FR, Edge.DL, Edge.BR],  
                Move.D: [Edge.UF, Edge.UL, Edge.UB, Edge.UR, Edge.DL, Edge.DB, Edge.DR,  Edge.DF,  Edge.FL, Edge.FR, Edge.BL, Edge.BR], 
                Move.R: [Edge.UF, Edge.UL, Edge.UB, Edge.FR, Edge.DF, Edge.DL, Edge.DB,  Edge.BR,  Edge.FL, Edge.DR, Edge.BL, Edge.UR],  
                Move.B: [Edge.UF, Edge.UL, Edge.BR, Edge.UR, Edge.DF, Edge.DL, Edge.BL,  Edge.DR,  Edge.FL, Edge.FR, Edge.UB, Edge.DB],  
            }

    '''
    0 -> No flip with respect to reference
    1 -> Flipped with respect to reference
    '''
    __edge_orientation_dict = {
                Move.U: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                Move.F: [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0], 
                Move.L: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  
                Move.D: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                Move.R: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  
                Move.B: [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1], 
            }
    
    '''
    Array to store dictionaries used in cubie-cube rotations. 
    '''
    cubie_move_dicts = [__corner_permutation_dict, __corner_orientation_dict, __edge_permutation_dict, __edge_orientation_dict]
    

    '''
    The colours on face array defines how to cycle colours clockwise on a face using the is-replaced-by form.
    This is used by the computer vision to correctly orient the faces for the solver after they have been captured. 
    '''
    colours_on_face_map = [6,3,0,7,4,1,8,5,2]
    
    '''
    Used for cubie-facelet conversion. 
    corner_facelet_indices stores the three facelets comprising each corner cubie. 
    edge_facelet_indices stores the two facelets comprising each edge cubie. 
    '''
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
            [Facelet.U7, Facelet.F1],  # UF
            [Facelet.U3, Facelet.L1],  # UL
            [Facelet.U1, Facelet.B1],  # UB
            [Facelet.U5, Facelet.R1],  # UR
            [Facelet.D1, Facelet.F7],  # DF
            [Facelet.D3, Facelet.L7],  # DL
            [Facelet.D7, Facelet.B7],  # DB
            [Facelet.D5, Facelet.R7],  # DR
            [Facelet.F3, Facelet.L5],  # FL
            [Facelet.F5, Facelet.R3],  # FR
            [Facelet.B5, Facelet.L3],  # BL
            [Facelet.B3, Facelet.R5]   # BR
        ]
  
    '''
    Defines the colours associated with each corner and edge piece.
    There are subtleties in the order in which these, and the preceding tables are defined, which avoid issues related to the order of 
    colours on the displayed cube.  
    '''
    corner_colour_table = [
            ['W', 'O', 'G'],  # UFL
            ['W', 'G', 'R'],  # UFR
            ['W', 'B', 'O'],  # UBL
            ['W', 'R', 'B'],  # UBR
            ['Y', 'G', 'O'],  # DFL
            ['Y', 'R', 'G'],  # DFR
            ['Y', 'O', 'B'],  # DBL
            ['Y', 'B', 'R'],  # DBR
        ]

    edge_colour_table = [
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
    
    '''
    Define the notation displayed to the user.
    Used by the solver. 
    '''
    move_notation = ['U', 'F', 'L', 'R', 'B', 'D', 'U2', 'F2', 'L2', 'R2', 'B2', 'D2', 'U3', 'F3', 'L3', 'R3', 'B3', 'D3']
    move_notation_for_display = ['U', 'F', 'L', 'R', 'B', 'D', 'U2', 'F2', 'L2', 'R2', 'B2', 'D2', 'U\'', 'F\'', 'L\'', 'R\'', 'B\'', 'D\'']
    '''
    Define allowed moves in g1 and g2 subsets. 
    '''
    g1_allowed_moves = range(18) 
    g2_allowed_moves = [Move.U, Move.D, Move.U3, Move.D3, Move.F2, Move.B2, Move.L2, Move.R2]

    '''
    Define RGB colours for the the cube. 
    And the displayed facelet indices. 
    '''

    colour_map = {
            'R': (255, 0, 0),       # Red
            'O': (255, 100, 0),     # Orange
            'Y': (255, 255, 0),     # Yellow
            'W': (255, 255, 255),   # White
            'G': (0, 187, 0),       # Green
            'B': (0, 0, 187),       # Blue
            'T': (0,0,0)            # Test
        }
    
    overlay_colour_map = {
        'W' : (255, 255, 255),  # White
        'O' : (0, 165, 255),    # Orange
        'G' : (0, 255, 0),      # Green
        'R' : (0, 0, 255),      # Red
        'B' : (255, 0, 0),      # Blue
        'Y' : (0, 255, 255)     # Yellow
    }
            
'''
Class to manage the loading of move tables. 
If a move table is not found, it will raise an error. 

-- Need to add automatic loading of the tables -- (error correction)
'''


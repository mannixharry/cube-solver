from enum import IntEnum
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
    U2 = 6
    F2 = 7
    L2 = 8
    D2 = 9
    R2 = 10
    B2 = 11
    U3 = 12 
    F3 = 13
    L3 = 14
    D3 = 15
    R3 = 16
    B3 = 17 

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

class Data:

    #move_tables = move_tables.MoveTableGenerator()
    
    corner_permutation_tables = {
            Move.U : [1, 3, 0, 2, 4, 5, 6, 7],  # UFR -> UFL, UBR -> UFR, UFL -> UBL, UBL -> UBR
            Move.F : [4, 0, 2, 3, 5, 1, 6, 7],  # UFL -> DFL, UFR -> UFL, DFR -> UFR, DFL -> DFR
            Move.L : [2, 1, 6, 3, 0, 5, 4, 7],  # UFL -> DFL, DFL -> DBL, DBL -> UBL, UBL -> UFL
            Move.D : [0, 1, 2, 3, 6, 4, 7, 5],  # DFR -> DBR, DBR -> DBL, DBL -> DFL, DFL -> DFR 
            Move.R : [0, 5, 2, 1, 4, 7, 6, 3],  # DFR -> UFR, UFR -> UBR, UBR -> DBR, DBR -> DFR
            Move.B : [0, 1, 3, 7, 4, 5, 2, 6],  # UBR -> UBL, UBL -> DBL, DBL -> DBR, DBR -> UBR
        }
 
    corner_orientation_tables = {
                Move.U : [0, 0, 0, 0, 0, 0, 0, 0],  # U move doesn't change any orientation
                Move.F : [2, 1, 0, 0, 1, 2, 0, 0],  # UFL -> 2, UFR -> 1, DFR -> 2, DFL -> 1
                Move.L : [1, 0, 2, 0, 2, 0, 1, 0],  # UFL -> 2, UBL -> 1, DBL -> 2, DFL -> 1
                Move.D : [0, 0, 0, 0, 0, 0, 0, 0],  # D move doesn't change any orientation
                Move.R : [0, 2, 0, 1, 0, 1, 0, 2],  # UFR -> 2, UBR -> 1, DBR -> 2, DFR -> 1
                Move.B : [0, 0, 1, 2, 0, 0, 2, 1],  # UBR -> 1, UBR -> 1, DBR -> 2, DBL -> 1
            }

    edge_permutation_tables = {
                Move.U: [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],  # UR -> UF, UF -> UL, UL -> UB, UB -> UR
                Move.F: [8, 1, 2, 3, 9, 5, 6, 7, 4, 0, 10, 11],  # FL -> UF, UF -> FR, FR -> FD, FD -> FL
                Move.D: [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],  # DF -> DR, DR -> DB, DB -> DL, DL -> DF
                Move.R: [0, 1, 2, 9, 4, 5, 6, 11, 8, 7, 10, 3],  # UR -> BR, BR -> DR, DR -> FR, FR -> UR
                Move.L: [0, 10, 2, 3, 4, 8, 6, 7, 1, 9, 5, 11],  # UL -> FL, FL -> DL, DL -> BL, BL -> UL
                Move.B: [0, 1, 11, 3, 4, 5, 10, 7, 8, 9, 2, 6],  # UB -> BL, BL -> DB, DB -> BR, BR -> UB
            }

            
    edge_orientation_tables = {
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
  
    # Define the colours associated with each corner and edge piece
    corner_colours = [
            ['W', 'O', 'G'],  # UFL
            ['W', 'G', 'R'],  # UFR
            ['W', 'B', 'O'],  # UBL
            ['W', 'R', 'B'],  # UBR
            ['Y', 'G', 'O'],  # DFL
            ['Y', 'R', 'G'],  # DFR
            ['Y', 'O', 'B'],  # DBL
            ['Y', 'B', 'R'],  # DBR
        ]

    edge_colours = [
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
    
    move_notation = ['U', 'F', 'L', 'D', 'R', 'B', 'U2', 'F2', 'L2', 'D2', 'R2', 'B2', 'U3', 'F3', 'L3', 'D3', 'R3', 'B3']

    
class Move_Tables:
    try: 
        with open('corner_orientation_table.json', 'r') as corner_orientation_file:
                corner_orientation_table = json.load(corner_orientation_file)
        with open('edge_orientation.json', 'r') as edge_orientation_file:
                edge_orientation_table = json.load(edge_orientation_file)
        with open('UD_slice_permutation.json', 'r') as UD_slice_permutation_file:
            UD_slice_permutation_table = json.load(UD_slice_permutation_file)
    except: 
        corner_orientation_table = edge_orientation_table = UD_slice_permutation_table = None
        print('Move Tables not found')
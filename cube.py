from data import *

class CubieCube:
    def __init__(self):
        
        self.corner_permutations = list(range(8))
        self.corner_orientations = [0] * 8
        self.edge_permutations = list(range(12))
        self.edge_orientations = [0] * 12
        
        self.corner_permutation_tables = Data.corner_permutation_tables
        self.corner_orientation_tables = Data.corner_orientation_tables
        self.edge_permutation_tables = Data.edge_permutation_tables
        self.edge_orientation_tables = Data.edge_orientation_tables

        self.corner_colours = Data.corner_colours
        self.edge_colours = Data.edge_colours
        self.corner_facelet_indices = Data.corner_facelet_indices
        self.edge_facelet_indices = Data.edge_facelet_indices
        
        
    def rotate_clockwise(self, move):

        corner_permutation_table = self.corner_permutation_tables[move]
        new_corner_permutations = [0] * 8
        new_corner_orientations = [0] * 8
        for i in range(8):
            new_corner_permutations[i] = self.corner_permutations[corner_permutation_table[i]]
            new_corner_orientations[i] = self.corner_orientations[corner_permutation_table[i]]

        self.corner_permutations = new_corner_permutations
        self.corner_orientations = new_corner_orientations


        corner_orientation_table = self.corner_orientation_tables[move]
        for i in range(8):
            new_corner_orientations[i] = (self.corner_orientations[i] + corner_orientation_table[i]) % 3 
        self.corner_orientations = new_corner_orientations

        edge_permutation_table = self.edge_permutation_tables[move]
        new_edge_permutations = [0] * 12
        new_edge_orientations = [0] * 12
        for i in range(12):
            new_edge_permutations[i] = self.edge_permutations[edge_permutation_table[i]]
            new_edge_orientations[i] = self.edge_orientations[edge_permutation_table[i]]

        self.edge_permutations = new_edge_permutations
        self.edge_orientations = new_edge_orientations

        edge_orientation_table = self.edge_orientation_tables[move]
        for i in range(12):
            new_edge_orientations[i] = (self.edge_orientations[i] + edge_orientation_table[i]) % 2 
        self.edge_orientations = new_edge_orientations
        

    def __repr__(self):
        return (f"Corner Permutations: {self.corner_permutations}\n"
                f"Corner Orientations: {self.corner_orientations}\n"
                f"Edge Permutations: {self.edge_permutations}\n"
                f"Edge Orientations: {self.edge_orientations}\n")
        
class FaceletCube:
    def __init__(self, facelet_str=None):
        self.facelets = ['x'] * 54 if facelet_str is None else list(facelet_str)
    
        self.corner_colours = Data.corner_colours
        self.edge_colours = Data.edge_colours
        self.corner_facelet_indices = Data.corner_facelet_indices
        self.edge_facelet_indices = Data.edge_facelet_indices    
        
    def from_cubie_cube(self, cubie_cube):
        facelets = ['x'] * 54
        
        # Fill the corners
        for i in range(8):
            permutation = cubie_cube.corner_permutations[i]
            orientation = cubie_cube.corner_orientations[i]
            for j in range(3):
                facelets[self.corner_facelet_indices[i][j]] = (self.corner_colours[permutation])[(j+orientation)%3]

        # Fill the edges
        for i in range(12):
            permutation = cubie_cube.edge_permutations[i]
            orientation = cubie_cube.edge_orientations[i]
            for j in range(2):
                facelets[self.edge_facelet_indices[i][j]] = self.edge_colours[permutation][(j + orientation) % 2]

        # Fill the centre pieces (fixed colours)
        centre_colours = ['W', 'O', 'G', 'R', 'B', 'Y']
        centre_indices = [Facelet.U4, Facelet.L4, Facelet.F4, Facelet.R4, Facelet.B4, Facelet.D4]

        for i in range(6):
            facelets[centre_indices[i]] = centre_colours[i]

        self.facelets = facelets
        return ''.join(facelets)
    
        

    def to_cubie_cube(self):
        
        cubie_cube = CubieCube()

        new_corner_permuations = [0] * 8
        new_corner_orientations = [0] * 8
        new_edge_permutations = [0] * 12
        new_edge_orientations = [0] * 12

        for i, corner_index, in enumerate(self.corner_facelet_indices): 
            colours = [self.facelets[i] for i in corner_index]
            orientation = -(colours.index('W')  if 'W' in colours else colours.index('Y')) % 3
            permutation =  self.corner_colours.index([colours[(i-orientation)%3] for i in range(3)])
            new_corner_permuations[i] = permutation
            new_corner_orientations[i] = orientation
            
        for i, edge_index, in enumerate(self.edge_facelet_indices): 
            colours = [self.facelets[i] for i in edge_index]
            orientation = -(colours.index('W')  if 'W' in colours else colours.index('Y') if 'Y' in colours else colours.index('G') if 'G' in colours else colours.index('B')) % 2
            permutation =  self.edge_colours.index([colours[(i-orientation)%2] for i in range(2)])
            new_edge_permutations[i] = permutation
            new_edge_orientations[i] = orientation
        
        cubie_cube.corner_permutations = new_corner_permuations
        cubie_cube.corner_orientations = new_corner_orientations
        cubie_cube.edge_permutations = new_edge_permutations
        cubie_cube.edge_orientations = new_edge_orientations
        
        return cubie_cube

    def __repr__(self):
        return ''.join(self.facelets)
  
  
def main():
    
    
    cube = CubieCube()
    
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
    
    import main
    facelet = FaceletCube()
    main.main(facelet.from_cubie_cube(cube))
    
    
    #generate_edge_tables()
    # write code that iterates through all possible edge_orientations 
    # for each of these, calculate the coordinate of that edge. 
    # also calculate the result of the 18 possible moves on that coordinate (using teh cubie to do these rotations )
    # store the results in a file called edge_table 
    return       

if __name__ == '__main__':
    main()



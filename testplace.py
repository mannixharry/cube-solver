import main 
import cube
from data import *  


test_cube = cube.CubieCube()
test_cube.rotate_clockwise(Move.U2)
test_cube.rotate_clockwise(Move.D2)
test_cube.rotate_clockwise(Move.F2)
test_cube.rotate_clockwise(Move.B2)
test_cube.rotate_clockwise(Move.L2)
test_cube.rotate_clockwise(Move.R2)
test_cube.edge_orientations = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
main.main(str(cube.FaceletCube(test_cube)))
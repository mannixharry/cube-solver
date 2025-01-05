import main 
import cube
from data import *  


test_cube = cube.CubieCube()

test_cube.rotate_clockwise(Move.U)
test_cube.rotate_clockwise(Move.L3)
test_cube.rotate_clockwise(Move.R3)
test_cube.rotate_clockwise(Move.B3)
test_cube.rotate_clockwise(Move.L2)
test_cube.rotate_clockwise(Move.D2)
test_cube.rotate_clockwise(Move.F)
test_cube.rotate_clockwise(Move.D2)
test_cube.rotate_clockwise(Move.L2)

test_cube.rotate_clockwise(Move.F2)
test_cube.rotate_clockwise(Move.L2)
test_cube.rotate_clockwise(Move.B)
test_cube.rotate_clockwise(Move.L)
test_cube.rotate_clockwise(Move.R)



main.main(str(cube.FaceletCube(test_cube)))
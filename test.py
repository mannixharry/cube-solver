import main 
import cube
from data import *  


test_cube = cube.CubieCube()

test_cube.rotate_clockwise(Move.U)
test_cube.rotate_clockwise(Move.L3)


main.main(str(cube.FaceletCube(test_cube)))
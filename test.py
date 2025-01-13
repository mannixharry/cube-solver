import main 
import cube
from data import *  


test_cube = cube.CubieCube()
test_cube.move(Move.U2)
test_cube.move(Move.D2)
test_cube.move(Move.F2)

facelet_cube = cube.FaceletCube(test_cube)
new_test = cube.CubieCube(facelet_cube)


main.main(str(cube.FaceletCube(test_cube)))
main.main(str(cube.FaceletCube(new_test)))
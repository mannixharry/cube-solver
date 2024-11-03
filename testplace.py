import main 
import cube 

test_cube = cube.CubieCube()
test_cube.corner_orientations = [0, 0, 1, 2, 0, 0, 2, 1]
main.main(str(cube.FaceletCube(test_cube)))
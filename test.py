import main 
import cube
from data import *  


test_cube = cube.CubieCube('WYBWWBRGBYWYBGWYGBROGROYWOGOORRRWROWYRGBBGGBBOYWGYYORO')

#OGBRWWGBOWOWYGYYRRWBRYOBBGRBRYGRWWYGOWGOBRYBRGGBOYOYWO

facelet_cube = cube.FaceletCube(test_cube)


main.main(str(cube.FaceletCube(test_cube)))

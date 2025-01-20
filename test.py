import main 
import cube
from data import *  


test_cube = cube.CubieCube('OGBRWWGBOWOWYGYYRRWBRYOBBGRBRYGRWWYGOWGOBRYBRGGBOYOYWO')

#OGBRWWGBOWOWYGYYRRWBRYOBBGRBRYGRWWYGOWGOBRYBRGGBOYOYWO

facelet_cube = cube.FaceletCube(test_cube)


main.main(str(cube.FaceletCube(test_cube)))

'''
TO DO:

- make it so that impossible solves are detected
- make an animation to show how to scan in cube.
- 

'''

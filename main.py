from data import *
from engine import *
import solver
import pygame
from pygame.locals import * 
import cube 

def generate_solve_moves(full_solution):
    return (i for i in full_solution)

def main(cube_string='WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY'):

    cube_manager = CubeManager(cube_string)
    start_solve_demonstration = False

    # Timer for move demonstration
    last_move_time = pygame.time.get_ticks()
    move_interval_ms = 2000  # 1000 ms = 1 second
    solve_stage = 0
    
    last_move = None
    setting_view = False

    clock = pygame.time.Clock()
    running = True
    while running:
        cube_manager.main()
        rotation_speed = cube_manager.rotation_speed
        keys = pygame.key.get_pressed()
        angle = [0, 0, 0]

        # Handle key presses for cube rotation
        if keys[K_UP]:
            angle[0] = -rotation_speed
        if keys[K_DOWN]:
            angle[0] = rotation_speed
        if keys[K_LEFT]:
            angle[1] = rotation_speed
        if keys[K_RIGHT]:
            angle[1] = -rotation_speed
        if keys[K_z]:
            angle[2] = -rotation_speed
        if keys[K_x]:
            angle[2] = rotation_speed

        # Start demonstration if space is pressed
        if keys[K_x]:
            cube_manager.set_cube_view(Move.F)

        if keys[K_SPACE]:
            if not start_solve_demonstration:
                start_solve_demonstration = True
                cube_solver = solver.Solver()
                print(cube_manager.cube)  # Current cube state
                cube_to_solve = cube.CubieCube(cube_manager.cube)

                contracted_solution, _ = cube_solver.solve_cube(cube_to_solve)
                move_generator = generate_solve_moves(contracted_solution)
                if contracted_solution:
                    move = next(move_generator)
                    last_move_time = pygame.time.get_ticks()
                    solve_stage = 0
                    last_move = None
                    setting_view = False
                else: 
                    start_solve_demonstration = False

        if keys[K_TAB]:
            new_cube = cube_manager.cube
            main(str(cube.FaceletCube(new_cube)))
            running = False
# Demonstration with alternating actions
        if start_solve_demonstration:
        
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time >= move_interval_ms:
                try:
                    if solve_stage % 3 == 0:
                        if last_move != None:
                            move = Move(next(move_generator))
                            if last_move%6 in [Face.B, Face.D] and move%6 in [Face.L, Face.R] or last_move%6 in [Face.L, Face.R] and move%6 in [Face.D, Face.B] or last_move%6 in [Face.B, Face.D] and move%6 in [Face.B, Face.D]:
                                setting_view = cube_manager.set_cube_view(Edge.UF, 60)
                            else:
                                setting_view = False
                        last_move = Move(move)
                        
                        if not setting_view:
                            solve_stage += 1
                        
                    if solve_stage % 3 == 1:

                        view = Move(move)
                        setting_view = cube_manager.set_cube_view(view, 60)
                        if not setting_view:
                            solve_stage += 1

                    if solve_stage % 3 == 2:
                        # Perform face turn
                        cube_manager.set_face_turn(move)

                    solve_stage += 1
                    last_move_time = current_time  # Update last move time

                except StopIteration:
                    start_solve_demonstration = False
                    print("Solve demonstration complete.")
                    
                    cube_manager.set_cube_view(Corner.UFR)
                    

        cube_manager.change_cube_rotation(angle)

        # Handle manual face turns
        face_key_list = [K_u, K_f, K_l, K_r, K_b, K_d]
        
        if not start_solve_demonstration:
            move_number = next((i for i, val in enumerate(face_key_list) if keys[val]), None)
            if move_number is not None:
                move = Move(move_number)
                if keys[K_LSHIFT]:
                    move += 12  # Counter-clockwise
                if keys[K_LCTRL]:
                    move += 6  # Double move
                    
                cube_manager.set_face_turn(move)

        cube_manager.main()
        fps = clock.get_fps()
        cube_manager.renderer.display_fps(fps)

        pygame.display.flip()
        clock.tick(60)
        running = cube_manager.renderer.update()

    pygame.event.clear()
    pygame.quit()

if __name__ == '__main__':
    main()
    
# Next step is to add button to import cube. 
# + Instant scramble. 
# + Generate random scramble
# + solve 
# + display notation on screen when solving, and number of moves left. 
# then think about making solving more efficient (considering sub-optimal g1 paths.)
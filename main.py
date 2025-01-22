from data import *
from engine import *
import solver
import pygame
from pygame.locals import * 
import cube 
import vision

def main(cube_string='WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY'):

    cube_capturer = vision.Capturer()
    cube_manager = CubeManager(cube_string)
    is_demonstrating_solve = False
    is_paused = False

    # Timer for move demonstration
    move_interval_ms = 2000  # 1000 ms = 1 second
    
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

        if keys[K_SPACE]:
            if not is_demonstrating_solve and not cube_manager.face_turning:
                cube_solver = solver.Solver()
                cube_to_solve = cube.CubieCube(cube_manager.cube)

                solution, _ = cube_solver.solve_cube(cube_to_solve)
                solution_length = len(solution)
                
                if solution:
                    last_move_time = pygame.time.get_ticks()
                    solve_stage = 0
                    solution_index = 0
                    is_demonstrating_solve = True
                    solve_move = None
                    cube_manager.set_cube_view(Edge.UF)
                    
        if keys[K_TAB]:
            captured_cube =  cube_capturer.capture_cube()
            is_demonstrating_solve = False 

            if captured_cube: 
                cube_manager = CubeManager(captured_cube)

        if keys[K_RETURN]:
            cube_manager = CubeManager(cube.CubieCube())
            
        # Demonstration with alternating actions
        if is_demonstrating_solve:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time >= move_interval_ms:
                
                if solution_index == solution_length:
                    is_demonstrating_solve = False
                    print("Solve demonstration complete.")
                    cube_manager.set_cube_view(Corner.UFR)
                    continue
                
                if solve_stage % 3 == 0:
                    
                    if solution_index == 0:
                        solve_move = solution[solution_index]
                        setting_view = False
                    else: 
                        last_move = move
                        solve_move = solution[solution_index]
                        last_face = last_move % 6 
                        if last_face in [Face.L, Face.R, Face.D, Face.B]:
                            setting_view = cube_manager.set_cube_view(Edge.UF, 60)
                        else:
                            setting_view = False

                    if not setting_view:
                        solve_stage += 1
                    
                if solve_stage % 3 == 1:

                    view = Move(solve_move)
                    setting_view = cube_manager.set_cube_view(view, 60)
                    if not setting_view:
                        solve_stage += 1

                if solve_stage % 3 == 2:
                    # Perform face turn
                    cube_manager.set_face_turn(solve_move)
                    solution_index += 1

                solve_stage += 1
                last_move_time = current_time  # Update last move time

        cube_manager.change_cube_rotation(angle)

        # Handle manual face turns
        face_key_list = [K_u, K_f, K_l, K_r, K_b, K_d]
        
        if not is_demonstrating_solve:
            
            clicked_facelet = cube_manager.get_clicked_facelet()
            if clicked_facelet != None:
                move = Move(clicked_facelet // 9)
                counter_clockwise = (clicked_facelet % 9) in [0,3,6]
                double = (clicked_facelet%9) in [1,4,7]
                if counter_clockwise:
                    move += 12 
                if double:
                    move+=6
                
                cube_manager.set_face_turn(move)
                
            else:
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
        if is_demonstrating_solve and solve_move is not None:
            cube_manager.renderer.display_move_text(solution_length-solution_index, solve_move)
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
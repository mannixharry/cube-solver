from data import *
from engine import *
import solver
import pygame
from pygame.locals import * 
import cube 
import vision

def display_program_info(renderer, informatation):

    renderer.display_info(informatation)
    pygame.display.flip()

def wait():
    # Wait for the user to press Enter
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    pygame.quit()
                    exit()

def main(cube_string='WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY'):
       
    main_instructions = [
        "Welcome to the Rubik's Cube Solver",
        "Instructions:",
        "",
        "1. Click on a facelet to perform a face turn.",
        "2. Use arrow keys to rotate the cube view.",
        "3. Press 'Space' to solve the cube.",
        "4. Press 'Tab' to import a cube from the webcam.",
        "5. Press 'Backspace' to reset the cube.",
        "6. Press 'Escape' to quit the application.",
        "7. Press 'I' to enter this menu.",
        "",
        
        "Press Enter to continue..."
    ]
    
    
    capture_instructions = [
        "How to Capture the Cube:",
        "",
        "1. Start with the WHITE face in the overlay.",
        "   ORANGE should face UP.",
        "   Press SPACE to capture the WHITE face once aligned.",
        "",
        "2. Rotate the cube to capture the ORANGE, GREEN, RED, and BLUE faces.",
        "   Keep WHITE on TOP during these captures.",
        "   Press SPACE to capture each of these faces after aligning them.",
        "",
        "3. For the YELLOW face, rotate the cube so that:",
        "   - GREEN is on TOP, and",
        "   - YELLOW is in the overlay.",
        "   Press SPACE to capture the YELLOW face.",
        "",
        "Tips:",
        "- Align the cube with the overlay for accurate detection.",
        "- Ensure good lighting and avoid sticker reflections.",
        "",
    ]

    cube_capturer = vision.Capturer()
    cube_manager = CubeManager(cube_string)
    is_demonstrating_solve = False
    is_paused = False
    pause_debounce_ms = 500
    last_pause_time = 0

     # Display program info at the start
    display_program_info(cube_manager.renderer, main_instructions)
    wait()
    cube_manager.set_cube_view(Edge.UF)
    
    # Timer for move demonstration
    move_interval_ms = 3000  # 1000 ms = 1 second
    
    clock = pygame.time.Clock()
    running = True

    while running:

        current_time = pygame.time.get_ticks()

        cube_manager.main()
        rotation_speed = 0.025
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
            display_program_info(cube_manager.renderer, capture_instructions)
            captured_cube =  cube_capturer.capture_cube()
            is_demonstrating_solve = False 

            if captured_cube: 
                cube_manager = CubeManager(captured_cube)

        if keys[K_i]:
            display_program_info(cube_manager.renderer, main_instructions)
            wait()

        if is_demonstrating_solve and (current_time - last_pause_time) > pause_debounce_ms and (keys[K_p] or keys[K_BACKSPACE]):
            if keys[K_p]:  # Corrected condition
                last_pause_time = pygame.time.get_ticks()
                is_paused = not is_paused  # Toggle the pause state
                if not is_paused:
                    solve_stage = 0
            elif keys[K_BACKSPACE] and solution_index != 0:  # Corrected condition
                last_pause_time = pygame.time.get_ticks()
                solution_index -= 1
                move_to_invert = solution[solution_index]
                solve_stage = 0
          
                if move_to_invert < 6:
                    inverse_move = move_to_invert + 12
                elif move_to_invert < 12:
                    inverse_move = move_to_invert
                else:
                    inverse_move = move_to_invert - 12

                cube_manager.set_face_turn(inverse_move)
                last_move_time = pygame.time.get_ticks()
                
                
                cube_manager.renderer.display_move_text(solution_length-solution_index, solution[solution_index])

        if is_paused:
            cube_manager.renderer.display_text('paused...')

        if is_demonstrating_solve and not is_paused:    
            if solution_index < solution_length:
                    cube_manager.renderer.display_move_text(solution_length-solution_index, solution[solution_index])
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
                        last_move = solution[solution_index-1]
                        solve_move = solution[solution_index]
                        last_face = last_move % 6 
                        face = solve_move % 6
                        if last_face in [Face.L, Face.R] and face in [Face.D, Face.B] or last_face in [Face.D, Face.B] and face in [Face.L, Face.R]:
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
                    solution_index += 1
                    cube_manager.set_face_turn(solve_move)
                    

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

        fps = clock.get_fps()
        cube_manager.renderer.display_fps(fps)
        pygame.display.flip()
        clock.tick(120)
        running = cube_manager.renderer.update()

    pygame.event.clear()
    pygame.quit()

if __name__ == '__main__':
    main()
    

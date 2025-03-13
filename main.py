from move_table_generator import move_tables
from pruning_table_generator import pruning_tables
from data import *
from engine import *
import solver
import pygame
from pygame.locals import * 
import cube 
import vision
from screen import Button


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

def initialize_buttons(renderer):
    """Initialize and assign buttons to the cube manager's renderer."""
    width, height = renderer.width, renderer.height

    scramble_image = pygame.image.load('resources/scramble.png')
    reset_image = pygame.image.load('resources/reset.png')
    solve_image = pygame.image.load('resources/solve.png')
    capture_image = pygame.image.load('resources/capture.png')
    pause_play_image = pygame.image.load('resources/pause-play.png')
    replay_image = pygame.image.load('resources/replay.png')
    skip_image = pygame.image.load('resources/skip.png')
    
    size = (175, 70)

    scramble_button = Button('scramble', scramble_image, 0.05 * width, 0.4 * height, size, key = K_m)
    reset_button = Button('reset', reset_image, 0.05 * width, 0.5 * height, size, key = K_n)
    solve_button = Button('solve', solve_image, 0.95 * width - size[0], 0.4 * height, size, key = K_SPACE)
    capture_button = Button('capture', capture_image, 0.95 * width - size[0], 0.5 * height, size, key = K_TAB)
    pause_play_button = Button('pause-play', pause_play_image, 0.5*width - 60, 0.90 * height - 40, (120,80), key=K_p)
    replay_button = Button('replay', replay_image, 0.35*width - 30, 0.90 * height - 30, (60,60))
    skip_button = Button('skip', skip_image, 0.65*width - 30, 0.90 * height - 30, (60,60))

    renderer.add_button(scramble_button)
    renderer.add_button(reset_button)
    renderer.add_button(solve_button)
    renderer.add_button(capture_button)
    renderer.add_button(pause_play_button)
    renderer.add_button(replay_button)
    renderer.add_button(skip_button)

def main(cube_string='WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY'):
       
    #!!!
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

    renderer = Renderer()

    cube_capturer = vision.Capturer()
    cube_manager = CubeManager(cube_string, renderer)
    is_demonstrating_solve = False
    is_paused = False

     # Display program info at the start
    display_program_info(cube_manager.renderer, main_instructions)
    wait()
    cube_manager.set_cube_view(Edge.UF)
    
    # Timer for move demonstration
    move_interval_ms = 3000  # 1000 ms = 1 second
    
    clock = pygame.time.Clock()
    running = True

    initialize_buttons(renderer)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        cube_manager.main()

        for button in cube_manager.renderer.buttons:
            button.display(cube_manager.renderer.screen)

        rotation_speed = 0.025
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        cube_manager.renderer.update_mouse(mouse_pressed, mouse_pos, keys)

        angle = [0, 0, 0]

        # Handle key presses for cube rotation
        if keys[K_UP]:
            angle[0] = -rotation_speed
        if keys[K_DOWN]:
            angle[0] = +rotation_speed
        if keys[K_LEFT]:
            angle[1] = rotation_speed
        if keys[K_RIGHT]:
            angle[1] = -rotation_speed
        if keys[K_z]:
            angle[2] = -rotation_speed
        if keys[K_x]:
            angle[2] = rotation_speed

        clicked_button = cube_manager.renderer.get_clicked_button()
        if clicked_button:
            clicked_button_name  = clicked_button.name
        else:
            clicked_button_name  = None

        if clicked_button_name  == 'solve':
            if not is_demonstrating_solve and not cube_manager.face_turning:
                cube_solver = solver.Solver()
                cube_to_solve = cube.CubieCube(cube_manager.cube)
                print(cube_to_solve)
                if not cube_to_solve.verify_solvability():
                    raise('Cube is not solvable')

                cube_manager.renderer.display_text('Generating Solve...', 60)
                pygame.display.flip()
                solution = cube_solver.solve_cube(cube_to_solve)
                solution_length = len(solution)
                
                if solution:
                    last_move_time = pygame.time.get_ticks()
                    solve_stage = 0
                    solution_index = 0
                    is_demonstrating_solve = True
                    solve_move = None
                    cube_manager.set_cube_view(Edge.UF)
                    
        if clicked_button_name  == 'capture':
            display_program_info(renderer, capture_instructions)
            captured_cube =  cube_capturer.capture_cube()
            is_demonstrating_solve = False 

            if captured_cube: 
                cube_manager.update_cube(captured_cube)
               

        if keys[K_s] or clicked_button_name  == 'scramble':
            
            new_cube = cube.CubieCube()
            new_cube.scramble()

            cube_manager.update_cube(new_cube)
            is_demonstrating_solve = False
            
        if clicked_button_name  == 'reset':
            cube_manager.update_cube(cube.CubieCube())
            
            is_demonstrating_solve = False

        if keys[K_i]:
            display_program_info(renderer, main_instructions)
            wait()
        if is_demonstrating_solve:
            if clicked_button_name == 'pause-play':
                is_paused = not is_paused
                if not is_paused:
                    solve_stage = 0

            elif clicked_button_name == 'replay' and solution_index != 0 :  # Corrected condition
                move_to_invert = solution[solution_index-1]
                

                if move_to_invert < 6:
                    inverse_move = move_to_invert + 12
                elif move_to_invert < 12:
                    inverse_move = move_to_invert
                else:
                    inverse_move = move_to_invert - 12
                
                if cube_manager.set_face_turn(inverse_move):
                    solution_index -= 1 
                    solve_stage = 0
                    last_move_time = pygame.time.get_ticks()

            elif clicked_button_name == 'skip' and solution_index < solution_length:
                solve_move = solution[solution_index]
                
                if cube_manager.set_face_turn(solve_move):
                    solution_index += 1
                    solve_stage = 0
                    last_move_time = pygame.time.get_ticks()

                if solution_index == solution_length:
                    is_demonstrating_solve = False
                    print("Solve demonstration complete.")
                    cube_manager.set_cube_view(Corner.UFR)
                    continue
                

            
            
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
                    if not cube_manager.set_face_turn(solve_move):
                        solve_stage -= 1
                    

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

    pygame.event.clear()
    pygame.quit()

if __name__ == '__main__':
    main()
    

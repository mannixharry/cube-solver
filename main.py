import pygame
from pygame.locals import *
import cube
from data import * 
import numpy as np

class Renderer:

    def __init__(self, width=800, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.thickness = 2
        self.screen = self.create_window()
        self.font = pygame.font.SysFont('Arial', 20)
        self.colour = (0, 0, 0)
        
        self.displayed_quadrilaterals = []
        self.displayed_quadrilaterals_indices = []
        
        self.faces_clicked = []

    def detect_facelet_click(self, mouse_pos):
        
        def is_point_inside_triangle(A, B, C, P):
            v0, v1, v2 = C - A, B - A, P - A
            dot00, dot01, dot02, dot11, dot12 = np.dot(v0, v0), np.dot(v0, v1), np.dot(v0, v2), np.dot(v1, v1), np.dot(v1, v2)
            invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
            u, v = (dot11 * dot02 - dot01 * dot12) * invDenom, (dot00 * dot12 - dot01 * dot02) * invDenom
            return u >= 0 and v >= 0 and u + v <= 1
    
        def is_point_inside_quadrilateral(A, B, C, D, P):
            A, B, C, D, P = np.array(A), np.array(B), np.array(C), np.array(D), np.array(P)
            return is_point_inside_triangle(A, B, C, P) or is_point_inside_triangle(A, C, D, P)
        
        for i, quad in enumerate(self.displayed_quadrilaterals): 
            if is_point_inside_quadrilateral(*quad, mouse_pos):
                self.faces_clicked.append(self.displayed_quadrilaterals_indices[i])
                print(self.faces_clicked)
                break
                
    def create_window(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Basic 3D Engine')
        return screen

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.detect_facelet_click(mouse_pos)
        return True
    
    def clear_screen(self):
        self.screen.fill((255, 255, 255))
    
    def draw_line(self, a, b, colour):
        pygame.draw.line(self.screen, colour, a, b, self.thickness*3)
    
    def draw_rectangle(self, corners, colour):
        if colour:
            pygame.draw.polygon(self.screen, colour, corners)
            pygame.draw.polygon(self.screen, 'black', corners, self.thickness*2)
        else: 
            pygame.draw.polygon(self.screen, 'black', corners)

    def add_displayed_quadrilateral(self, rectangle, index):

        self.displayed_quadrilaterals.append(rectangle)
        self.displayed_quadrilaterals_indices.append(index)
        
    def display_fps(self, fps):
        fps_text = self.font.render(f'FPS: {int(fps)}', True, self.colour)
        self.screen.blit(fps_text, (10, 10))

class Rectangle:
    def __init__(self, corners, piece_colour=False):
        self.corners = [np.array(corner) for corner in corners]
        self.piece_colour = piece_colour 

    def get_normal(self):
        a,  b, c, _ = self.corners
        vector_x = b - a
        vector_y = c - a
        normal = np.cross(vector_x, vector_y)
        normal /= np.linalg.norm(normal)
        return normal
    
class Cube:
    def __init__(self, position_vector, scale=1):

        face_rectangles = [
            Rectangle([[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]]),  # Bottom face
            Rectangle([[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]),  # Top face
            Rectangle([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]]),  # Front face
            Rectangle([[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]]),  # Back face
            Rectangle([[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]]),  # Left face
            Rectangle([[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1]])   # Right face
        ]

        self.rectangles = []
        for rectangle in face_rectangles:
            self.rectangles.append(Rectangle([(corner + position_vector) * scale for corner in rectangle.corners],
                                             rectangle.piece_colour))
       
class Projector:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fov = 90
        self.znear, self.zfar = 0.1, 10000
        aspect = width / height
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        nf = 1.0 / (self.znear - self.zfar)
        self.projection_matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (self.zfar + self.znear) * nf, 2 * self.zfar * self.znear * nf],
            [0, 0, -1, 0]
        ])

    def project_vector(self, vector):
        vector_homogeneous = np.append(vector, 1)
        projected_vector = self.projection_matrix @ vector_homogeneous
        if projected_vector[3] != 0:
            projected_vector /= projected_vector[3]
        projected_vector += np.array([1, 1, 0, 0])
        return (
            projected_vector[0] * 0.5 * self.width,
            projected_vector[1] * 0.5 * self.height
        )


class Transformer:
    def __init__(self, projector):
        self.projector = projector
        self.rotation_matrix = np.zeros((3,3))
    
    @staticmethod
    def create_rotation_matrix(angle):
        angle_x, angle_y, angle_z = angle

        def create_rotation_matrix_x(angle):
            cos_theta, sin_theta = np.cos(angle), np.sin(angle)
            return np.array([
                [1, 0, 0],
                [0, cos_theta, -sin_theta],
                [0, sin_theta, cos_theta]
            ])

        def create_rotation_matrix_y(angle):
            cos_theta, sin_theta = np.cos(angle), np.sin(angle)
            return np.array([
                [cos_theta, 0, sin_theta],
                [0, 1, 0],
                [-sin_theta, 0, cos_theta]
            ])

        def create_rotation_matrix_z(angle):
            cos_theta, sin_theta = np.cos(angle), np.sin(angle)
            return np.array([
                [cos_theta, -sin_theta, 0],
                [sin_theta, cos_theta, 0],
                [0, 0, 1]
            ])
    
        return create_rotation_matrix_x(angle_x) @ create_rotation_matrix_y(angle_y) @ create_rotation_matrix_z(angle_z)

    
    @staticmethod
    def transform_vector(rotation_matrix, vertex): # adjust this so that the rotation matrix is input 
        rotated_vertex = rotation_matrix @ vertex 
        translated_vertex = rotated_vertex + np.array([0, 0, 8]) 
        return translated_vertex

class CubeManager:
    def __init__(self, cube_string= 'WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY'):

        self.cube = cube.CubieCube(cube_string)

        self.outer_rectangles = []
        self.faces = []

        self.frames_per_rotation = 60
        self.rotating = self.rotation_to_execute = False

        self.renderer = Renderer()
        self.projector = Projector(self.renderer.width, self.renderer.height)
        self.transformer = Transformer(self.projector)
        
        self.cubes = [Cube([i/2, j/2, k/2]) for i in range(-3, 3, 2) for j in range(-3, 3, 2) for k in range(-3, 3, 2)]
        self.process_cube_faces()

        self.angle_x = self.angle_y = self.angle_z = 0

        self.rotation_speed = 0.05

    def process_cube_faces(self):
        rectangles_to_sort = []

        for cube_index, cube in enumerate(self.cubes):
            for rect_index, rectangle in enumerate(cube.rectangles):
                centre = self.find_centre_rectangle(rectangle)
                dist = max(map(abs, centre))
                rectangles_to_sort.append([rectangle, dist, cube_index * 6 + rect_index, centre])

        # Sort rectangles by distance in descending order and select the top 54
        rectangles_to_sort.sort(key=lambda x: x[1], reverse=True)
        self.outer_rectangles = rectangles_to_sort[:54]
        self.set_colours()

    @staticmethod
    def find_centre_rectangle(rectangle):
        a, b, c, d = rectangle.corners
        return (a + b + c + d) / 4.0
    
    def set_colours(self):

        cube_string = str(cube.FaceletCube(self.cube))

        colour_map = Data.colour_map
        faces_dict = Data.faces_dict

        face_symbols  = ['U', 'F', 'L', 'R', 'B', 'D']
        for i, symbol in enumerate(face_symbols):
            face = []
            indices = faces_dict[symbol]
            for j, colour in enumerate(cube_string[i*9:(i+1)*9]):
                index = indices[j] - 1 
                rect_info = self.outer_rectangles[index][2]
                cube_index, rect_index = divmod(rect_info, 6)
                self.cubes[cube_index].rectangles[rect_index].piece_colour = colour_map[colour]
                
                face.append(self.cubes[cube_index])
            self.faces.append(face)
            
    def set_rotation(self, move):
        if not self.rotating:
            move_type = move % 6 
            turn_count = 1 + (move // 6)

            face = self.faces[move_type]
            c = [1, 2, -1][turn_count-1]
            if move_type in [Move.R, Move.D, Move.F]:
                c *= -1 

            if move_type in [Move.U, Move.D]:
                angle = [0,c,0]
            if move_type in [Move.L, Move.R]:
                angle = [c,0,0]
            if move_type in [Move.F, Move.B]:
                angle = [0,0,c]
            angle = np.multiply(angle, np.pi/2)

            self.rotating_face, self.move, self.target_angle, self.rotation_to_execute = face, move, angle, True
            return move, face, np.multiply(angle, np.pi/2)

    def rotate_face(self):
        # add varying rotation speed according to curve in animation 
        if not self.rotating:
            if self.rotation_to_execute:
                self.rotating = True
            self.current_frame = 0
            self.last_angle = 0
        else:
            if self.current_frame < self.frames_per_rotation:
                self.current_frame += 1 
                angle = (np.sin(np.pi * self.current_frame/(2*self.frames_per_rotation))) ** 0.8 * self.target_angle 
                
                rotation_matrix = Transformer.create_rotation_matrix(angle - self.last_angle)  # Adjust for specific axis
                self.last_angle = angle
            else: 
                #Reset rotation and apply new colours
                rotation_matrix = Transformer.create_rotation_matrix(-self.target_angle)

                self.cube.rotate_clockwise(self.move)
                self.set_colours()
                self.rotating = False 
                self.rotation_to_execute = False

            face = self.move % 6 
            for i, cube in enumerate(self.rotating_face):
                for j, rectangle in enumerate(cube.rectangles):

                    for k, corner in enumerate(rectangle.corners):
                        rotated_corner = corner @ rotation_matrix
                        self.faces[face][i].rectangles[j].corners[k] = rotated_corner

    def main(self):

        self.rotate_face()    
        self.renderer.clear_screen() # Clear the screen

        self.rotation_matrix = Transformer.create_rotation_matrix([self.angle_x, self.angle_y, self.angle_z])

        rectangles_to_draw = []
        index = 0
        for cube in self.cubes:
            for rectangle in cube.rectangles:
                rotating = self.rotating
                if not rotating and not rectangle.piece_colour:
                    continue
                if rectangle.piece_colour:
                    index += 1
                    
                transformed_vertices = []
                projected_vertices = []
            
                transformed_vertices = [Transformer.transform_vector(self.rotation_matrix, corner) for corner in rectangle.corners]
                transformed_rectangle = Rectangle(transformed_vertices)
                transformed_normal = transformed_rectangle.get_normal()

                reference = transformed_vertices[0] / np.linalg.norm(transformed_vertices[0])

                if np.dot(transformed_normal, reference) < 0:
                    projected_vertices = [self.projector.project_vector(vertex) for vertex in transformed_vertices]
                    centre = CubeManager.find_centre_rectangle(transformed_rectangle)

                    centroid_depth = np.linalg.norm(centre)
                    rectangles_to_draw.append((projected_vertices, rectangle.piece_colour, centroid_depth, index))
                
        # Sort rectangles by piece_colour and depth
        rectangles_to_draw.sort(key=lambda x: (isinstance(x[1], tuple), -x[2]))

        for rectangle, piece_colour, _, index in rectangles_to_draw:

            self.renderer.draw_rectangle(rectangle, piece_colour)
            self.renderer.add_displayed_quadrilateral(rectangle, index)
            
def main(cube_string ='WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY'):
    
    cube_manager = CubeManager(cube_string)

    clock = pygame.time.Clock()
    running = True
    while running:
        cube_manager.main()
        # Handle key presses for rotation
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            cube_manager.angle_y -= cube_manager.rotation_speed  # Rotate left around Y-axis
        if keys[K_RIGHT]:
            cube_manager.angle_y += cube_manager.rotation_speed  # Rotate right around Y-axis
        if keys[K_UP]:
            cube_manager.angle_x -= cube_manager.rotation_speed  # Rotate up around X-axis
        if keys[K_DOWN]:
            cube_manager.angle_x += cube_manager.rotation_speed  # Rotate down around X-axis
        if keys[K_z]:
            cube_manager.angle_z -= cube_manager.rotation_speed  # Rotate counterclockwise around Z-axis
        if keys[K_x]:
            cube_manager.angle_z += cube_manager.rotation_speed  # Rotate clockwise around Z-axis

        face_key_list = [K_u, K_f, K_l, K_r, K_b, K_d]
        move_number = next((i for i, val in enumerate(face_key_list) if keys[val]), None)
        if move_number != None:
            move = Move(move_number)
            if keys[K_LSHIFT]:
                move += 12 # Turns into counter-clockwise
            if keys[K_LCTRL]:
                move += 6 # Turns into double move
            cube_manager.set_rotation(move)

        cube_manager.main()
        fps = clock.get_fps()
        cube_manager.renderer.display_fps(fps)

        pygame.display.flip()

        clock.tick(60)

        running = cube_manager.renderer.update()

    # Clear all events and terminate the program 
    pygame.event.clear()
    pygame.quit()

if __name__ == "__main__":
    main()


# next move is to tidy up subroutines 
# then refactor code to remove transformer class, and projector. 
# add general code to set the rotation of the whole cube. / rotate the whole cube towards a target. 
# add code to call face turns, using move. 
# then move all pygame logic into a diff file which can call main. 
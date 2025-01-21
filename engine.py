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
        
        self.faces_clicked = []

    def detect_facelet_click(self, mouse_pos):
        
        def is_point_inside_triangle(A, B, C, P):
            v0, v1, v2 = C - A, B - A, P - A
            dot00, dot01, dot02, dot11, dot12 = np.dot(v0, v0), np.dot(v0, v1), np.dot(v0, v2), np.dot(v1, v1), np.dot(v1, v2)
            invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
            u, v = (dot11 * dot02 - dot01 * dot12) * invDenom, (dot00 * dot12 - dot01 * dot02) * invDenom
            return u >= 0 and v >= 0 and u + v <= 1
    
        def is_point_inside_quadrilateral(corners, P):
            A, B, C, D, = [np.array(i) for i in corners]
            P = np.array(P)
            return is_point_inside_triangle(A, B, C, P) or is_point_inside_triangle(A, C, D, P)
        
        for i, quad in enumerate(self.displayed_quadrilaterals): 
            if is_point_inside_quadrilateral(quad, mouse_pos):
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
        self.displayed_quadrilaterals, self.displayed_quadrilaterals_indices = [], []
    
    def draw_line(self, a, b, colour):
        pygame.draw.line(self.screen, colour, a, b, self.thickness*3)
    
    def draw_rectangle(self, corners, colour):
        if colour:
            pygame.draw.polygon(self.screen, colour, corners)
        else: 
            pygame.draw.polygon(self.screen, 'black', corners)
        pygame.draw.polygon(self.screen, 'black', corners, self.thickness*2)

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
    def transform_vector(rotation_matrix, vertex):
        rotated_vertex = rotation_matrix @ vertex 
        translated_vertex = rotated_vertex + np.array([0, 0, 8]) 
        return translated_vertex

class CubeManager:
    def __init__(self, cube_string):

        self.cube = cube.CubieCube(cube_string)

        self.highlighted_facelets = []
        self.outer_rectangles = []
        self.faces = []

        self.frames_per_face_turn = 60
        self.face_turning = self.face_turn_to_execute = False
        self.cube_rotating = self.cube_rotation_to_execute = False

        self.renderer = Renderer()
        self.projector = Projector(self.renderer.width, self.renderer.height)
        self.transformer = Transformer(self.projector)
        
        self.cubes = [Cube([i/2, j/2, k/2]) for i in range(-3, 3, 2) for j in range(-3, 3, 2) for k in range(-3, 3, 2)]
        self.process_cube_faces()

        self.angle_x = self.angle_y = self.angle_z = 0
        self.current_cube_rotation_angle = [0,0,0]

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
        colour_map = {
            'R': (255, 0, 0),       # Red
            'O': (255, 100, 0),     # Orange
            'Y': (255, 255, 0),     # Yellow
            'W': (255, 255, 255),   # White
            'G': (0, 187, 0),       # Green
            'B': (0, 0, 187),       # Blue
        }
        

        faces_array = [52, 32, 19, 49, 30, 16, 47, 29, 14,
                       46, 28, 13, 41, 26, 8, 33, 21, 0,
                       53, 50, 48, 45, 43, 42, 40, 37, 35,
                       15, 17, 20, 9, 10, 12, 2, 4, 7,
                       18, 31, 51, 11, 27, 44, 5, 24, 38,
                       34, 22, 1, 36, 23, 3, 39, 25, 6]

        for face in range(6):
            face_cubes = []
            for face_facelet in range(9):
                index = face * 9 + face_facelet
                facelet_index_in_rectangles = faces_array[index]
                facelet_colour = cube_string[index]

                idx = self.outer_rectangles[facelet_index_in_rectangles][2]
                cube_index = idx // 6 
                rect_index = idx % 6             
                self.cubes[cube_index].rectangles[rect_index].piece_colour = colour_map[facelet_colour]
                face_cubes.append(self.cubes[cube_index])
            self.faces.append(face_cubes)

    def change_cube_rotation(self, angle_delta):
        if self.cube_rotating:
            return False
        self.current_cube_rotation_angle = [
            ((self.current_cube_rotation_angle[i] + angle_delta[i] + np.pi) % (2 * np.pi)) - np.pi
            for i in range(3)
        ]
        
    def set_cube_rotation(self, target_angle, frames_per_cube_rotation):
        if self.cube_rotating:
            return False
        self.cube_target_angle = np.array(target_angle)
        # Normalize target angle to ensure interpolation uses the shortest path
        self.cube_target_angle = ((self.cube_target_angle + np.pi) % (2 * np.pi)) - np.pi
        self.cube_rotation_to_execute = True
        self.frames_per_cube_rotation = frames_per_cube_rotation
        self.cube_initial_angle = np.copy(self.current_cube_rotation_angle)
        self.current_cube_rotation_frame = 0
        self.cube_rotating = True

    def interpolate_angles(self,start_angle, end_angle, factor):
        """Interpolate angles ensuring shortest rotation path."""
        delta = ((end_angle - start_angle + np.pi) % (2 * np.pi)) - np.pi
        return start_angle + factor * delta

    def get_cube_rotation_matrix(self):
        if not self.cube_rotating:
            return Transformer.create_rotation_matrix(self.current_cube_rotation_angle)
        
        if self.current_cube_rotation_frame < self.frames_per_cube_rotation:
            self.current_cube_rotation_frame += 1
            interpolation_factor = np.sin(np.pi * self.current_cube_rotation_frame / (2 * self.frames_per_cube_rotation))
            current_angle = [
                self.interpolate_angles(self.cube_initial_angle[i], self.cube_target_angle[i], interpolation_factor)
                for i in range(3)
            ]
            rotation_matrix = Transformer.create_rotation_matrix(current_angle)
        else:
            self.cube_rotating = False
            self.current_cube_rotation_angle = self.cube_target_angle
            rotation_matrix = Transformer.create_rotation_matrix(self.cube_target_angle)

        return rotation_matrix
    def set_cube_view(self, viewpoint, frames_per_cube_rotation = 120):

        qtr_pi = np.pi/4
        hlf_pi = np.pi/2
        eleven_sixteenths_pi = 11/16 * np.pi
        seven_sixteenths_pi = 7/32 * np.pi
        pi = np.pi

        corner_view_angles = [
            [-qtr_pi,qtr_pi,0],
            [-qtr_pi, -qtr_pi,0],
            [-qtr_pi, pi-qtr_pi, 0],
            [-qtr_pi, qtr_pi-pi,0],
            [qtr_pi, qtr_pi,0],
            [qtr_pi, -qtr_pi,0],
            [qtr_pi, pi-qtr_pi,0],
            [qtr_pi, qtr_pi-pi,0]
        ]

        edge_view_angles = [
            [-qtr_pi,0,0],
            [-qtr_pi,hlf_pi,0],
            [-qtr_pi, pi, 0],
            [-qtr_pi, -hlf_pi, 0],
            [qtr_pi,0,0],
            [qtr_pi, hlf_pi,0],
            [qtr_pi, pi,0],
            [qtr_pi, -hlf_pi,0], 
            [0,qtr_pi,0],
            [0,-qtr_pi,0], 
            [0,pi-qtr_pi,0], 
            [0,qtr_pi-pi,0]
        ]
    
        face_view_angles = [
            [-hlf_pi,0 ,0],
            [0,0,0],
            [0, hlf_pi,0],
            [0,-hlf_pi,0],
            [0,pi,0],
            [hlf_pi,0,0]
        ]

        move_view_angles = [
            [-qtr_pi,0,0],
            [-qtr_pi,0,0],
            [-qtr_pi,seven_sixteenths_pi,0],
            [-qtr_pi,-seven_sixteenths_pi, 0],
            [-eleven_sixteenths_pi,0,0],
            [3/16 * pi,0,0]
        ]

        if isinstance(viewpoint, Face):
            viewing_angle = face_view_angles[viewpoint]
        elif isinstance(viewpoint, Edge):
            viewing_angle = edge_view_angles[viewpoint]
        elif isinstance(viewpoint, Corner):
            viewing_angle = corner_view_angles[viewpoint]
        elif isinstance(viewpoint, Move):
            viewing_angle = move_view_angles[viewpoint%6]
        else:
            raise    
        viewing_angle = [np.float64(i) for i in viewing_angle]
        if viewing_angle == self.current_cube_rotation_angle:
            return False
        self.set_cube_rotation(viewing_angle, frames_per_cube_rotation)
        return True 
    
    def set_face_turn(self, move):
        if self.face_turning:
            return False
    
        move_type = move % 6 
        turn_count = 1 + (move // 6)

        face = self.faces[move_type]
        clockwise = [1, 2, -1][turn_count-1]
        if move_type in [Move.R, Move.D, Move.F]:
            clockwise *= -1 

        if move_type in [Move.U, Move.D]:
            angle = [0,clockwise,0]
        if move_type in [Move.L, Move.R]:
            angle = [clockwise,0,0]
        if move_type in [Move.F, Move.B]:
            angle = [0,0,clockwise]
        angle = np.multiply(angle, np.pi/2)

        self.current_face_turn_frame = self.current_face_turn_angle = 0

        self.move, self.face_target_angle, self.face_turning = move, angle, True
        return move, face, np.multiply(angle, np.pi/2)

    def update_face_turns(self):
        # add varying rotation speed according to curve in animation 
        if not self.face_turning:
            return
        
        if self.move // 6 == 1:
            frames = self.frames_per_face_turn * 2 
        else: 
            frames = self.frames_per_face_turn

        if self.current_face_turn_frame < frames:
            self.current_face_turn_frame += 1 
            angle = (np.sin(np.pi * self.current_face_turn_frame/(2*frames))) * self.face_target_angle 
            rotation_matrix = Transformer.create_rotation_matrix(angle - self.current_face_turn_angle)
            self.current_face_turn_angle = angle
        else: 
            #Reset rotation and apply new colours
            rotation_matrix = Transformer.create_rotation_matrix(-self.face_target_angle)

            self.cube.move(self.move)
            self.set_colours()
            self.face_turning = False

        face = self.move % 6 
        for i, cube in enumerate(self.faces[face]):
            for j, rectangle in enumerate(cube.rectangles):

                for k, corner in enumerate(rectangle.corners):
                    rotated_corner = corner @ rotation_matrix
                    self.faces[face][i].rectangles[j].corners[k] = rotated_corner

    def main(self):

        self.update_face_turns()    
        self.renderer.clear_screen() # Clear the screen

        self.rotation_matrix = self.get_cube_rotation_matrix()

        rectangles_to_draw = []
        index = 0
        for cube in self.cubes:
            for rectangle in cube.rectangles:
                rotating = self.face_turning
                if not rotating and not rectangle.piece_colour:
                    continue
                    
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

                if rectangle.piece_colour:
                    index += 1
                
        # Sort rectangles by piece_colour and depth
        rectangles_to_draw.sort(key=lambda x: (isinstance(x[1], tuple), -x[2]))

        for rectangle, piece_colour, _, index in rectangles_to_draw:

            self.renderer.draw_rectangle(rectangle, piece_colour)
            self.renderer.add_displayed_quadrilateral(rectangle, index)


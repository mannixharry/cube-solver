from pygame.locals import *
from screen import Renderer
import cube
from data import * 
import numpy as np

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
    def __init__(self, width, height, fov=90):
        self.width, self.height = width, height
        self.fov = fov
        a = height / width
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        self.projection_matrix = np.array([
            [f, 0, 0],
            [0, f * a, 0],
            [0, 0, 1],
            
        ])

    def project_vector(self, vector):
        projected_vector = self.projection_matrix @ vector
        if projected_vector[2] != 0:
            projected_vector /= -projected_vector[2]
        projected_vector += np.array([1, 1, 0])
        return (
            projected_vector[0] * 0.5 * self.width,
            projected_vector[1] * 0.5 * self.height
        )


class Transformer:

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
    def transform_vector(rotation_matrix, vector):
        rotated_vector = rotation_matrix @ vector 
        translated_vector = rotated_vector + np.array([0, 0, 8]) 
        return translated_vector

class CubeManager:
    def __init__(self, cube_string, renderer):

        self.cube = cube.CubieCube(cube_string)

        self.highlighted_facelets = []
        self.outer_rectangles = []
        self.faces = []

        self.frames_per_face_turn = 30
        self.face_turning = self.face_turn_to_execute = False
        self.cube_rotating = self.cube_rotation_to_execute = False

        self.renderer = renderer
        self.renderer.clear_display_data()

        self.projector = Projector(self.renderer.width, self.renderer.height)
        self.transformer = Transformer()
        
        self.cubes = [Cube([i/2, j/2, k/2]) for i in range(-3, 3, 2) for j in range(-3, 3, 2) for k in range(-3, 3, 2)]
        self.process_cube_faces()

        self.angle_x = self.angle_y = self.angle_z = 0
        self.current_cube_rotation_angle = np.array([0,0,0])

    def update_cube(self, cube_string):
        #self.renderer.clear_display_data()

        self.highlighted_facelets = []
        self.outer_rectangles = []
        self.faces = []
        self.face_turning = self.face_turn_to_execute = False
        self.cube_rotating = self.cube_rotation_to_execute = False

        self.cube = cube.CubieCube(cube_string)
        self.cubes = [Cube([i/2, j/2, k/2]) for i in range(-3, 3, 2) for j in range(-3, 3, 2) for k in range(-3, 3, 2)]
        self.process_cube_faces()

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
    def set_cube_view(self, viewpoint, frames_per_cube_rotation = 60):

        qtr_pi = np.pi/4
        hlf_pi = np.pi/2
        eleven_sixteenths_pi = 11/16 * np.pi
        seven_sixteenths_pi = 7/32 * np.pi
        three_sixteenths_pi = 3/16 * np.pi
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
            [three_sixteenths_pi,0,0]
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

        if all([viewing_angle[i] == self.current_cube_rotation_angle[i] for i in range(3)]):
            return False
        self.set_cube_rotation(viewing_angle, frames_per_cube_rotation)
        return True 
    
    def set_face_turn(self, move, frames_per_face_turn = 30):
        self.frames_per_face_turn = frames_per_face_turn
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

    def get_clicked_facelet(self):
        return self.renderer.get_clicked_facelet()

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


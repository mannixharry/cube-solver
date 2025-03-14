from pygame.locals import *
import cube
from data import * 
import numpy as np

class Rectangle:
    def __init__(self, corners, piece_colour=False):
        
        self.corners = [np.array(corner) for corner in corners]
        self.piece_colour = piece_colour 

    def get_normal(self):
        a,  b, c, _ = self.corners
        normal = np.cross(b-a, c-a)
        normal /= np.linalg.norm(normal)
        return normal
    
class Cube:
    
    __colour_map = Data.colour_map
 
    def __init__(self, cube_string=None):
        
        self.facelets = []
        
        if cube_string is None:
            cube_string = str(cube.FaceletCube())
        elif isinstance(cube_string, cube.FaceletCube):
            cube_string = str(cube_string)
        
        f_face = [Rectangle([[0.5 - i, 1.5 - j, -1.5], [0.5 - i, 0.5 - j, -1.5],  
                      [1.5 - i, 0.5 - j, -1.5], [1.5 - i, 1.5 - j, -1.5]])  
          for j in range(3) for i in range(3)]

        pi = np.pi
        face_rotation_angles = [(pi/2, 0, 0), (0,0,0), (0, -pi/2, 0), (0, pi/2, 0), (0,pi,0), (-pi/2, 0, 0)]
        # Given in order UFLRBD

        for i, angle in enumerate(face_rotation_angles):
            rotation_matrix = Transformer.create_rotation_matrix(angle)
            face = []
            for j, rect in enumerate(f_face):
                colour = self.__colour_map[cube_string[i*9 + j]]
                face.append(Rectangle([(rotation_matrix @ i) for i in rect.corners], colour))
            self.facelets += face
             
class Projector:
    def __init__(self, width, height, fov=90):
        self.width, self.height = width, height
        self.fov = fov
        a = height / width
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        self.__projection_matrix = np.array([
            [f, 0, 0],
            [0, f * a, 0],
            [0, 0, 1],
            
        ])

    def project_vector(self, vector):
        projected_vector = self.__projection_matrix @ vector
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

        def __create_rotation_matrix_x(angle):
            cos_theta, sin_theta = np.cos(angle), np.sin(angle)
            return np.array([
                [1, 0, 0],
                [0, cos_theta, -sin_theta],
                [0, sin_theta, cos_theta]
            ])

        def __create_rotation_matrix_y(angle):
            cos_theta, sin_theta = np.cos(angle), np.sin(angle)
            return np.array([
                [cos_theta, 0, sin_theta],
                [0, 1, 0],
                [-sin_theta, 0, cos_theta]
            ])

        def __create_rotation_matrix_z(angle):
            cos_theta, sin_theta = np.cos(angle), np.sin(angle)
            return np.array([
                [cos_theta, -sin_theta, 0],
                [sin_theta, cos_theta, 0],
                [0, 0, 1]
            ])
    
        return __create_rotation_matrix_x(angle_x) @ __create_rotation_matrix_y(angle_y) @ __create_rotation_matrix_z(angle_z)

    @staticmethod
    def transform_vector(rotation_matrix, vector):
        rotated_vector = rotation_matrix @ vector 
        translated_vector = rotated_vector + np.array([0, 0, 8]) 
        return translated_vector

class CubeManager:
    
    __frames_per_face_turn = 30
    
    __current_cube_rotation_angle = np.array([0,0,0])
    
    def __init__(self, cube_string, renderer):

        self.renderer = renderer
        
        width, height = self.renderer.width, self.renderer.height
        self.projector = Projector(width, height)

        self.set_cube(cube_string)

    def set_cube(self, cube_string):
        
        self.face_turning = False
        self.cube_rotating = False

        self.cube = cube.CubieCube(cube_string)
        self.facelets = Cube(str(cube.FaceletCube(cube_string))).facelets
        
    def __find_centre_rectangle(self, rectangle):
        a, b, c, d = rectangle.corners
        return (a + b + c + d) / 4.0    

    def change_cube_rotation(self, angle_delta):
        if self.cube_rotating:
            return False
        self.__current_cube_rotation_angle = [
            ((self.__current_cube_rotation_angle[i] + angle_delta[i]) % (2 * np.pi))
            for i in range(3)
        ]
        
    def set_cube_rotation(self, target_angle, frames_per_cube_rotation):
        if self.cube_rotating:
            return False
        
        self.__cube_target_angle = ((np.array(target_angle) + np.pi) % (2 * np.pi)) - np.pi
        self.__frames_per_cube_rotation = frames_per_cube_rotation
        self.__cube_initial_angle = np.copy(self.__current_cube_rotation_angle)
        self.__current_cube_rotation_frame = 0
        self.cube_rotating = True

    def __interpolate_angles(self,initial_angle, target_angle, factor):
        delta = ((target_angle - initial_angle + np.pi)  % (2 * np.pi)) - np.pi # shift to inverval (0, 2pi), apply mod, then shift back to (-pi, pi)
        return initial_angle + factor * delta

    def __get_cube_rotation_matrix(self):
        if not self.cube_rotating:
            return Transformer.create_rotation_matrix(self.__current_cube_rotation_angle)
        
        if self.__current_cube_rotation_frame < self.__frames_per_cube_rotation:
            self.__current_cube_rotation_frame += 1
            interpolation_factor = np.sin(np.pi * self.__current_cube_rotation_frame / (2 * self.__frames_per_cube_rotation))
            current_angle = [self.__interpolate_angles(self.__cube_initial_angle[i], self.__cube_target_angle[i], interpolation_factor) for i in range(3)]
            rotation_matrix = Transformer.create_rotation_matrix(current_angle)
        else:
            self.cube_rotating = False
            self.__current_cube_rotation_angle = self.__cube_target_angle
            rotation_matrix = Transformer.create_rotation_matrix(self.__cube_target_angle)

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

        if all([viewing_angle[i] == self.__current_cube_rotation_angle[i] for i in range(3)]):
            return False
        self.set_cube_rotation(viewing_angle, frames_per_cube_rotation)
        return True 
    
    def set_face_turn(self, move, frames_per_face_turn = 30):
        self.__frames_per_face_turn = frames_per_face_turn
        if self.face_turning:
            return False
    
        move_type = move % 6 
        turn_count = 1 + (move // 6)

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

        self.__current_face_turn_frame = self.__current_face_turn_angle = 0

        self.__move, self.__face_target_angle, self.face_turning = move, angle, True
        return move, np.multiply(angle, np.pi/2)

    def __update_face_turns(self):
        
        slice_facelets = {
            'U': list(range(0,9)) + [9,10,11] + [18,19,20] + [27,28,29] + [36,37,38],
            'F': list(range(9,18)) + [6,7,8] + [20,23,26] + [27,30,33] + [45,46,47],
            'L': list(range(18,27)) + [0,3,6] + [9,12,15] + [38,41,44] + [45,48,51],
            'R': list(range(27,36)) + [2,5,8] + [11,14,17] + [36,39,42] + [47,50,53],
            'B': list(range(36,45)) + [0,1,2] + [18,21,24] + [29,32,35] + [51,52,53],
            'D': list(range(45,54)) + [15,16,17] + [24,25,26] + [33,34,35] + [42,43,44]
        }
                 
        if not self.face_turning:
            return
        
        if self.__move // 6 == 1:
            frames = self.__frames_per_face_turn * 2 
        else: 
            frames = self.__frames_per_face_turn

        if self.__current_face_turn_frame < frames:
            self.__current_face_turn_frame += 1 
            angle = (np.sin(np.pi * self.__current_face_turn_frame / (2 * frames))) * self.__face_target_angle 
            face_rotation_matrix = Transformer.create_rotation_matrix(angle - self.__current_face_turn_angle)
            self.__current_face_turn_angle = angle
            
            face = self.__move % 6 
            for facelet in slice_facelets['UFLRBD'[face]]:
                rectangle = self.facelets[facelet]
                for j, corner in enumerate(rectangle.corners):
                    rotated_corner = corner @ face_rotation_matrix
                    self.facelets[facelet].corners[j] = rotated_corner
        else: 
            #Reset rotation and apply new colours
            self.cube.move(self.__move)
            cube_string = str(cube.FaceletCube(self.cube))
            
            self.set_cube(cube_string)
            
    def get_clicked_facelet(self):
        return self.renderer.get_clicked_facelet()

    def main(self):

        self.__update_face_turns()    
        
        self.renderer.clear_screen() # Clear the screen
        cube_rotation_matrix = self.__get_cube_rotation_matrix()

        rectangles_to_draw = []
        index = 0
        for rectangle in np.array(self.facelets):
                rotating = self.face_turning
                if not rotating and not rectangle.piece_colour:
                    continue
                    
                transformed_vertices = []
                projected_vertices = []
            
                transformed_vertices = [Transformer.transform_vector(cube_rotation_matrix, corner) for corner in rectangle.corners]
                transformed_rectangle = Rectangle(transformed_vertices)
                transformed_normal = transformed_rectangle.get_normal()

                reference = transformed_vertices[0]  # direction vector towards point

                piece_colour = rectangle.piece_colour if np.dot(transformed_normal, reference) > 0 else (0,0,0)
                
                projected_vertices = [self.projector.project_vector(vertex) for vertex in transformed_vertices]
                centre = self.__find_centre_rectangle(transformed_rectangle)
                centroid_depth = centre[2]
                
                rectangles_to_draw.append((projected_vertices, piece_colour, centroid_depth, index))

                index += 1
                
        # Sort rectangles by depth
        rectangles_to_draw.sort(key=lambda x: -x[2])

        for rectangle, piece_colour, _, index in rectangles_to_draw:

            self.renderer.draw_rectangle(rectangle, piece_colour)
            self.renderer.add_displayed_quadrilateral(rectangle, index)

import numpy as np
from pygame.locals import *

from . import cube
from .data import *

class Rectangle:
    '''A rectangle in 3D space.'''

    def __init__(self, corners, piece_colour=False):
        '''
        Args:
            corners (List[np.array]): position vectors of the four corners, given anti-clockwise so
                the computed normal faces outwards (towards the camera) - needed for backface culling.
            piece_colour (Tuple[int, int, int]): display colour. Defaults to False.
        '''
        self.corners = [np.array(corner) for corner in corners]
        self.piece_colour = piece_colour

    def get_normal(self):
        '''Returns the unit normal to the plane containing the rectangle.'''
        a, b, c, _ = self.corners
        normal = np.cross(b - a, c - a)
        normal /= np.linalg.norm(normal)
        return normal

    def find_centre(self):
        '''Returns the position vector of the rectangle's centre.'''
        a, b, c, d = self.corners
        return (a + b + c + d) / 4.0

class Cube3D:
    '''Builds the 54 coloured facelet Rectangles that make up a rendered cube.

    Attributes:
        facelets (List[Rectangle]): the 54 facelet rectangles.
    '''
    __colour_map = Data.colour_map

    def __init__(self, cube_string=None):
        '''Builds one face as 9 Rectangles, then copies and rotates it 6 times to form the whole
        cube, colouring each facelet according to cube_string.

        Args:
            cube_string (FaceletCube, str, optional): input cube. Defaults to a solved cube.

        Raises:
            TypeError: cube_string does not match an expected type.
        '''
        self.facelets = []

        if cube_string is None:
            cube_string = str(cube.FaceletCube())
        elif isinstance(cube_string, cube.FaceletCube):
            cube_string = str(cube_string)
        elif isinstance(cube_string, str):
            cube_string = cube_string
        else:
            raise TypeError('Input cube_string is not of expected type')

        f_face = [Rectangle([[0.5 - i, 1.5 - j, -1.5], [0.5 - i, 0.5 - j, -1.5],
                      [1.5 - i, 0.5 - j, -1.5], [1.5 - i, 1.5 - j, -1.5]])
          for j in range(3) for i in range(3)]

        pi = np.pi
        face_rotation_angles = [(pi / 2, 0, 0), (0, 0, 0), (0, -pi / 2, 0), (0, pi / 2, 0), (0, pi, 0), (-pi / 2, 0, 0)]
        # Given in order UFLRBD

        for i, angle in enumerate(face_rotation_angles):
            rotation_matrix = Transformer.create_rotation_matrix(angle)
            face = []
            for j, rect in enumerate(f_face):
                colour = self.__colour_map[cube_string[i * 9 + j]]
                face.append(Rectangle([(rotation_matrix @ i) for i in rect.corners], colour))
            self.facelets += face

class Projector:
    '''Projects a 3D position vector onto a 2D screen coordinate.'''

    def __init__(self, width, height, fov=np.pi / 2):
        '''
        Args:
            width (int): screen width (pygame window).
            height (int): screen height.
            fov (float, optional): field of view. Defaults to 90 degrees.
        '''
        self.width, self.height = width, height
        self.fov = fov
        a = height / width
        f = 1.0 / np.tan(self.fov / 2.0)
        self.__projection_matrix = np.array([
            [f, 0, 0],
            [0, f * a, 0],
            [0, 0, 1],
        ])

    def project_vector(self, vector):
        '''Projects a 3D vector to a 2D screen coordinate.'''
        projected_vector = self.__projection_matrix @ vector
        if projected_vector[2] != 0:
            projected_vector /= -projected_vector[2]
        projected_vector += np.array([1, 1, 0])

        return (
            projected_vector[0] * 0.5 * self.width,
            projected_vector[1] * 0.5 * self.height,
        )

class Transformer:
    '''Rotates 3D position vectors about the origin.'''

    @staticmethod
    def create_rotation_matrix(angle):
        '''Builds a combined rotation matrix for angle.

        Args:
            angle (Tuple[float, float, float]): rotation about the X, Y and Z axes, in radians.

        Returns:
            np.ndarray: rotation matrix.
        '''
        angle_x, angle_y, angle_z = angle

        def __create_rotation_matrix_x(angle_x):
            cos_theta, sin_theta = np.cos(angle_x), np.sin(angle_x)
            return np.array([
                [1, 0, 0],
                [0, cos_theta, -sin_theta],
                [0, sin_theta, cos_theta]
            ])

        def __create_rotation_matrix_y(angle_y):
            cos_theta, sin_theta = np.cos(angle_y), np.sin(angle_y)
            return np.array([
                [cos_theta, 0, sin_theta],
                [0, 1, 0],
                [-sin_theta, 0, cos_theta]
            ])

        def __create_rotation_matrix_z(angle_z):
            cos_theta, sin_theta = np.cos(angle_z), np.sin(angle_z)
            return np.array([
                [cos_theta, -sin_theta, 0],
                [sin_theta, cos_theta, 0],
                [0, 0, 1]
            ])

        return __create_rotation_matrix_x(angle_x) @ __create_rotation_matrix_y(angle_y) @ __create_rotation_matrix_z(angle_z)

    @staticmethod
    def transform_vector(rotation_matrix, vector):
        '''Rotates vector by rotation_matrix and pushes it 8 units into the screen.'''
        rotated_vector = rotation_matrix @ vector
        return rotated_vector + np.array([0, 0, 8])

class CubeManager:
    '''Owns the rendered Cube3D: view/face-turn animation, projection, backface culling and depth
    sorting, handing the resulting rectangles to Renderer for display.

    Attributes:
        renderer (Renderer): renderer used to display the cube.
        cube (CubieCube): current cube state.
        face_turning (bool): True while a face-turn animation is in progress.
        cube_rotating (bool): True while a cube-rotation animation is in progress.
    '''

    __frames_per_face_turn = 30
    __frames_per_cube_rotation = 60

    __current_cube_rotation_angle = np.array([0, 0, 0])
    __cube_initial_angle = __cube_target_angle = 0
    __current_cube_rotation_frame = 0

    def __init__(self, cube_input, renderer):
        '''
        Args:
            cube_input (CubieCube, FaceletCube, str): initial cube state.
            renderer (Renderer): renderer to use (passed in so it isn't recreated on each new cube).
        '''
        self.renderer = renderer
        width, height = self.renderer.width, self.renderer.height
        self.__projector = Projector(width, height)
        self.set_cube(cube_input)

    def set_cube(self, cube_input):
        '''Loads a cube state.

        Args:
            cube_input (CubieCube, FaceletCube, str): cube state to load.
        '''
        self.face_turning = False
        self.cube_rotating = False

        self.cube = cube.CubieCube(cube_input)
        self.__facelets = Cube3D(str(cube.FaceletCube(cube_input))).facelets

    def change_cube_rotation(self, angle_delta):
        '''Adjusts the current view angle by angle_delta.

        Returns:
            bool: True; False if a rotation is already in progress.
        '''
        if self.cube_rotating:
            return False
        self.__current_cube_rotation_angle = [
            ((self.__current_cube_rotation_angle[i] + angle_delta[i]) % (2 * np.pi))
            for i in range(3)
        ]
        return True

    def set_cube_rotation(self, target_angle, frames_per_cube_rotation):
        '''Starts an animated rotation of the view towards target_angle.

        Args:
            target_angle (Tuple[float, float, float]): angle to rotate towards.
            frames_per_cube_rotation (int): number of frames the rotation should take.

        Returns:
            bool: True; False if a rotation is already in progress.
        '''
        if self.cube_rotating:
            return False

        self.__cube_target_angle = ((np.array(target_angle) + np.pi) % (2 * np.pi)) - np.pi
        self.__frames_per_cube_rotation = frames_per_cube_rotation
        self.__cube_initial_angle = np.copy(self.__current_cube_rotation_angle)
        self.__current_cube_rotation_frame = 0
        self.cube_rotating = True

        return True

    def __interpolate_angles(self, initial_angle, target_angle, factor):
        '''Linearly interpolates factor of the way from initial_angle to target_angle, taking the
        shortest route between the two.
        '''
        delta = ((target_angle - initial_angle + np.pi) % (2 * np.pi)) - np.pi
        return initial_angle + factor * delta

    def __get_cube_rotation_matrix(self):
        '''Returns the view rotation matrix for the current frame.'''
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

    def set_cube_view(self, viewpoint, frames_per_cube_rotation=60):
        '''Starts an animated rotation towards a preset viewing angle for viewpoint.
        Most of the viewpoints besides Move are unused today but kept for future use.

        Args:
            viewpoint (Face, Edge, Corner, Move): the viewpoint to rotate towards.
            frames_per_cube_rotation (int, optional): frames the rotation should take. Defaults to 60.

        Returns:
            bool: True if a rotation was started; False if already at that view.
        '''
        pi = np.pi
        qtr_pi = np.pi / 4
        hlf_pi = np.pi / 2
        eleven_sixteenths_pi = 11 / 16 * np.pi
        seven_sixteenths_pi = 7 / 32 * np.pi
        three_sixteenths_pi = 3 / 16 * np.pi

        corner_view_angles = [
            (-qtr_pi, qtr_pi, 0),
            (-qtr_pi, -qtr_pi, 0),
            (-qtr_pi, pi - qtr_pi, 0),
            (-qtr_pi, qtr_pi - pi, 0),
            (qtr_pi, qtr_pi, 0),
            (qtr_pi, -qtr_pi, 0),
            (qtr_pi, pi - qtr_pi, 0),
            (qtr_pi, qtr_pi - pi, 0)
        ]

        edge_view_angles = [
            (-qtr_pi, 0, 0),
            (-qtr_pi, hlf_pi, 0),
            (-qtr_pi, pi, 0),
            (-qtr_pi, -hlf_pi, 0),
            (qtr_pi, 0, 0),
            (qtr_pi, hlf_pi, 0),
            (qtr_pi, pi, 0),
            (qtr_pi, -hlf_pi, 0),
            (0, qtr_pi, 0),
            (0, -qtr_pi, 0),
            (0, pi - qtr_pi, 0),
            (0, qtr_pi - pi, 0)
        ]

        face_view_angles = [
            (-hlf_pi, 0, 0),
            (0, 0, 0),
            (0, hlf_pi, 0),
            (0, -hlf_pi, 0),
            (0, pi, 0),
            (hlf_pi, 0, 0)
        ]

        move_view_angles = [
            (-qtr_pi, 0, 0),
            (-qtr_pi, 0, 0),
            (-qtr_pi, seven_sixteenths_pi, 0),
            (-qtr_pi, -seven_sixteenths_pi, 0),
            (-eleven_sixteenths_pi, 0, 0),
            (three_sixteenths_pi, 0, 0)
        ]

        if isinstance(viewpoint, Face):
            viewing_angle = face_view_angles[viewpoint]
        elif isinstance(viewpoint, Edge):
            viewing_angle = edge_view_angles[viewpoint]
        elif isinstance(viewpoint, Corner):
            viewing_angle = corner_view_angles[viewpoint]
        elif isinstance(viewpoint, Move):
            viewing_angle = move_view_angles[viewpoint % 6]
        else:
            raise TypeError('viewpoint is not of expected type')
        viewing_angle = [np.float64(i) for i in viewing_angle]

        if all(viewing_angle[i] == self.__current_cube_rotation_angle[i] for i in range(3)):
            return False
        self.set_cube_rotation(viewing_angle, frames_per_cube_rotation)
        return True

    def set_face_turn(self, move, frames_per_face_turn=30):
        '''Starts an animated face turn.

        Args:
            move (Move): move to perform.
            frames_per_face_turn (int, optional): frames the turn should take. Defaults to 30.

        Returns:
            bool: True; False if a face is already turning.
        '''
        self.__frames_per_face_turn = frames_per_face_turn
        if self.face_turning:
            return False

        move_type = move % 6
        turn_count = 1 + (move // 6)

        clockwise = [1, 2, -1][turn_count - 1]
        if move_type in [Move.R, Move.D, Move.F]:
            clockwise *= -1

        if move_type in [Move.U, Move.D]:
            angle = (0, clockwise, 0)
        if move_type in [Move.L, Move.R]:
            angle = (clockwise, 0, 0)
        if move_type in [Move.F, Move.B]:
            angle = (0, 0, clockwise)
        angle = np.multiply(angle, np.pi / 2)

        self.__current_face_turn_frame = self.__current_face_turn_angle = 0
        self.__move, self.__face_target_angle, self.face_turning = move, angle, True
        return True

    def __update_face_turns(self):
        '''Advances a face-turn animation by one frame, applying the cube move once it completes.'''
        slice_facelets = {
            'U': list(range(0, 9)) + [9, 10, 11] + [18, 19, 20] + [27, 28, 29] + [36, 37, 38],
            'F': list(range(9, 18)) + [6, 7, 8] + [20, 23, 26] + [27, 30, 33] + [45, 46, 47],
            'L': list(range(18, 27)) + [0, 3, 6] + [9, 12, 15] + [38, 41, 44] + [45, 48, 51],
            'R': list(range(27, 36)) + [2, 5, 8] + [11, 14, 17] + [36, 39, 42] + [47, 50, 53],
            'B': list(range(36, 45)) + [0, 1, 2] + [18, 21, 24] + [29, 32, 35] + [51, 52, 53],
            'D': list(range(45, 54)) + [15, 16, 17] + [24, 25, 26] + [33, 34, 35] + [42, 43, 44]
        }

        if not self.face_turning:
            return

        if self.__move // 6 == 1:
            frames = self.__frames_per_face_turn * 2
        else:
            frames = self.__frames_per_face_turn

        if self.__current_face_turn_frame < frames:
            self.__current_face_turn_frame += 1
            factor = np.sin(np.pi * self.__current_face_turn_frame / (2 * frames))
            angle = factor * self.__face_target_angle
            face_rotation_matrix = Transformer.create_rotation_matrix(angle - self.__current_face_turn_angle)
            self.__current_face_turn_angle = angle

            face = self.__move % 6
            for facelet in slice_facelets['UFLRBD'[face]]:
                rectangle = self.__facelets[facelet]
                for j, corner in enumerate(rectangle.corners):
                    rectangle.corners[j] = corner @ face_rotation_matrix
        else:
            # Turn animation complete: apply the real move and reload with the new colours.
            self.cube.move(self.__move)
            cube_string = str(cube.FaceletCube(self.cube))
            self.set_cube(cube_string)

    def main(self):
        '''Main engine loop: advances animations, culls backfacing rectangles, depth-sorts and
        draws the remaining ones.
        '''
        self.__update_face_turns()

        self.renderer.clear_screen()
        cube_rotation_matrix = self.__get_cube_rotation_matrix()

        to_draw = []
        for index, rectangle in enumerate(self.__facelets):
            transformed_vertices = [Transformer.transform_vector(cube_rotation_matrix, corner) for corner in rectangle.corners]
            transformed_rectangle = Rectangle(transformed_vertices)
            transformed_normal = transformed_rectangle.get_normal()

            reference = transformed_vertices[0]  # direction vector towards the rectangle
            piece_colour = rectangle.piece_colour if np.dot(transformed_normal, reference) > 0 else (0, 0, 0)

            projected_vertices = [self.__projector.project_vector(vertex) for vertex in transformed_vertices]
            centroid_depth = transformed_rectangle.find_centre()[2]

            to_draw.append((projected_vertices, piece_colour, centroid_depth, index))

        to_draw.sort(key=lambda x: -x[2])  # farthest first

        for quadrilateral, piece_colour, _, index in to_draw:
            self.renderer.draw_quadrilateral(quadrilateral, piece_colour)
            self.renderer.add_displayed_quadrilateral(quadrilateral, index)

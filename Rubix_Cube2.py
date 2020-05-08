import pygame
import pygame.gfxdraw
import math
from math import sqrt, cos, sin, atan, atan2
import random
import copy

traceList = []

Red = 255, 0, 0
Green = 0, 255, 0
Blue = 0, 0, 255
Black = 0, 0, 0
Yellow = 255, 255, 0
Orange = 255, 100, 0
White = 255, 255, 255
LightGrey = 200, 200, 200


class MinCube:
    def __init__(self, point_dict, faces, face_col_list=None):
        self.pointDict = point_dict
        self.faces = faces
        if face_col_list is None:
            self.faceColList = [(random.randint(127, 255), random.randint(127, 255), random.randint(127, 255)) for _ in
                                range(len(faces))]
        else:
            self.faceColList = face_col_list

    def render(self, specificRotationMatrix, rotationOffset):
        colourCoordinationCounter = 0
        for face in self.faces:
            if clockwise([flatten(self.pointDict[face[n]], specificRotationMatrix, rotationOffset) for n in range(3)]):
                # Draw the coloured-in shape
                pygame.draw.polygon(screen, self.faceColList[colourCoordinationCounter],
                                    [flatten(self.pointDict[face[n]], specificRotationMatrix,
                                             rotationOffset) for n in range(len(face))])

                # Draw the associated borders
                for pointCounter in range(len(face)):
                    pa = self.pointDict[face[pointCounter]]
                    pb = self.pointDict[face[(pointCounter + 1) % len(face)]]

                    start = flatten(pa, specificRotationMatrix, rotationOffset)
                    end = flatten(pb, specificRotationMatrix, rotationOffset)
                    drawAntialiasedLine(start[0], start[1], end[0], end[1], LightGrey, 1)
            colourCoordinationCounter += 1


def flatten(triple, rot_matrix, rot_offset):
    """
    Takes 3D coordinates, rotates them, and turns them into 2D coordinates.
    """
    a = rot_offset[0] + triple[0]
    b = rot_offset[1] + triple[1]
    c = rot_offset[2] + triple[2]
    a, b, c = matrix_multiply([a, b, c], rot_matrix)
    a -= rot_offset[0]
    b -= rot_offset[1]
    c -= rot_offset[2]

    n = globalZoom + c / 99000
    a = ((a * n) + (250 * (1 - n)))
    b = ((b * n) + (250 * (1 - n)))

    return a, b


def matrix_multiply(triple, rot_matrix):
    """Multiplies a 3D vector with a rotation matrix"""
    return rot_matrix[0][0] * triple[0] + rot_matrix[0][1] * triple[1] + rot_matrix[0][2] * triple[2], \
           rot_matrix[1][0] * triple[0] + rot_matrix[1][1] * triple[1] + rot_matrix[1][2] * triple[2], \
           rot_matrix[2][0] * triple[0] + rot_matrix[2][1] * triple[1] + rot_matrix[2][2] * triple[2]


def make_matrix_from_theta_and_axis(theta: float, axis: list):
    """Generates a rotation matrix given an axis and an angle."""
    n1 = axis[0]
    n2 = axis[1]
    n3 = axis[2]
    # http://scipp.ucsc.edu/~haber/ph216/rotation_12.pdf
    output = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    output[0][0] = math.cos(theta) + (n1 ** 2) * (1 - math.cos(theta))
    output[0][1] = (n1 * n2 * (1 - math.cos(theta))) - (n3 * math.sin(theta))
    output[0][2] = (n1 * n3 * (1 - math.cos(theta))) + (n2 * math.sin(theta))
    output[1][0] = (n1 * n2 * (1 - math.cos(theta))) + (n3 * math.sin(theta))
    output[1][1] = math.cos(theta) + ((n2 ** 2) * (1 - math.cos(theta)))
    output[1][2] = (n2 * n3 * (1 - math.cos(theta))) - (n1 * math.sin(theta))
    output[2][0] = (n1 * n3 * (1 - math.cos(theta))) - (n2 * math.sin(theta))
    output[2][1] = (n2 * n3 * (1 - math.cos(theta))) + (n1 * math.sin(theta))
    output[2][2] = math.cos(theta) + ((n3 ** 2) * (1 - math.cos(theta)))
    return output


def clockwise(points3: list):
    """Takes an ordered set of 2D points and works out whether or not they are clockwise."""
    dx1, dx2 = points3[1][0] - points3[0][0], points3[2][0] - points3[1][0]
    dy1, dy2 = points3[1][1] - points3[0][1], points3[2][1] - points3[1][1]

    try:
        angle_a, angle_b = atan(dy1 / dx1) + (math.pi / 2), atan(dy2 / dx2) + (math.pi / 2)
    except ZeroDivisionError:
        return False

    if dx1 < 0:
        angle_a += math.pi
    if dx2 < 0:
        angle_b += math.pi

    return math.pi > angle_b - angle_a > 0 or math.pi * -1 > angle_b - angle_a > math.pi * -2


def matrix_m_with_matrix(a: list, b: list):
    """Multiplies two 3*3 matrices."""
    output = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    output[0][0] = sum([(c[0] * c[1]) for c in zip(a[0], [d[0] for d in b])])
    output[0][1] = sum([(c[0] * c[1]) for c in zip(a[0], [d[1] for d in b])])
    output[0][2] = sum([(c[0] * c[1]) for c in zip(a[0], [d[2] for d in b])])

    output[1][0] = sum([(c[0] * c[1]) for c in zip(a[1], [d[0] for d in b])])
    output[1][1] = sum([(c[0] * c[1]) for c in zip(a[1], [d[1] for d in b])])
    output[1][2] = sum([(c[0] * c[1]) for c in zip(a[1], [d[2] for d in b])])

    output[2][0] = sum([(c[0] * c[1]) for c in zip(a[1], [d[0] for d in b])])
    output[2][1] = sum([(c[0] * c[1]) for c in zip(a[1], [d[1] for d in b])])
    output[2][2] = sum([(c[0] * c[1]) for c in zip(a[1], [d[2] for d in b])])
    return output


def drawAntialiasedLine(x1, y1, x2, y2, colour, thickness):
    """Alternative to pygame.draw.line that incorporates some anti-aliasing techniques."""
    # With thanks to Yannis Assael: https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line
    centre = ((x1 + x2) // 2, (y1 + y2) // 2)
    length = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    angle = atan2(y1 - y2, x1 - x2)

    UL = (centre[0] + (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          centre[1] + (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    UR = (centre[0] - (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          centre[1] + (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))
    BL = (centre[0] + (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          centre[1] - (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    BR = (centre[0] - (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          centre[1] - (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))

    pygame.gfxdraw.aapolygon(screen, (UL, UR, BR, BL), colour)
    pygame.gfxdraw.filled_polygon(screen, (UL, UR, BR, BL), colour)


# Generates the mapping for point coordinates.
pDict = {}
m = 0
for x in range(4):
    for y in range(4):
        for z in range(4):
            pDict[m] = [100 + (x * 100), 100 + (y * 100), 100 + (z * 100)]
            m += 1

# Generates the pieces, with their faces and colours.

redYellowBlue = MinCube(copy.deepcopy(pDict), [[4, 5, 1, 0], [0, 1, 17, 16], [20, 4, 0, 16]],
                        face_col_list=[Red, Blue, Yellow])
yellowBlue = MinCube(copy.deepcopy(pDict), [[36, 20, 16, 32], [16, 17, 33, 32]],
                     face_col_list=[Yellow, Blue])
orangeYellowBlue = MinCube(copy.deepcopy(pDict), [[48, 49, 53, 52], [52, 36, 32, 48], [32, 33, 49, 48]],
                           face_col_list=[Orange, Yellow, Blue])
yellow = MinCube(copy.deepcopy(pDict), [[40, 24, 20, 36]],
                 face_col_list=[Yellow])
redYellow = MinCube(copy.deepcopy(pDict), [[8, 9, 5, 4], [24, 8, 4, 20]],
                    face_col_list=[Red, Yellow])
orangeYellow = MinCube(copy.deepcopy(pDict), [[52, 53, 57, 56], [56, 40, 36, 52]],
                       face_col_list=[Orange, Yellow])
redYellowGreen = MinCube(copy.deepcopy(pDict), [[12, 13, 9, 8], [28, 12, 8, 24], [28, 29, 13, 12]],
                         face_col_list=[Red, Yellow, Green])
yellowGreen = MinCube(copy.deepcopy(pDict), [[44, 28, 24, 40], [44, 45, 29, 28]],
                      face_col_list=[Yellow, Green])
orangeYellowGreen = MinCube(copy.deepcopy(pDict), [[56, 57, 61, 60], [60, 61, 45, 44], [60, 44, 40, 56]],
                            face_col_list=[Orange, Green, Yellow])
blue = MinCube(copy.deepcopy(pDict), [[17, 18, 34, 33]],
               face_col_list=[Blue])
blueOrange = MinCube(copy.deepcopy(pDict), [[49, 50, 54, 53], [33, 34, 50, 49]],
                     face_col_list=[Orange, Blue])
redBlue = MinCube(copy.deepcopy(pDict), [[5, 6, 2, 1], [1, 2, 18, 17]],
                  face_col_list=[Red, Blue])
red = MinCube(copy.deepcopy(pDict), [[9, 10, 6, 5]],
              face_col_list=[Red])
orange = MinCube(copy.deepcopy(pDict), [[53, 54, 58, 57]],
                 face_col_list=[Orange])
orangeGreen = MinCube(copy.deepcopy(pDict), [[57, 58, 62, 61], [61, 62, 46, 45]],
                      face_col_list=[Orange, Green])
green = MinCube(copy.deepcopy(pDict), [[45, 46, 30, 29]],
                face_col_list=[Green])
redGreen = MinCube(copy.deepcopy(pDict), [[13, 14, 10, 9], [29, 30, 14, 13]],
                   face_col_list=[Red, Green])
blueOrangeWhite = MinCube(copy.deepcopy(pDict), [[50, 51, 55, 54], [34, 35, 51, 50], [51, 35, 39, 55]],
                          face_col_list=[Orange, Blue, White])
blueWhite = MinCube(copy.deepcopy(pDict), [[18, 19, 35, 34], [35, 19, 23, 39]],
                    face_col_list=[Blue, White])
blueWhiteRed = MinCube(copy.deepcopy(pDict), [[2, 3, 19, 18], [19, 3, 7, 23], [3, 2, 6, 7]],
                       face_col_list=[Blue, White, Red])
whiteRed = MinCube(copy.deepcopy(pDict), [[23, 7, 11, 55 - 28], [7, 6, 10, 11]],
                   face_col_list=[White, Red])
white = MinCube(copy.deepcopy(pDict), [[39, 23, 27, 43]],
                face_col_list=[White])
orangeGreenWhite = MinCube(copy.deepcopy(pDict), [[58, 59, 63, 62], [62, 63, 47, 46], [59, 43, 47, 63]],
                           face_col_list=[Orange, Green, White])
orangeWhite = MinCube(copy.deepcopy(pDict), [[54, 55, 59, 58], [55, 39, 43, 59]],
                      face_col_list=[Orange, White])
whiteGreen = MinCube(copy.deepcopy(pDict), [[43, 27, 31, 47], [47, 31, 30, 46]],
                     face_col_list=[White, Green])
whiteGreenRed = MinCube(copy.deepcopy(pDict), [[27, 11, 15, 31], [31, 15, 14, 30], [11, 10, 14, 15]],
                        face_col_list=[White, Green, Red])

shapes = [redYellowBlue, yellowBlue, orangeYellowBlue, yellow,
          redYellow, orangeYellow, redYellowGreen, yellowGreen,
          orangeYellowGreen, blue, blueOrange,
          redBlue, red, orange, orangeGreen, green, redGreen,
          blueOrangeWhite, blueWhite, blueWhiteRed, whiteRed, white,
          orangeGreenWhite, orangeWhite, whiteGreen, whiteGreenRed]

# Stores the move-codes, involved points, and rotation axes for the relevant key-presses.
operationalGroupDictionary = {
    pygame.K_b: ['B', [19, 18, 17, 20, 23, 24, 25, 22, 21], [0, 0, -1], [0, 0, 1]],
    pygame.K_r: ['R', [2, 11, 19, 22, 25, 16, 8, 5, 13], [-1, 0, 0], [1, 0, 0]],
    pygame.K_f: ['F', [0, 1, 2, 5, 8, 7, 6, 3, 4], [0, 0, 1], [0, 0, -1]],
    pygame.K_l: ['L', [0, 3, 6, 14, 23, 20, 17, 9, 12], [1, 0, 0], [-1, 0, 0]],
    pygame.K_u: ['U', [0, 9, 17, 18, 19, 11, 2, 1, 10], [0, -1, 0], [0, 1, 0]],
    pygame.K_d: ['D', [6, 7, 8, 16, 25, 24, 23, 14, 15], [0, 1, 0], [0, -1, 0]]}

# Stores the shape-numbers that will be reshuffled at the end of the rotation.
reShapingDictionary = {
    'B': ((17, 18, 19, 22, 25, 24, 23, 20), (19, 22, 25, 24, 23, 20, 17, 18)),
    'B-': ((25, 24, 23, 20, 17, 18, 19, 22), (19, 22, 25, 24, 23, 20, 17, 18)),
    'R': ((25, 16, 8, 5, 2, 11, 19, 22), (19, 22, 25, 16, 8, 5, 2, 11)),
    'R-': ((2, 11, 19, 22, 25, 16, 8, 5), (19, 22, 25, 16, 8, 5, 2, 11)),
    'F': ((8, 7, 6, 3, 0, 1, 2, 5), (2, 5, 8, 7, 6, 3, 0, 1)),
    'F-': ((0, 1, 2, 5, 8, 7, 6, 3), (2, 5, 8, 7, 6, 3, 0, 1)),
    'L': ((23, 20, 17, 9, 0, 3, 6, 14), (6, 14, 23, 20, 17, 9, 0, 3)),
    'L-': ((0, 3, 6, 14, 23, 20, 17, 9), (6, 14, 23, 20, 17, 9, 0, 3)),
    'U': ((17, 18, 19, 11, 2, 1, 0, 9), (0, 9, 17, 18, 19, 11, 2, 1)),
    'U-': ((2, 1, 0, 9, 17, 18, 19, 11), (0, 9, 17, 18, 19, 11, 2, 1)),
    'D': ((8, 16, 25, 24, 23, 14, 6, 7), (6, 7, 8, 16, 25, 24, 23, 14)),
    'D-': ((23, 14, 6, 7, 8, 16, 25, 24), (6, 7, 8, 16, 25, 24, 23, 14))}

# Stores the shape-number <-> shape references to be reshuffled.
shapePointers = {
    0: blueOrangeWhite,
    1: blueWhite,
    2: blueWhiteRed,
    3: orangeWhite,
    4: white,
    5: whiteRed,
    6: orangeGreenWhite,
    7: whiteGreen,
    8: whiteGreenRed,
    9: blueOrange,
    10: blue,
    11: redBlue,
    12: orange,
    13: red,
    14: orangeGreen,
    15: green,
    16: redGreen,
    17: orangeYellowBlue,
    18: yellowBlue,
    19: redYellowBlue,
    20: orangeYellow,
    21: yellow,
    22: redYellow,
    23: orangeYellowGreen,
    24: yellowGreen,
    25: redYellowGreen
}

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Rubix Cube simulation')

rotMatrix = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

debugging = False
scrambling = False
simPresses = None
sCount = 0
globalZoom = 0.8
operationalGroup = []
moveKey = None

pygame.font.init()
myf = pygame.font.SysFont('Avenir', 20)

if __name__ == "__main__":
    import main

    main.main_exit()

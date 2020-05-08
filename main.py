import time
import datetime
import sys
from Rubix_Cube2 import *

global debugging

pygame.font.init()
myf = pygame.font.SysFont('Avenir', 36, False)


def main_exit():
    sys.exit()


startTime = time.time()
running = True
thetaX = math.pi / 8
thetaY = -math.pi / 8 + math.pi
thetaZ = 0
dragging = False
startThetas = [0, 0]  # Necessary only for elimination of weak warning.
startPos = []
moving = False
moveAxis = [0, 0, 0]
moveAmount = 0
sCount = 0

simPresses = []
while running:
    # Input section
    movement = pygame.mouse.get_rel()
    pressed = pygame.key.get_pressed()
    for event in pygame.event.get() + simPresses:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                globalZoom += 0.05
            if event.key == pygame.K_l:
                globalZoom -= 0.05
            if event.key == pygame.K_s:
                scrambling = True
                sCount = 0
                startTime = time.time()
                print('--- Scrambling begin.')
            if event.key in operationalGroupDictionary:
                # Begin the face turn
                unPack = operationalGroupDictionary[event.key]
                moveKey = unPack[0]
                operationalGroup = [shapePointers[x] for x in unPack[1]]
                if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
                    # Move axis is different for clockwise and anticlockwise.
                    moveKey += '-'
                    moveAxis = unPack[2]
                else:
                    moveAxis = unPack[3]
                moving = True
                moveAmount = 0

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            startPos = event.pos
            startThetas = [thetaY, thetaX]

        if event.type == pygame.MOUSEMOTION and dragging:
            thetaY = startThetas[0] - (event.pos[0] - startPos[0]) / 100
            thetaX = startThetas[1] + (event.pos[1] - startPos[1]) / 100

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT]:
        thetaY -= 0.015
    if pressed[pygame.K_RIGHT]:
        thetaY += 0.015
    if pressed[pygame.K_UP]:
        thetaX += 0.015
    if pressed[pygame.K_DOWN]:
        thetaX -= 0.015
    if pressed[pygame.K_COMMA]:
        thetaZ -= 0.02
    if pressed[pygame.K_PERIOD]:
        thetaZ += 0.02

    # Game logic

    if moving:
        moveAmount += 0.03

    if (moving and not -math.pi / 2 < moveAmount < math.pi / 2) or scrambling:
        # Finish a move.
        moveAmount = math.pi / 2
        moving = False
        if not scrambling:
            print(moveKey)

        rotMatrixA = make_matrix_from_theta_and_axis(thetaX, [1, 0, 0])
        rotMatrixB = make_matrix_from_theta_and_axis(thetaY, [0, 1, 0])
        rotMatrixC = make_matrix_from_theta_and_axis(thetaZ, [0, 0, 1])

        rotMatrix = matrix_m_with_matrix(rotMatrixA, rotMatrixB)
        rotMatrix = matrix_m_with_matrix(rotMatrixC, rotMatrix)

        operationalMatrix = make_matrix_from_theta_and_axis(moveAmount, moveAxis)

        for m in operationalGroup:
            for p in m.pointDict.keys():
                # Permanently move the pieces
                l = m.pointDict[p]
                l[0], l[1], l[2] = l[0] - 250, l[1] - 250, l[2] - 250
                l = matrix_multiply(m.pointDict[p], operationalMatrix)
                m.pointDict[p] = [l[0] + 250, l[1] + 250, l[2] + 250]
        try:
            store = [shapePointers[n] for n in reShapingDictionary[moveKey][1]]
            for n, x in enumerate(reShapingDictionary[moveKey][0]):
                shapePointers[x] = store[n]
        except KeyError:  # Sometimes the key shows up as None.
            pass

        moveAmount = 0
        moveAxis = [0, 0, 0]
        tG = []

    if scrambling:
        simPresses.append(pygame.event.Event(pygame.KEYDOWN,
                                             key=random.choice([pygame.K_l, pygame.K_r, pygame.K_u,
                                                                pygame.K_d, pygame.K_f, pygame.K_b])))
        sCount += 1
    if sCount > 30:
        sCount = 0
        scrambling = False
        moving = False
        simPresses = []
        print('--- Scrambling finished.')

    # Render section
    screen.fill(Black)

    rotMatrixA = make_matrix_from_theta_and_axis(thetaX, [1, 0, 0])
    rotMatrixB = make_matrix_from_theta_and_axis(thetaY, [0, 1, 0])
    rotMatrixC = make_matrix_from_theta_and_axis(thetaZ, [0, 0, 1])

    rotMatrix = matrix_m_with_matrix(rotMatrixA, rotMatrixB)
    rotMatrix = matrix_m_with_matrix(rotMatrixC, rotMatrix)

    operationalMatrix = matrix_m_with_matrix(rotMatrix, make_matrix_from_theta_and_axis(moveAmount, moveAxis))

    for shape in shapes:
        if shape in operationalGroup:
            shape.render(operationalMatrix, [-250, -250, -250])
        else:
            shape.render(rotMatrix, [-250, -250, -250])

    pygame.draw.line(screen, Red, (200, 470), (200 + math.cos(thetaZ) * 30, 470 + math.sin(thetaZ) * 30))
    pygame.draw.line(screen, Green, (300, 470), (300 + math.cos(thetaX) * 30, 470 + math.sin(thetaX) * 30))
    pygame.draw.line(screen, Blue, (400, 470), (400 + math.cos(thetaY) * 30, 470 + math.sin(thetaY) * 30))

    timerPlq = myf.render(str(datetime.timedelta(seconds=(int(time.time() - startTime)))), True, (255, 255, 255))
    screen.blit(timerPlq, (0, 0))

    pygame.display.flip()
pygame.quit()

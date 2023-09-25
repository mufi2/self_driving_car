import math
import pygame

class Car:
    def __init__(self, x, y, width, height, controlType, maxSpeed=3):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.speed = 0
        self.acceleration = 0.2
        self.maxSpeed = maxSpeed
        self.friction = 0.05
        self.angle = 0
        self.damaged = False

        if controlType != "DUMMY":
            self.sensor = Sensor(self)
        self.controls = Controls(controlType)

    def update(self, roadBorders, traffic):
        if not self.damaged:
            self.move()
            self.polygon = self.createPolygon()
            self.damaged = self.assessDamage(roadBorders, traffic)
        if hasattr(self, 'sensor'):
            self.sensor.update(roadBorders, traffic)

    def assessDamage(self, roadBorders, traffic):
        for roadBorder in roadBorders:
            if self.polysIntersect(self.polygon, roadBorder):
                return True
        for otherCar in traffic:
            if self.polysIntersect(self.polygon, otherCar.polygon):
                return True
        return False

    def createPolygon(self):
        points = []
        rad = math.hypot(self.width, self.height) / 2
        alpha = math.atan2(self.width, self.height)
        points.append({
            'x': self.x - math.sin(self.angle - alpha) * rad,
            'y': self.y - math.cos(self.angle - alpha) * rad
        })
        points.append({
            'x': self.x - math.sin(self.angle + alpha) * rad,
            'y': self.y - math.cos(self.angle + alpha) * rad
        })
        points.append({
            'x': self.x - math.sin(math.pi + self.angle - alpha) * rad,
            'y': self.y - math.cos(math.pi + self.angle - alpha) * rad
        })
        points.append({
            'x': self.x - math.sin(math.pi + self.angle + alpha) * rad,
            'y': self.y - math.cos(math.pi + self.angle + alpha) * rad
        })
        return points

    def move(self):
        if self.controls.forward:
            self.speed += self.acceleration
        if self.controls.reverse:
            self.speed -= self.acceleration

        if self.speed > self.maxSpeed:
            self.speed = self.maxSpeed
        if self.speed < -self.maxSpeed / 2:
            self.speed = -self.maxSpeed / 2

        if self.speed > 0:
            self.speed -= self.friction
        if self.speed < 0:
            self.speed += self.friction
        if abs(self.speed) < self.friction:
            self.speed = 0

        if self.speed != 0:
            flip = 1 if self.speed > 0 else -1
            if self.controls.left:
                self.angle += 0.03 * flip
            if self.controls.right:
                self.angle -= 0.03 * flip

        self.x -= math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def draw(self, screen, color):
        if self.damaged:
            pygame.draw.polygon(screen, (169, 169, 169), self.polygon)
        else:
            pygame.draw.polygon(screen, color, self.polygon)

        if hasattr(self, 'sensor'):
            self.sensor.draw(screen)
import random

class NeuralNetwork:
    def __init__(self, neuronCounts):
        self.levels = []
        for i in range(len(neuronCounts) - 1):
            self.levels.append(Level(neuronCounts[i], neuronCounts[i + 1]))

    #staticmethod
    def feedForward(givenInputs, network):
        outputs = Level.feedForward(givenInputs, network.levels[0])
        for i in range(1, len(network.levels)):
            outputs = Level.feedForward(outputs, network.levels[i])
        return outputs

class Level:
    def __init__(self, inputCount, outputCount):
        self.inputs = [0] * inputCount
        self.outputs = [0] * outputCount
        self.biases = [random.uniform(-1, 1) for _ in range(outputCount)]
        
        self.weights = [[random.uniform(-1, 1) for _ in range(outputCount)] for _ in range(inputCount)]

    #staticmethod
    def feedForward(givenInputs, level):
        for i in range(len(level.inputs)):
            level.inputs[i] = givenInputs[i]

        for i in range(len(level.outputs)):
            sum_val = 0
            for j in range(len(level.inputs)):
                sum_val += level.inputs[j] * level.weights[j][i]

            if sum_val > level.biases[i]:
                level.outputs[i] = 1
            else:
                level.outputs[i] = 0

        return level.outputs

class Controls:
    def __init__(self, controlType):
        self.forward = False
        self.left = False
        self.right = False
        self.reverse = False

        if controlType == "KEYS":
            self.addKeyboardListeners()
        elif controlType == "DUMMY":
            self.forward = True

    def addKeyboardListeners(self):
        keys = pygame.key.get_pressed()
        self.forward = keys[pygame.K_UP]
        self.left = keys[pygame.K_LEFT]
        self.right = keys[pygame.K_RIGHT]
        self.reverse = keys[pygame.K_DOWN]

class Sensor:
    def __init__(self, car):
        self.car = car
        self.rayCount = 5
        self.rayLength = 150
        self.raySpread = math.pi / 2

        self.rays = []
        self.readings = []

    def update(self, roadBorders, traffic):
        self.castRays()
        self.readings = []
        for ray in self.rays:
            self.readings.append(self.getReading(ray, roadBorders, traffic))

    def getReading(self, ray, roadBorders, traffic):
        touches = []

        for roadBorder in roadBorders:
            touch = self.getIntersection(ray[0], ray[1], roadBorder[0], roadBorder[1])
            if touch:
                touches.append(touch)

        for otherCar in traffic:
            poly = otherCar.polygon
            for j in range(len(poly)):
                value = self.getIntersection(ray[0], ray[1], poly[j], poly[(j + 1) % len(poly)])
                if value:
                    touches.append(value)

        if not touches:
            return None
        else:
            offsets = [touch['offset'] for touch in touches]
            minOffset = min(offsets)
            return [touch for touch in touches if touch['offset'] == minOffset][0]

    def castRays(self):
        self.rays = []
        for i in range(self.rayCount):
            rayAngle = self.lerp(self.raySpread / 2, -self.raySpread / 2, 0.5 if self.rayCount == 1 else i / (self.rayCount - 1)) + self.car.angle

            start = {'x': self.car.x, 'y': self.car.y}
            end = {
                'x': self.car.x - math.sin(rayAngle) * self.rayLength,
                'y': self.car.y - math.cos(rayAngle) * self.rayLength
            }
            self.rays.append([start, end])

    def draw(self, screen):
        for i in range(self.rayCount):
            end = self.rays[i][1]
            if self.readings[i]:
                end = self.readings[i]

            pygame.draw.line(screen, (255, 255, 0), (self.rays[i][0]['x'], self.rays[i][0]['y']), (end['x'], end['y']), 2)
            pygame.draw.line(screen, (0, 0, 0), (self.rays[i][1]['x'], self.rays[i][1]['y']), (end['x'], end['y']), 2)

    #staticmethod
    def lerp(A, B, t):
        return A + (B - A) * t

    #staticmethod
    def getIntersection(A, B, C, D):
        tTop = (D['x'] - C['x']) * (A['y'] - C['y']) - (D['y'] - C['y']) * (A['x'] - C['x'])
        uTop = (C['y'] - A['y']) * (A['x'] - B['x']) - (C['x'] - A['x']) * (A['y'] - B['y'])
        bottom = (D['y'] - C['y']) * (B['x'] - A['x']) - (D['x'] - C['x']) * (B['y'] - A['y'])

        if bottom != 0:
            t = tTop / bottom
            u = uTop / bottom
            if 0 <= t <= 1 and 0 <= u <= 1:
                return {
                    'x': A['x'] + (B['x'] - A['x']) * t,
                    'y': A['y'] + (B['y'] - A['y']) * t,
                    'offset': t
                }

        return None

def polysIntersect(poly1, poly2):
    for i in range(len(poly1)):
        for j in range(len(poly2)):
            touch = Sensor.getIntersection(poly1[i], poly1[(i + 1) % len(poly1)], poly2[j], poly2[(j + 1) % len(poly2)])
            if touch:
                return True
    return False

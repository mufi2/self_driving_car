import pygame
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)

# Utility function for collision
def doPolygonsIntersect(a, b):
    polygons = [a, b]
    minA, maxA = 0, 0
    projected = []
    for i in range(len(polygons)):
        polygon = polygons[i]
        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            p1 = polygon[i1]
            p2 = polygon[i2]
            normal = {'x': p2['y'] - p1['y'], 'y': p1['x'] - p2['x']} # Fixed this line
            minA, maxA = None, None
            for j in range(len(a)):
                projected = normal['x'] * a[j]['x'] + normal['y'] * a[j]['y']
                if minA is None or projected < minA:
                    minA = projected
                if maxA is None or projected > maxA:
                    maxA = projected
            minB, maxB = None, None
            for j in range(len(b)):
                projected = normal['x'] * b[j]['x'] + normal['y'] * b[j]['y']
                if minB is None or projected < minB:
                    minB = projected
                if maxB is None or projected > maxB:
                    maxB = projected
            if maxA < minB or maxB < minA:
                return False
    return True


# Road class
class Road:
    def __init__(self):
        self.width = 400
        self.laneNumber = 4
        self.laneWidth = self.width / self.laneNumber
        self.roadBorder = [{'x': -self.width / 2, 'y': HEIGHT}, {'x': self.width / 2, 'y': HEIGHT}, {'x': self.width / 2, 'y': 0}, {'x': -self.width / 2, 'y': 0}]
        self.middleLines = []
        for i in range(1, self.laneNumber):
            self.middleLines.append([{'x': i * self.laneWidth - self.width / 2, 'y': HEIGHT}, {'x': i * self.laneWidth - self.width / 2, 'y': 0}])

    def display(self, screen):
        pygame.draw.polygon(screen, WHITE, [(pt['x'] + WIDTH / 2, pt['y']) for pt in self.roadBorder], 5)
        for line in self.middleLines:
            pygame.draw.line(screen, WHITE, (line[0]['x'] + WIDTH / 2, line[0]['y']), (line[1]['x'] + WIDTH / 2, line[1]['y']), 3)

# Car class
class Car:
    def __init__(self, x, y, width, height):
        self.position = {'x': x, 'y': y}
        self.width = width
        self.height = height
        self.frontalArea = self.width * self.height
        self.dragCoefficient = 0.3
        self.speed = 0
        self.acceleration = 0.4
        self.turnSpeed = 5
        self.angle = 0
        self.color = GRAY
        self.hp = 100
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(GRAY)
        self.rect = self.surface.get_rect(center=(self.position['x'], self.position['y']))

    def move(self):
        self.speed += self.acceleration
        self.position['y'] -= self.speed * math.cos(math.radians(self.angle))
        self.position['x'] += self.speed * math.sin(math.radians(self.angle))

    def turn(self, direction):
        if direction == "left":
            self.angle += self.turnSpeed
        if direction == "right":
            self.angle -= self.turnSpeed

    def display(self, screen):
        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        self.rect = rotated_surface.get_rect(center=(self.position['x'], self.position['y']))
        screen.blit(rotated_surface, self.rect.topleft)

    def collision(self, road):
        if doPolygonsIntersect(self.getVertices(), road.roadBorder):
            self.color = WHITE
            self.hp -= 1
            return True
        return False

    def getVertices(self):
        angle = math.radians(self.angle)
        cosA = math.cos(angle)
        sinA = math.sin(angle)
        halfWidth = self.width / 2
        halfHeight = self.height / 2
        centerX = self.position['x']
        centerY = self.position['y']
        return [
            {'x': centerX + (halfWidth * cosA - halfHeight * sinA), 'y': centerY + (halfWidth * sinA + halfHeight * cosA)},
            {'x': centerX + (halfWidth * cosA + halfHeight * sinA), 'y': centerY + (halfWidth * sinA - halfHeight * cosA)},
            {'x': centerX + (-halfWidth * cosA + halfHeight * sinA), 'y': centerY + (-halfWidth * sinA - halfHeight * cosA)},
            {'x': centerX + (-halfWidth * cosA - halfHeight * sinA), 'y': centerY + (-halfWidth * sinA + halfHeight * cosA)}
        ]

# Game loop
def game():
    pygame.display.set_caption("Car Racing Game")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    road = Road()
    car = Car(WIDTH / 2, HEIGHT - 200, 50, 100)
    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            car.move()
        if keys[pygame.K_LEFT]:
            car.turn("left")
        if keys[pygame.K_RIGHT]:
            car.turn("right")
        road.display(screen)
        car.display(screen)
        car.collision(road)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    game()


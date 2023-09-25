import pygame
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LANE_COUNT = 3
ROAD_WIDTH = 200

# Colors
WHITE = (255, 255, 255)
LIGHTGRAY = (211, 211, 211)
DARKGRAY = (169, 169, 169)
BLUE = (0, 0, 255)

# Car class
class Car:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x - width / 2, y - height / 2, width, height)
        self.speed = 0
        self.acceleration = 0.2
        self.maxSpeed = 3
        self.friction = 0.05
        self.angle = 0

    def update(self, controls):
        if controls.forward:
            self.speed += self.acceleration
        if controls.reverse:
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
            if controls.left:
                self.angle += 0.03 * flip
            if controls.right:
                self.angle -= 0.03 * flip
        self.rect.x -= math.sin(self.angle) * self.speed
        self.rect.y -= math.cos(self.angle) * self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

# Controls class
class Controls:
    def __init__(self):
        self.forward = False
        self.left = False
        self.right = False
        self.reverse = False

# Road class
class Road:
    def __init__(self, x, width, lane_count=3):
        self.x = x
        self.width = width
        self.lane_count = lane_count

    def draw(self, screen):
        for i in range(1, self.lane_count):
            lane_x = self.x - (self.width / 2) + (i * (self.width / self.lane_count))
            pygame.draw.line(screen, WHITE, (lane_x, 0), (lane_x, SCREEN_HEIGHT), 5)

        pygame.draw.line(screen, WHITE, (self.x - self.width / 2, 0), (self.x - self.width / 2, SCREEN_HEIGHT), 5)
        pygame.draw.line(screen, WHITE, (self.x + self.width / 2, 0), (self.x + self.width / 2, SCREEN_HEIGHT), 5)

# Main function
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Self-driving car - No libraries")
    clock = pygame.time.Clock()

    car = Car(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100, 30, 50)
    controls = Controls()
    road = Road(SCREEN_WIDTH / 2, ROAD_WIDTH)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    controls.forward = True
                if event.key == pygame.K_DOWN:
                    controls.reverse = True
                if event.key == pygame.K_LEFT:
                    controls.left = True
                if event.key == pygame.K_RIGHT:
                    controls.right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    controls.forward = False
                if event.key == pygame.K_DOWN:
                    controls.reverse = False
                if event.key == pygame.K_LEFT:
                    controls.left = False
                if event.key == pygame.K_RIGHT:
                    controls.right = False

        car.update(controls)

        screen.fill(DARKGRAY)
        road.draw(screen)
        car.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

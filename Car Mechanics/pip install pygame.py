import pygame
import sys
import math  # Import the math module

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CAR_WIDTH, CAR_HEIGHT = 30, 50

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Car class
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.acceleration = 0.2
        self.maxSpeed = 3
        self.friction = 0.05
        self.angle = 0

    def move(self, controls):
        if controls['forward']:
            self.speed += self.acceleration
        if controls['reverse']:
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
            if controls['left']:
                self.angle += 0.03 * flip
            if controls['right']:
                self.angle -= 0.03 * flip

        self.x -= math.sin(self.angle) * self.speed  # Use math.sin
        self.y -= math.cos(self.angle) * self.speed  # Use math.cos

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, CAR_WIDTH, CAR_HEIGHT))

# Main loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Self-driving car - Python")
    clock = pygame.time.Clock()

    car = Car(WIDTH // 2, HEIGHT // 2)
    controls = {'forward': False, 'reverse': False, 'left': False, 'right': False}

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    controls['forward'] = True
                if event.key == pygame.K_DOWN:
                    controls['reverse'] = True
                if event.key == pygame.K_LEFT:
                    controls['left'] = True
                if event.key == pygame.K_RIGHT:
                    controls['right'] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    controls['forward'] = False
                if event.key == pygame.K_DOWN:
                    controls['reverse'] = False
                if event.key == pygame.K_LEFT:
                    controls['left'] = False
                if event.key == pygame.K_RIGHT:
                    controls['right'] = False

        screen.fill(WHITE)
        car.move(controls)
        car.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()


import pygame
import sys

SCALE = 5

SCREEN_WIDTH = 84 * SCALE
SCREEN_HEIGHT= 48 * SCALE

INITIAL_SNAKE_LENGTH = 3 * SCALE

LIGHT = "#c7f0d8"
DARK = "#43523d"
RED = '#ff0000'

LEFT = "🠔"
RIGHT = "🠖"
UP = "🠕"
DOWN = "🠗"

FPS = 60

class SnakeBodyPixel:
    def __init__(self, x, y, direction):
        self.image = pygame.Surface((1*SCALE, 1*SCALE))
        self.x = x
        self.y = y
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



    def update(self, direction, speed):
        if direction == LEFT:
            self.rect.x -= speed
        elif direction == RIGHT:
            self.rect.x += speed
        elif direction == UP:
            self.rect.y -= speed
        elif direction == DOWN:
            self.rect.y += speed
    
    def draw(self, target_surface):
        self.image.fill(DARK)
        target_surface.blit(self.image, (self.rect.x, self.rect.y))

class SnakeHeadPixel:
    def __init__(self, x, y, direction):
        self.image = pygame.Surface((1*SCALE, 1*SCALE))
        self.x = x
        self.y = y
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        
    def update(self, direction, speed):
        if direction == LEFT:
            self.rect.x -= speed
        elif direction == RIGHT:
            self.rect.x += speed
        elif direction == UP:
            self.rect.y -= speed
        elif direction == DOWN:
            self.rect.y += speed

    
    
    def draw(self, target_surface):
        self.image.fill(RED)
        target_surface.blit(self.image, (self.rect.x, self.rect.y))

class Snake:
    def __init__(self, length, target_surface) -> None:
        self.length = length
        self.target_surface = target_surface
        
        self.direction = LEFT
        self.head = SnakeHeadPixel(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.direction)
        self.speed = 1
        
        self.body_sprites = []
        for i in range(self.length -1):
            self.body_sprites.append(SnakeBodyPixel(self.head.x + 1 + i, self.head.y, self.direction))
        
    def draw(self):
        self.head.draw(self.target_surface)
        for body in self.body_sprites:
            body.draw(self.target_surface)
        

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            if self.direction in [LEFT, RIGHT]:
                self.direction = UP
                
        elif keys[pygame.K_DOWN]:
            if self.direction in [LEFT, RIGHT]:
                self.direction = DOWN
        elif keys[pygame.K_LEFT]:
            if self.direction in [UP, DOWN]:
                self.direction = LEFT
        elif keys[pygame.K_UP]:
            if self.direction in [UP, DOWN]:
                self.direction = RIGHT

    
    def update(self):
        
        self.head.update(self.direction, self.speed)
        for pos in self.body_sprites:
            pos.update(self.direction, self.speed)

    def draw(self):
        self.head.draw(self.target_surface)
        for body in self.body_sprites:
            body.draw(self.target_surface)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)
        self.clock = pygame.time.Clock()
        

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        self.snake.handle_input()


    def update(self):
        self.snake.update()

    def draw(self):
        self.screen.fill(LIGHT)
        self.snake.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
import pygame
import random
import sys

SCALE = 10

ORIGINAL_SCREEN_WIDTH = 84
ORIGINAL_SCREEN_HEIGHT = 48

SCREEN_WIDTH = ORIGINAL_SCREEN_WIDTH * SCALE
SCREEN_HEIGHT= ORIGINAL_SCREEN_HEIGHT * SCALE

INITIAL_SNAKE_LENGTH = 3
WALL_WIDTH = 2
BLOCK_SIZE = 4
# APPLE_SIZE = 3



LIGHT = "#c7f0d8"
DARK = "#43523d"
RED = '#ff0000'
BLACK = "#000000"

GAME_OVER_IMAGE = "gameover.png"
APPLE_IMAGE = "apple.png"

LEFT = "🠔"
RIGHT = "🠖"
UP = "🠕"
DOWN = "🠗"

FOUR_BUTTON_MODE = False

FPS = 12



class SnakeBodyPixel:
    def __init__(self, x, y, direction, size, color=DARK):
        self.color = color
        self.size = size
        self.image = pygame.Surface((self.size*SCALE, self.size*SCALE))
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, direction, speed):
        if direction == LEFT:
            self.rect.x -= speed * SCALE
        elif direction == RIGHT:
            self.rect.x += speed * SCALE
        elif direction == UP:
            self.rect.y -= speed * SCALE
        elif direction == DOWN:
            self.rect.y += speed * SCALE
    
    def draw(self, target_surface):
        self.image.fill(self.color)
        target_surface.blit(self.image, (self.rect.x, self.rect.y))


class Apple (pygame.sprite.Sprite):
    def __init__(self, x, y, image, groups, color=DARK) -> None:
        super().__init__(groups)
        # self.image_segments = []
        # for y, row in enumerate(apple_map):
        #     for x, cell in enumerate(row):
        #         self.image_segments.append((x*SCALE, y*SCALE, cell, pygame.Surface((1*SCALE, 1*SCALE))))
        # print(f"{[(r[0], r[1], r[2]) for r in self.image_segments]=}")
        self.image = image
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # print(f"{self.rect.topleft=}")

    def draw(self, target_surface):
        self.image.fill(self.color)
        target_surface.blit(self.image, (self.rect.x, self.rect.y))
        # for segment in self.image_segments:
        #     print(f"{segment=}")
        #     x, y, c, image = segment
        #     if c == 'X': 
        #         target_surface.blit(image, (self.rect.x + x, self.rect.y +y))

    


class Snake:
    def __init__(self, length, target_surface) -> None:
        self.length = length
        self.target_surface = target_surface
        self.size = BLOCK_SIZE
        
        self.direction = LEFT
        self.speed = 1
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2

        self.body_sprites = []
        for i in range(self.length):
            color=DARK
            # Change color for debuging
            # if i == 0:
            #     color = BLACK
            # elif i %2 == 0:
            #     color = RED
            # else:
            #     color = DARK
            body_part = SnakeBodyPixel(start_x + i * self.size * SCALE, start_y, self.direction, self.size, color)
            self.body_sprites.append(body_part)
        
    def draw(self):
        for body in self.body_sprites:
            body.draw(self.target_surface)
            

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Four button controls, direction only changes if selection is possible
        if FOUR_BUTTON_MODE:
            if self.direction in [LEFT, RIGHT]:
                if keys[pygame.K_UP]:
                    self.direction = UP
                elif keys[pygame.K_DOWN]:
                    self.direction = DOWN
            elif self.direction in [UP, DOWN]:
                if keys[pygame.K_LEFT]:
                    self.direction = LEFT    
                elif keys[pygame.K_RIGHT]:
                    self.direction = RIGHT
        
        # Two button controls, left rotates counter clockwise, right clockwise
    def handle_event(self, event):
        if event and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if self.direction == UP:
                    self.direction = LEFT
                elif self.direction == LEFT:
                    self.direction = DOWN
                elif self.direction == DOWN:
                    self.direction = RIGHT
                else:
                    self.direction = UP
            elif event.key == pygame.K_RIGHT:
                if self.direction == UP:
                    self.direction = RIGHT
                elif self.direction == LEFT:
                    self.direction = UP
                elif self.direction == DOWN:
                    self.direction = LEFT
                else:
                    self.direction = DOWN
            elif event.key == pygame.K_g:
                self.grow()

    def grow(self):
        tail = self.body_sprites[-1]
        x = tail.rect.x
        y = tail.rect.y
        
        if tail.direction == LEFT:
            x += SCALE
        elif tail.direction == RIGHT:
            x -= SCALE
        elif tail.direction == UP:
            y += SCALE
        else:  # tail.direction == DOWN
            y -= SCALE
        self.body_sprites.append(SnakeBodyPixel(x, y, self.direction, self.size, color=DARK))
    
    def update(self):
        head = self.body_sprites[0]
        # store our current position in the variable to be used by the next sprite
        self.current_x, self.current_y = head.rect.x, head.rect.y

        # calculate and set our next position
        head.rect.x, head.rect.y = get_next_pos(head, self.speed * self.size, self.direction)

        self.current_sprite_direction = self.direction
        
        
        for body in self.body_sprites[1:]:
            # store own current position in temp variables
            temp_own_current_x = body.rect.x
            temp_own_current_y = body.rect.y

            temp_own_direction = body.direction
            
            # set our own (next) position to that of the previous sprite
            body.rect.x = self.current_x # set by previous iteration
            body.rect.y = self.current_y
            body.direction = self.current_sprite_direction

            # Set the variable to be used by the next sprite to our (original) current position
            self.current_x = temp_own_current_x
            self.current_y = temp_own_current_y
            self.current_sprite_direction = temp_own_direction
            

    def draw(self):
        for body in self.body_sprites:
            body.draw(self.target_surface)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, groups, size=1, color=DARK) -> None:
        super().__init__(groups)
        self.image = pygame.Surface((width*SCALE*size, height*SCALE*size))
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, target_surface):
        self.image.fill(self.color)
        target_surface.blit(self.image, (self.rect.x, self.rect.y))

class Level:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        interstitial_game_over_image = pygame.image.load(GAME_OVER_IMAGE).convert_alpha()
        self.game_over_image = pygame.transform.scale(interstitial_game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.collision_sprites = pygame.sprite.Group()
        interstitial_apple_image = pygame.image.load(APPLE_IMAGE).convert_alpha()
        apple_width = interstitial_apple_image.get_width() * SCALE
        apple_height = interstitial_apple_image.get_height() * SCALE
        self.apple_image = pygame.transform.scale(interstitial_apple_image, (apple_width, apple_height))
        
        self.create_apple(self.apple_image)
        
        self.create_snake()        
        self.create_map()

        self.running = True


    def create_apple(self, image):
        self.apple = pygame.sprite.GroupSingle()
        x = random.randint(1, ORIGINAL_SCREEN_WIDTH-1) * SCALE
        y = random.randint(1, ORIGINAL_SCREEN_HEIGHT-1) * SCALE
        Apple(x, y, image, [self.apple])

    def create_snake(self):
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)


    def create_map(self):
        groups = [self.collision_sprites]

        top=Wall(x=0, y=0, width=ORIGINAL_SCREEN_WIDTH, height=WALL_WIDTH, groups=groups)
        bottom=Wall(x=0, y=SCREEN_HEIGHT-SCALE*WALL_WIDTH, width=ORIGINAL_SCREEN_WIDTH, height=WALL_WIDTH, groups=groups)
        left=Wall(x=0, y=0, width=WALL_WIDTH, height=ORIGINAL_SCREEN_HEIGHT, groups=groups)
        right=Wall(x=SCREEN_WIDTH-SCALE*WALL_WIDTH, y=0, width=WALL_WIDTH, height=ORIGINAL_SCREEN_HEIGHT, groups=groups)
        


    def run(self):
        while True:
            if self.running:
                self.handle_input()
                self.update()
                self.draw()
            else:
                self.screen.blit(self.game_over_image, (0,0))
                # print_text(self.screen, "Game Over")
                self.handle_input()
            
            pygame.display.update()
            self.clock.tick(FPS)

    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not self.running:
                self.restart()
            elif event.type == pygame.KEYDOWN and not FOUR_BUTTON_MODE:
                self.snake.handle_event(event)
        self.snake.handle_input()


    def update(self):
        # spawn_apple
        self.snake.update()
        self.handle_collections()
        self.handle_collisions()

    def draw(self):
        self.screen.fill(LIGHT)
        if self.running:
            self.snake.draw()
            # if apple, draw apple
            self.apple.draw(self.screen)
        for sprite in self.collision_sprites:
            sprite.draw(self.screen)

    def restart(self):
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)
        self.running = True

    def handle_collections(self):
        head = self.snake.body_sprites[0]
        apple = self.apple.sprite
        if apple.rect.colliderect(head.rect):
            self.snake.grow()
            self.create_apple(self.apple_image)

    def handle_collisions(self):
        head = self.snake.body_sprites[0]
        body_sprites = self.snake.body_sprites[1:]
        
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(head.rect):
                self.running = False

        for i, sprite in enumerate(body_sprites):
            if sprite.rect.colliderect(head.rect):
                print(f"{i=} {head.rect.topleft=} {head.rect.bottomright=} {sprite.rect.topleft=} {sprite.rect.bottomright=}")
                self.running = False


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        self.level = Level()

    def run(self):
        self.level.run()
        



def get_next_pos(sprite, speed, direction):
    if direction == LEFT:
        next_x = sprite.rect.x - speed * SCALE
        next_y = sprite.rect.y
    elif direction == RIGHT:
        next_x = sprite.rect.x + speed * SCALE
        next_y = sprite.rect.y
    elif direction == UP:
        next_x = sprite.rect.x
        next_y = sprite.rect.y - speed * SCALE
    else: #  elif self.direction == DOWN:
        next_x = sprite.rect.x
        next_y = sprite.rect.y + speed * SCALE

    return next_x, next_y


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
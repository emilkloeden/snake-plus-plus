from turtle import right
import pygame
import random
import sys
import os

SCALE = 1

try:
    with open(os.path.join("assets", "scale.txt"), "r") as f:
        SCALE = int(f.readline().strip())
        if SCALE > 10:
            SCALE = 10
        elif SCALE < 1:
            SCALE = 1
except Exception:
    SCALE = 1

SCORE_SCALE = 4
STARTING_SCORE = 0

ORIGINAL_SCREEN_WIDTH = 84
ORIGINAL_SCREEN_HEIGHT = 48

SCREEN_WIDTH = ORIGINAL_SCREEN_WIDTH * SCALE
SCREEN_HEIGHT= ORIGINAL_SCREEN_HEIGHT * SCALE

INITIAL_SNAKE_LENGTH = 3
WALL_WIDTH = 4
BLOCK_SIZE = 4

SPAWN_RATE = 5
INCREMENT_BONUS = 3


LIGHT = "#c7f0d8"
DARK = "#43523d"
RED = '#ff0000'
BLACK = "#000000"

GAME_OVER_IMAGE = "gameover.png"
APPLE_IMAGE = "apple.png"
RESIZER_IMAGE = "resizer.png"
PLUS_IMAGE = "plus.png"
SMILEY_IMAGE = "smiley.png"

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



class Interactable(pygame.sprite.Sprite):
    def __init__(self, x, y, image, groups, color=DARK):
        super().__init__(groups)
        self.image = image
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, target_surface):
        target_surface.blit(self.image, (self.rect.x, self.rect.y))

class Apple(Interactable):
    def __init__(self, x, y, image, groups, color=DARK):
        super().__init__(x, y, image, groups, color)
        
class Resizer(Interactable):
    def __init__(self, x, y, image, groups, color=DARK):
        super().__init__(x, y, image, groups, color)
        
class Incrementor(Interactable):
    def __init__(self, x, y, image, groups, color=DARK):
        super().__init__(x, y, image, groups, color)
    

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
    
    def shrink(self):
        current_num_body_parts = len(self.body_sprites) 
        # print(f"Before shrink: {current_num_body_parts=}")
        next_num_body_parts = self.length if current_num_body_parts // 2 < self.length else current_num_body_parts // 2
        self.body_sprites = self.body_sprites[:next_num_body_parts]
        # print(f"After shrink: {len(self.body_sprites)}")
    
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
        interstitial_game_over_image = pygame.image.load(os.path.join("assets", GAME_OVER_IMAGE)).convert_alpha()
        self.game_over_image = pygame.transform.scale(interstitial_game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.collision_sprites = pygame.sprite.Group()
        self.interactable_sprites = pygame.sprite.Group()

        interstitial_apple_image = pygame.image.load(os.path.join("assets", APPLE_IMAGE)).convert_alpha()
        self.interactable_width = interstitial_apple_image.get_width() * SCALE
        self.interactable_height = interstitial_apple_image.get_height() * SCALE
        self.apple_image = pygame.transform.scale(interstitial_apple_image, (self.interactable_width, self.interactable_height))
        
        interstitial_resizer_image = pygame.image.load(os.path.join("assets", RESIZER_IMAGE)).convert_alpha()
        self.rezizer_image = pygame.transform.scale(interstitial_resizer_image, (self.interactable_width, self.interactable_height))
        
        interstitial_incrementor_image = pygame.image.load(os.path.join("assets", PLUS_IMAGE)).convert_alpha()
        self.incrementor_image = pygame.transform.scale(interstitial_incrementor_image, (self.interactable_width, self.interactable_height))
        
        self.smiley_image = pygame.image.load(os.path.join("assets", SMILEY_IMAGE)).convert_alpha()
        self.score_images = load_score_images()


        self.score = STARTING_SCORE
        self.can_collect_bonus = False

        self.create_snake()        
        self.create_apple(self.apple_image)
        
        self.create_map()

        self.running = True


    def create_apple(self, image):
        self.apple = pygame.sprite.GroupSingle()
        x, y = self.choose_spot() 
        Apple(x, y, image, [self.apple])

    def choose_spot(self):
        "This attempts to ensure apples won't spawn under the snake"
        x = random.randint(WALL_WIDTH*SCALE, ((ORIGINAL_SCREEN_WIDTH-WALL_WIDTH) * SCALE) -self.interactable_width)
        y = random.randint(WALL_WIDTH*SCALE, ((ORIGINAL_SCREEN_HEIGHT-WALL_WIDTH) * SCALE) - self.interactable_height)
        temp_rect = pygame.Rect(x, y, self.interactable_width, self.interactable_height)
        for sprite in self.snake.body_sprites:
            if sprite.rect.colliderect(temp_rect):
                return self.choose_spot()
        return x,y

    def create_snake(self):
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)


    def create_map(self):
        groups = [self.collision_sprites]

        top=Wall(x=0, y=0, width=ORIGINAL_SCREEN_WIDTH, height=WALL_WIDTH, groups=groups)
        bottom=Wall(x=0, y=SCREEN_HEIGHT-SCALE*WALL_WIDTH, width=ORIGINAL_SCREEN_WIDTH, height=WALL_WIDTH, groups=groups)
        left=Wall(x=0, y=0, width=WALL_WIDTH*0.5, height=ORIGINAL_SCREEN_HEIGHT, groups=groups)
        right=Wall(x=SCREEN_WIDTH-SCALE*WALL_WIDTH*0.5, y=0, width=WALL_WIDTH*0.5, height=ORIGINAL_SCREEN_HEIGHT, groups=groups)
        
    def spawn_bonus(self):
        self.can_collect_bonus = False
        x, y = self.choose_spot() 
        if random.random() > 0.5:
            Resizer(x, y, self.rezizer_image, [self.interactable_sprites])
        else:
            Incrementor(x, y, self.incrementor_image, [self.interactable_sprites])

    def run(self):
        while True:
            if self.running:
                self.handle_input()
                self.update()
                self.draw()
                
                if self.score > 0 and self.score % SPAWN_RATE == 0 and self.can_collect_bonus:
                    self.spawn_bonus()
            else:
                self.screen.blit(self.game_over_image, (0,0))
                self.draw_score()
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


    def draw_score(self):
        score_str = str(self.score)
        y = (WALL_WIDTH + SCORE_SCALE) * SCALE
        x = (ORIGINAL_SCREEN_WIDTH - WALL_WIDTH -SCORE_SCALE) * SCALE
        
        if len(score_str) == 1:
            image = self.score_images[score_str]
            self.screen.blit(image, (x, y))
        elif len(score_str) == 2:
            left_score_str = score_str[0]
            right_score_str = score_str[-1]
            right_image = self.score_images[right_score_str]
            self.screen.blit(right_image, (x, y))
            
            left_image = self.score_images[left_score_str]
            x -= right_image.get_width()
            self.screen.blit(left_image, (x, y))
        else:
            self.screen.blit(self.smiley_image, (x, y))

    def draw(self):
        self.screen.fill(LIGHT)
        if self.running:
            self.draw_score()
            self.snake.draw()
            # if apple, draw apple
            self.apple.draw(self.screen)
            for sprite in self.interactable_sprites:
                sprite.draw(self.screen)
        for sprite in self.collision_sprites:
            sprite.draw(self.screen)

    def restart(self):
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)
        self.score = STARTING_SCORE
        self.running = True

    def handle_collections(self):
        head = self.snake.body_sprites[0]
        apple = self.apple.sprite
        if apple.rect.colliderect(head.rect):
            self.score += 1
            if self.score % SPAWN_RATE != 0 and self.interactable_sprites:
                for interactable in self.interactable_sprites:
                    interactable.kill()
            if self.score % SPAWN_RATE == 0 and not self.interactable_sprites:
                self.can_collect_bonus = True
            self.snake.grow()
            self.create_apple(self.apple_image)

        for interactable in self.interactable_sprites:
            if interactable.rect.colliderect(head.rect):
                interactable.kill()
                if isinstance(interactable, Resizer):
                    self.snake.shrink()
                elif isinstance(interactable, Incrementor):
                    self.score += INCREMENT_BONUS

    def handle_collisions(self):
        head = self.snake.body_sprites[0]
        body_sprites = self.snake.body_sprites[1:]
        
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(head.rect):
                self.running = False

        for i, sprite in enumerate(body_sprites):
            if sprite.rect.colliderect(head.rect):
                # print(f"{i=} {head.rect.topleft=} {head.rect.bottomright=} {sprite.rect.topleft=} {sprite.rect.bottomright=}")
                self.running = False


class IntroScreen():
    def __init__(self):
        self.screen = pygame.display.get_surface()
        interstitial_image = pygame.image.load(os.path.join("assets", "title.png"))
        self.image = pygame.transform.scale(interstitial_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            pygame.display.update()
            self.clock.tick()

    def draw(self):
        self.screen.fill(LIGHT)
        self.screen.blit(self.image, (0,0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.running = False


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        self.level = Level()
        self.intro_screen = IntroScreen()

    def run(self):
        self.intro_screen.run()
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


def load_score_images():
    scaled_images = {}
    for i in range(10):
        interstitial_image = pygame.image.load(os.path.join("assets", f"{i}.png")).convert_alpha()
        image = pygame.transform.scale(interstitial_image, (SCORE_SCALE*SCALE, SCORE_SCALE*SCALE))
        scaled_images[str(i)] = image

    return scaled_images

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
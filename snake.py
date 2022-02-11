import string
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

WALL_SCORE_PADDING = 4
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

APPLE_IMAGE = "apple"
RESIZER_IMAGE = "resizer"
PLUS_IMAGE = "plus"
SCORE_KEEPER_IMAGE = "square"

LEFT = "🠔"
RIGHT = "🠖"
UP = "🠕"
DOWN = "🠗"

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
    


class ScoreKeeper(Interactable):
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
            body_part = SnakeBodyPixel(start_x + i * self.size * SCALE, start_y, self.direction, self.size, DARK)
            self.body_sprites.append(body_part)
        
    def draw(self):
        for body in self.body_sprites:
            body.draw(self.target_surface)
            


        
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
        next_num_body_parts = self.length if current_num_body_parts // 2 < self.length else current_num_body_parts // 2
        self.body_sprites = self.body_sprites[:next_num_body_parts]
    
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
    def __init__(self, alphabet, big_alphabet):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.collision_sprites = pygame.sprite.Group()
        self.interactable_sprites = pygame.sprite.Group()

        self.alphabet = alphabet
        self.big_alphabet = big_alphabet

        self.apple_image = load_scaled_image("apple")
        self.rezizer_image = load_scaled_image("resizer")
        self.incrementor_image = load_scaled_image("plus")
        self.score_keeper_image = load_scaled_image("square")
        
        self.score = STARTING_SCORE
        self.can_collect_bonus = False
        self.keep_score = False

        self.create_snake()        
        self.create_apple()
        self.create_map()

        self.running = True


    def create_apple(self):
        # This is created here as a hack to respawn it after collection
        # by calling this method directly
        self.apple = pygame.sprite.GroupSingle()
        x, y = self.choose_spot() 
        Apple(x, y, self.apple_image, [self.apple])


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
        # This is created here as a hack to respawn it on restart
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)


    def create_map(self):
        groups = [self.collision_sprites]

        # Top
        Wall(x=0, y=0, width=ORIGINAL_SCREEN_WIDTH, height=WALL_WIDTH, groups=groups)
        
        # Bottom
        Wall(x=0, y=SCREEN_HEIGHT-SCALE*WALL_WIDTH, width=ORIGINAL_SCREEN_WIDTH, height=WALL_WIDTH, groups=groups)
        
        # Left
        Wall(x=0, y=0, width=WALL_WIDTH*0.5, height=ORIGINAL_SCREEN_HEIGHT, groups=groups)
        
        # Right
        Wall(x=SCREEN_WIDTH-SCALE*WALL_WIDTH*0.5, y=0, width=WALL_WIDTH*0.5, height=ORIGINAL_SCREEN_HEIGHT, groups=groups)
        
    def spawn_bonus(self):
        self.can_collect_bonus = False
        x, y = self.choose_spot() 
         
        random_val = random.random()
        if random_val < 0.45:
            Resizer(x, y, self.rezizer_image, [self.interactable_sprites])
        elif random_val < 0.9 :
            Incrementor(x, y, self.incrementor_image, [self.interactable_sprites])
        else: # > 0.9 (or ~10% probability of an extra life)
            ScoreKeeper(x, y, self.score_keeper_image, [self.interactable_sprites])

    def run(self):
        while True:
            if self.running:
                self.handle_input()
                self.update()
                self.draw()
                
                if self.score > 0 and self.score % SPAWN_RATE == 0 and self.can_collect_bonus:
                    self.spawn_bonus()
            else:
                if self.keep_score:
                    print_text(self.screen, self.big_alphabet, "EXTRA", 0, 10*SCALE, center_x=True)
                    print_text(self.screen, self.big_alphabet, "LIFE", 0, 26*SCALE, center_x=True)
                else:
                    print_text(self.screen, self.big_alphabet, "GAME", 0, 10*SCALE, center_x=True)
                    print_text(self.screen, self.big_alphabet, "OVER", 0, 26*SCALE, center_x=True)
                self.draw_score()
                self.handle_input()
            
            pygame.display.update()
            self.clock.tick(FPS)

    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not self.running:
                self.restart(self.keep_score)
            elif event.type == pygame.KEYDOWN:
                self.snake.handle_event(event)
        

    def update(self):
        self.snake.update()
        self.handle_collections()
        self.handle_collisions()


    def draw_score(self):
        score_str = str(self.score)
        y = (WALL_WIDTH + WALL_SCORE_PADDING) * SCALE
        x = (ORIGINAL_SCREEN_WIDTH - WALL_WIDTH -WALL_SCORE_PADDING) * SCALE

        # This funky math just ensures right-aligning text works
        x -= (len(score_str)-1) * self.alphabet["A"].get_width()
        print_text(self.screen, self.alphabet, score_str, x, y)

    def draw(self):
        self.screen.fill(LIGHT)
        if self.running:
            self.draw_score()
            self.snake.draw()
            self.apple.draw(self.screen)
            for sprite in self.interactable_sprites:
                sprite.draw(self.screen)

        # Always draw the walls, it looks prettier this way
        for sprite in self.collision_sprites:
            sprite.draw(self.screen)

    def restart(self, keep_score=False):
        self.snake = Snake(INITIAL_SNAKE_LENGTH, self.screen)
        if not keep_score:
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
            self.create_apple()

        for interactable in self.interactable_sprites:
            if interactable.rect.colliderect(head.rect):
                interactable.kill()
                if isinstance(interactable, Resizer):
                    self.snake.shrink()
                elif isinstance(interactable, Incrementor):
                    self.score += INCREMENT_BONUS
                elif isinstance(interactable, ScoreKeeper):
                    self.keep_score = True

    def handle_collisions(self):
        head = self.snake.body_sprites[0]
        body_sprites = self.snake.body_sprites[1:]
        
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(head.rect):
                self.running = False

        for sprite in body_sprites:
            if sprite.rect.colliderect(head.rect):
                self.running = False


class IntroScreen():
    def __init__(self, alphabet, big_alphabet):
        self.screen = pygame.display.get_surface()
        interstitial_image = pygame.image.load(os.path.join("assets", "title.png"))
        self.image = pygame.transform.scale(interstitial_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.alphabet = alphabet
        self.big_alphabet = big_alphabet


    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            pygame.display.update()
            self.clock.tick()

    def draw(self):
        self.screen.fill(LIGHT)
        print_text(self.screen, self.big_alphabet, "snake++", 10*SCALE, 10*SCALE, center_x=True)
        print_text(self.screen, self.alphabet, "Press any key...", 10*SCALE, 36*SCALE, center_x=True)
    
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
        self.alphabet = load_alphabet()
        self.big_alphabet = load_alphabet(scale=SCALE*2)
        self.intro_screen = IntroScreen(self.alphabet, self.big_alphabet)
        self.level = Level(self.alphabet, self.big_alphabet)
        
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


def print_text(surface, alphabet, text, x, y, center_x=False):
    """Blits a line of text in our pixel font to the surface
    
    Can't handle multiple lines of text ;)"""
    uppercase = text.upper()
    character_width = alphabet["A"].get_width()
    total_text_width = len(uppercase) * (character_width + SCALE) - SCALE

    # If center, ignore x
    if center_x:
        x = (SCREEN_WIDTH - total_text_width) // 2
    for i, c in enumerate(uppercase):
        if c in alphabet:
            surface.blit(alphabet[c], (x + i * (character_width + SCALE), y))



def load_sized_image(image_filename, output_size=(SCREEN_WIDTH, SCREEN_HEIGHT)):
    interstitial_image = pygame.image.load(os.path.join("assets", f"{image_filename}.png")).convert_alpha()
    return pygame.transform.scale(interstitial_image, output_size)
        
def load_scaled_image(image_filename, scale=SCALE):
    interstitial_image = pygame.image.load(os.path.join("assets", f"{image_filename}.png")).convert_alpha()
    w, h = interstitial_image.get_size()
    return pygame.transform.scale(interstitial_image, (w*scale, h*scale))

def load_alphabet(scale=SCALE):
    character_set = string.ascii_uppercase + string.digits + "+-."
    alphabet = {}
    for i, c in enumerate(character_set):
        alphabet[c] = load_scaled_image(f"sprite_{i:02d}", scale=scale)
    return alphabet


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
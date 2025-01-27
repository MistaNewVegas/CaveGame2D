import pygame
import random

# Constants
SCREEN_WIDTH = 620
SCREEN_HEIGHT = 480

NUM_PLATFORMS = 2
PLATFORM_COORDS = [
                   (SCREEN_WIDTH/4, SCREEN_HEIGHT/2), 
                   (SCREEN_WIDTH - SCREEN_WIDTH/4, SCREEN_HEIGHT/2 - SCREEN_HEIGHT/4),

                   ]

PLAYER_SPRITES = {"static": "assets/character/red.png", "left": "assets/character/left.png", "right": "assets/character/right.png", "fall": "assets/character/fall.png"}

NUMBER_ENEMIES = 1

def distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """ Calc squared distance between two points """
    try: return (x2 - x1) ** 2 + (y2 - y1) ** 2
    except: pass 


class Player(pygame.sprite.Sprite):

    def __init__(self) -> None:
        super().__init__()

        self.sprites = {
            "static": pygame.transform.scale(pygame.image.load(PLAYER_SPRITES.get("static")), (25, 30)),
            "left": pygame.transform.scale(pygame.image.load(PLAYER_SPRITES.get("left")), (25, 30)),
            "right": pygame.transform.scale(pygame.image.load(PLAYER_SPRITES.get("right")), (25, 30)),
            "fall": pygame.transform.scale(pygame.image.load(PLAYER_SPRITES.get("fall")), (25, 30))
        }



        self.image = self.sprites["static"]

        self.rect = self.image.get_rect()

        self.rect.x = SCREEN_WIDTH/2
        self.rect.y = SCREEN_HEIGHT/2

        self.speed = 5
        self.jumpheight = -15
        self.gravity = 0.5
        self.velocity_y = 1
        self.velocity_x = 0

        self.onground = False
        self.jumping = False

    def update(self, floor, platforms):
        key = pygame.key.get_pressed()

        if key[pygame.K_a]:
            self.velocity_x = -self.speed
            self.image = self.sprites["left"]
        elif key[pygame.K_d]:
            self.velocity_x = self.speed
            self.image = self.sprites["right"]
        else:
            self.velocity_x = 0

        # wall borders
        if self.rect.x < 0:
            self.rect.x += 5
        if self.rect.x > SCREEN_WIDTH-30:
            self.rect.x -= 5

        # Move horizontally based on velocity_x
        self.rect.x += self.velocity_x

        # Initiate Jump
        if not self.jumping and self.onground and key[pygame.K_SPACE]:
            self.jumping = True
            self.onground = False
            self.velocity_y = self.jumpheight

        # Reset onground status before applying gravity and checking collisions
        self.onground = False

        # Apply Gravity
        if not self.onground:
            self.rect.y += self.velocity_y
            self.velocity_y += self.gravity

        # Check for collisions with floor and platforms
        self.check_collision(floor)

        for platform in platforms:
            self.check_collision(platform)

        # Separate logic for sprite update based on the final state
        if self.onground and self.velocity_x == 0:
            self.image = self.sprites["static"]
        elif self.velocity_x > 0:
            self.image = self.sprites["right"]
        elif self.velocity_x < 0:
            self.image = self.sprites["left"]

        elif not self.onground and self.velocity_y > 0.5:
            self.image = self.sprites["fall"]


    def check_collision(self, sprite):
        # Vertical collision check
        if self.rect.colliderect(sprite.rect):
            if self.velocity_y > 0 and self.rect.bottom <= sprite.rect.top + self.velocity_y:
                # Landing on top of the sprite
                self.rect.bottom = sprite.rect.top
                self.jumping = False
                self.onground = True
                self.velocity_y = 0
            elif self.velocity_y < 0 and self.rect.top >= sprite.rect.bottom + self.velocity_y:
                # Hitting the bottom of the sprite
                self.rect.top = sprite.rect.bottom
                self.velocity_y = 0

        if self.rect.colliderect(sprite.rect):
            if self.rect.right >= sprite.rect.left and self.rect.left < sprite.rect.left:
                # Collision on the right
                self.rect.right = sprite.rect.left
            elif self.rect.left <= sprite.rect.right and self.rect.right > sprite.rect.right:
                # Collision on the left
                self.rect.left = sprite.rect.right


class Floor(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/floor.png")
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, 60))

        self.rect = self.image.get_rect()

        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - 60

class Platform(pygame.sprite.Sprite):
    
    def __init__(self, coords):
        super().__init__()

        self.image = pygame.image.load("assets/amogmoon.png")
        self.image = pygame.transform.scale(self.image, (60, 60))

        self.rect = self.image.get_rect()

        x,y = coords
        self.rect.x = x
        self.rect.y = y

        self.direction_x = random.randint(-3,3)

    def update(self):

        self.rect.x += self.direction_x

        if self.rect.x > SCREEN_WIDTH:
            self.rect.x -= SCREEN_WIDTH + 60
        
        if self.rect.x < -60:
            self.rect.x += SCREEN_WIDTH + 60

class Blaster(pygame.sprite.Sprite):

    def __init__(self, direction):
        super().__init__()

        self.image = pygame.image.load("assets/bullet.png")
        self.image = pygame.transform.scale(self.image, (10,10))

        self.rect = self.image.get_rect()

        self.direction = direction # (0,0) (pos/neg, pos/neg) (x/y)

        self.speed = 10

    def update(self):
        self.rect.x += self.speed*self.direction[0]
        self.rect.y += self.speed*self.direction[1]

class Entity(pygame.sprite.Sprite):
    """ Anything that has gravity and collisions, Pretty much """
    def __init__(self):
        super().__init__()
        self.gravity = 1
        self.velocity_y = 1
        # self.max_vy
        self.velocity_x = 0

        # flags
        self.onground = False
        self.jumping = False
        self.frozen = False
        self.reflectx = False

        self.MAX_FALL_SPEED = 20

    def update(self, floor):
        """ Apply gravity, check collisions """
        # Apply gravity if not on ground
        if not self.onground:
            self.rect.y += self.velocity_y
            self.velocity_y += self.gravity

        # Simple collision flags (or)
        self.vertcol = False
        self.horcol = False
        self.collision_detected = self.vertcol or self.horcol

        self.check_collision_vert(floor)

    def check_collision_vert(self, sprite):
        """ Vertical Collisions """
        if self.rect.colliderect(sprite.rect): # not sure how heavy this function is
            # Landing on top of a chunk
            if self.velocity_y > 0 and self.rect.bottom > sprite.rect.top:
                projected_bottom = self.rect.bottom + self.velocity_y * 2.5 # still clipped thru when falling fast enough
                if projected_bottom >= sprite.rect.top and self.rect.top < sprite.rect.top:
                    self.rect.bottom = sprite.rect.top
                    self.velocity_y = 0
                    self.jumping = False
                    self.onground = True
                    self.vertcol = True
            # Hitting bottom of a chunk
            elif self.velocity_y < 0:
                projected_top = self.rect.top + self.velocity_y
                if projected_top <= sprite.rect.bottom and self.rect.bottom > sprite.rect.top:
                    self.rect.top = sprite.rect.bottom
                    self.velocity_y = 0
                    self.jumping = False
        else:
            self.onground = False

    def check_collision_hori(self, sprite):
        """ Horizontal Collisions """
        if self.rect.colliderect(sprite.rect):
            # <entity> --> [chunk]
            if self.rect.right > sprite.rect.left and self.rect.left < sprite.rect.left:
                overlap = self.rect.right - sprite.rect.left
                self.rect.x -= overlap
                self.reflectx = True
                self.horcol = True
            # [chunk] <-- <entity>
            if self.rect.left < sprite.rect.right and self.rect.right > sprite.rect.right:
                overlap = sprite.rect.right - self.rect.left
                self.rect.x += overlap
                self.horcol = True
                self.reflectx = True

class Enemy(Entity):

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.image.load("assets/character/red.png")
        self.image = pygame.transform.scale(self.image, (10, 10))

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.randomjump = None
        self.dojump = False
        self.speed = 1
        self.jumpheight = -10 # same as base player

        self.velocity_x = 1
        self.VX = 1

        self.health = 10
        self.worth = 200

        self.player_in_range = False
        self.iskill = False

    def update(self, floor, player):

        # gravity, check collisions return self.dojump if horizontal collision detected
        Entity.update(self, floor)

        if not 100 < self.rect.x < SCREEN_WIDTH - 100:
            self.velocity_x = -self.velocity_x

        self.seek(player)


        if self.dojump and not self.jumping and self.onground: # try to jump over obstacles
            self.velocity_y = self.jumpheight
            self.dojump = False

        if self.reflectx:
            self.velocity_x = -self.velocity_x

        self.rect.x += self.velocity_x # apply final calculations

        self.reflectx = False

    def seek(self, player):
        """ Logic for chasing player if in range """
        # self.velocity.x self.rect.x player.velocity.x player.rect.x
        if self.rect.x > player.rect.x:
            self.velocity_x = -self.VX
        else: self.velocity_x = self.VX



class Game:

    def __init__(self):

        pygame.init()

        # Screen set
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

        self.background = pygame.image.load('assets/background.png')
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption('Lab 4 // Asst 1 physics test ')

        self.all_sprites_list = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

        self.player = Player()
        self.all_sprites_list.add(self.player)

        self.floor = Floor()
        self.all_sprites_list.add(self.floor)

        self.bullet_list = pygame.sprite.Group()
        self.bullet_timer = 0
        self.bullet_span = 300 # ms

        """ Adding Enemies """
        self.enemies_list = pygame.sprite.Group()
        self.add_enemies()

        """ Adding Platforms """
        self.platforms = pygame.sprite.Group()
        for i in range(NUM_PLATFORMS):
            platform = Platform(PLATFORM_COORDS[i])
            self.all_sprites_list.add(platform)
            self.platforms.add(platform)

        pygame.font.init()
        self.font = pygame.font.SysFont('impact', 25)

    def add_enemies(self):
        for i in range(NUMBER_ENEMIES):
            x = random.randrange(20, SCREEN_WIDTH - 20)
            y = 90  # Set the y-coordinate as needed
            enemy = Enemy(x, y)
            self.enemies_list.add(enemy)
            self.all_sprites_list.add(enemy)

    def poll(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        key = pygame.key.get_pressed()
        direction = None

        if key[pygame.K_g]:
            self.add_enemies()

        if self.bullet_timer <= 0:
            if key[pygame.K_LEFT]:
                direction = (-1, 0)
            elif key[pygame.K_RIGHT]:
                direction = (1, 0)
            elif key[pygame.K_DOWN]:
                direction = (0, 1)
            elif key[pygame.K_UP]:

                direction = (0, -1)

            if direction:
                bullet = Blaster(direction)
                bullet.rect.x = self.player.rect.centerx
                bullet.rect.y = self.player.rect.centery
                self.all_sprites_list.add(bullet)
                self.bullet_list.add(bullet)
            
            self.bullet_timer = self.bullet_span

    def update(self):

        dt = self.clock.tick(60)  # Update the clock and get the time delta
        self.bullet_timer -= dt

        self.enemies_list.update(self.floor, self.player)
            

        self.player.update(self.floor, self.platforms)

        """ Bullet deletion logic """
        for bullet in self.bullet_list:
            if not (0 < bullet.rect.y < SCREEN_HEIGHT - 60):
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)
            if not (0 < bullet.rect.x < SCREEN_WIDTH):
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)

            amog_hit_list = pygame.sprite.spritecollide (bullet, self.enemies_list, True)

            for bullet in amog_hit_list:
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)


            for platform in self.platforms:
                if bullet.rect.colliderect(platform.rect):
                    # Collision detected, remove the bullet
                    self.bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                    break 

    
    def draw(self):
        # clear background
        self.screen.blit(self.background, (0,0))
        
        # draw sprites
        self.all_sprites_list.draw(self.screen)


        self.ecount = self.font.render('Entity Count: ' + str(len(self.enemies_list)+1), True, (0, 0, 0))
        self.screen.blit(self.ecount, [10, SCREEN_HEIGHT-30])

        self.fpsdis = self.font.render('FPS: ' + str(round(self.clock.get_fps())), True, (0, 0, 0))
        self.screen.blit(self.fpsdis, [SCREEN_WIDTH - 80, SCREEN_HEIGHT-30])

    def run(self):
        self.running = True

        clock = pygame.time.Clock()

        while self.running:
            # event processing
            self.poll()
            # logic
            self.update()
            # draw frame
            self.draw()
            # update screen
            pygame.display.flip()

            clock.tick(60)


if __name__ == '__main__':
    g = Game()
    print("starting...")
    g.run()
    print("shutting down...")
    pygame.quit()
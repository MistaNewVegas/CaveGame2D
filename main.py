
import pygame
import random
import terrain_data_generator

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MAX_FALL_SPEED = 20

"""------------------------------------------------ Supp Formulas ------------------------------------------------"""
def distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """ Calc squared distance between two points """
    try: return (x2 - x1) ** 2 + (y2 - y1) ** 2
    except: pass 
    
# rare 0div case in testing, dont care enough to see if possible in real thing

def roundeddiv(x: int, y: int) -> int:
    """ Return a rounded division between two int"""
    try: return round(x/y)
    except: pass

"""------------------------------------------------ Entities ------------------------------------------------"""

class Entity(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.gravity = 1
        self.velocity_y = 1
        # self.max_vy
        self.velocity_x = 0

        self.onground = False
        self.jumping = False
        self.frozen = False
        self.reflectx = False

    def update(self, chunks):
        """ Apply gravity, check collisions """
        # Apply gravity if not on ground
        if not self.onground:
            self.rect.y += self.velocity_y
            self.velocity_y += self.gravity

        # OR gate for simple/fast collision detection
        self.vertcol = False
        self.horcol = False
        self.collision_detected = self.vertcol or self.horcol

        # loop thru visible chunks, only check collision if chunk is within squared distance
        for chunk in chunks:
            if not self.collision_detected:
                if distance(self.rect.x, self.rect.y, chunk.rect.x, chunk.rect.y) < 2500:
                    self.check_collision_vert(chunk)
                    self.check_collision_hori(chunk)
            else:
                break

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
        else:
            self.onground = False


gridchunk = roundeddiv(SCREEN_WIDTH, 33)

class Player(Entity):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/entity/player.png")
        self.image = pygame.transform.scale(self.image, (gridchunk*0.4, gridchunk*0.5))

        self.rect = self.image.get_rect()


        self.speed = 4

        self.jumpheight = -10

        self.rect.x = SCREEN_WIDTH / 2
        self.rect.y = gridchunk * 10
        self.max_velocity_y = None

        self.health = 100
        self.score = 0
        self.level = 4

        print("Player Spawned")
        self.vertcol = False
        self.horcol = False


        self.damagecooldown = 2000
        self.takedamage = False
        self.damagetaken = 0

        self.levelup_message_duration = None
        self.levelupdisplay = False
        self.levelupmsg = ''

    def update(self, chunks, timedelta):

        # level check --- POWERUPS!!!
        self.score_needed = 100*(2**self.level) - self.score

        if self.score_needed <= 0:
            self.level += 1
            self.levelup_start_time = pygame.time.get_ticks()
            self.levelup_message_duration = 2000
            self.levelupdisplay = True

            print("level up")
            if self.level == 1:
                self.levelupmsg = ' 2x Jump Height!'
                self.jumpheight = -15
            elif self.level == 2:
                self.levelupmsg = ' +50HP'
                self.health += 50
            elif self.level == 3:
                self.levelupmsg = ' 2x Speed!'
                self.speed = self.speed * 2
            elif self.level == 4:
                self.levelupmsg = ' Sticky Bombs!'

            elif self.level == 5:
                self.levelupmsg = ' 1.5x Jump Height'
                self.jumpheight = self.jumpheight * 1.5


        self.damagecooldown -= timedelta
        # Get the state of all keyboard keys
        key = pygame.key.get_pressed()

        if not self.jumping and self.vertcol and not self.horcol and key[pygame.K_SPACE]:
            self.velocity_y += self.jumpheight
            self.jumping = True

        self.onground = False
        self.update_y(chunks)

        if self.takedamage and self.damagecooldown <= 0:
            self.health -= self.damagetaken
            self.takedamage = False
            self.damagetaken = 0
            self.damagecooldown = 2000

        if key[pygame.K_a]: 
            self.velocity_x = -self.speed

        elif key[pygame.K_d]:
            self.velocity_x = self.speed

        else:   
            self.velocity_x = 0

        # horizontal movement
        self.rect.x += self.velocity_x

        self.update_x(chunks)
        

    def update_y(self, chunks):
        """ Apply gravity, check collisions on y axis """
        # Apply gravity if not on ground
        if not self.onground:
            self.rect.y += self.velocity_y
            if self.velocity_y < 16: # totally forgot
                self.velocity_y += self.gravity

        self.vertcol = False

        for chunk in chunks:
            if not self.vertcol:
                if distance(self.rect.x, self.rect.y, chunk.rect.x, chunk.rect.y) < 2000:
                    self.check_collision_vert(chunk)
            else:
                break

    def update_x(self, chunks):
        """ Check horizontal collisions"""

        self.horcol = False

        for chunk in chunks:
            if not self.horcol:
                if distance(self.rect.x, self.rect.y, chunk.rect.x, chunk.rect.y) < 2000:
                    self.check_collision_hori(chunk)

            else:
                break  # Break if a collision is detected
        
class Bomb(Entity):

    def __init__(self, x, y):
        super().__init__()

        self.sprites = {
            "countdown_3": pygame.transform.scale(pygame.image.load("assets/bomb/bomb_3.png"), (int(gridchunk*0.75), int(gridchunk*0.75))),
            "countdown_2": pygame.transform.scale(pygame.image.load("assets/bomb/bomb_2.png"), (int(gridchunk*0.9), int(gridchunk*0.9))),
            "countdown_1": pygame.transform.scale(pygame.image.load("assets/bomb/bomb_1.png"), (int(gridchunk*0.75), int(gridchunk*0.75))),
            "flame": pygame.transform.scale(pygame.image.load("assets/bomb/flame.png"), (int(gridchunk*3), int(gridchunk*3)))  # explosion diameter = 3*chunk
        }

        self.image = self.sprites["countdown_3"]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.state = "countdown_3"
        self.bombtimer = 1200
        self.remove = False
        self.bombdamage = 10
        self.sticky = False # Level 4 upgrade

    def update(self, chunks, timedelta, player):

        self.bombtimer -= timedelta # bomb timer

        if self.bombtimer <= 300:
            self.explode(chunks, player)
        else:
            if not self.sticky:
                Entity.update(self, chunks)
            # Update the sprite based on remaining time
            if self.bombtimer <= 600:  # Last second
                self.state = "countdown_1"
            elif self.bombtimer <= 900:  # Second second
                self.state = "countdown_2"
            elif self.bombtimer <= 1200: # Third second
                self.state = "countdown_3"

            self.image = self.sprites[self.state]

    def explode(self, chunks, player):
        self.state = "boom"

        flame_sprite = self.sprites["flame"] # new rect for size of explosion sprite
        flame_rect = flame_sprite.get_rect() # since explosion is bigger than bomb

        original_center = self.rect.center
        flame_rect.center = original_center

        if self.bombtimer <= 0:
            self.remove = True

        for chunk in chunks:
            if flame_rect.colliderect(chunk.rect):
                chunk.blownup = True # mark chunks for removal
        
        if flame_rect.colliderect(player): # deal damage to player caught in blast
            if not player.takedamage:
                player.takedamage = True
                player.damagetaken = self.bombdamage

        self.image = flame_sprite
        self.rect = flame_rect

class Gold(Entity):

    def __init__(self, x, y, color):
        super().__init__()

        self.image = pygame.image.load("assets/entity/foodstuffs/{color}.png".format(color=color))
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH/34, SCREEN_WIDTH/34))

        self.rect = self.image.get_rect()

        self.rect.x = x*roundeddiv(SCREEN_WIDTH, 34)
        self.rect.y = y*roundeddiv(SCREEN_WIDTH, 34)

        self.worth = 100
        self.iskill = False

    def update(self, chunks, player):

        if not self.frozen:
            Entity.update(self, chunks)

            if self.rect.colliderect(player):
                self.iskill = True
                player.score += self.worth

class Enemy(Entity):

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.image.load("assets/entity/enemy.png")
        self.image = pygame.transform.scale(self.image, (gridchunk*0.75, gridchunk*0.75))

        self.rect = self.image.get_rect()

        self.rect.x = x*roundeddiv(SCREEN_WIDTH, 34) -1
        self.rect.y = y*roundeddiv(SCREEN_WIDTH, 34)

        self.randomjump = None
        self.speed = 3
        self.jumpheight = -5

        self.velocity_x = 2

        self.health = 10
        self.worth = 200

        self.iskill = False

    def update(self, chunks, player):

        Entity.update(self, chunks)
        random.seed(None)
        self.randomjump = random.choice([True, False])

        if self.randomjump and not self.jumping and self.onground:
            self.velocity_y = self.jumpheight


        if self.reflectx:
            self.velocity_x = -self.velocity_x

        self.rect.x += self.velocity_x

        self.reflectx = False



    pass

"""------------------------------------------------ Chunks ------------------------------------------------"""
class BorderChunk(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.image.load("assets/chunks/obby.png").convert()
        self.image = pygame.transform.scale(self.image, (gridchunk, gridchunk))

        self.rect = self.image.get_rect()

        self.rect.x = x*roundeddiv(SCREEN_WIDTH, 34) -1
        self.rect.y = y*roundeddiv(SCREEN_WIDTH, 34)

        self.canbreak = False
        self.blownup = False


class GroundChunk(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        dirtimg = pygame.image.load("assets/chunks/dirt4.png").convert()
        self.image = pygame.transform.scale(dirtimg, (gridchunk, gridchunk))

        self.rect = self.image.get_rect()

        self.rect.x = x*roundeddiv(SCREEN_WIDTH, 34) -1
        self.rect.y = y*roundeddiv(SCREEN_WIDTH, 34)

        self.canbreak = True
        self.blownup = False

"""-------------------------------------------- Supplementary --------------------------------------------"""

class Title(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('assets/text/title.png')
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.75))

        self.rect = self.image.get_rect()

        self.rect.centerx = SCREEN_WIDTH/2
        self.rect.centery = SCREEN_HEIGHT/2 - SCREEN_HEIGHT/24

"""------------------------------------------------ Game ------------------------------------------------"""

class Game:

    def __init__(self):
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.background = pygame.image.load('assets/text/background.png').convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # constants
        self.columns = 34
        self.rows = 60

        self.all_sprites_list = pygame.sprite.Group()

        self.chunklist = pygame.sprite.Group()
        self.visible_chunks = pygame.sprite.Group()
        self.entitylist = pygame.sprite.Group()

        self.player = Player()
        self.playergroup = pygame.sprite.GroupSingle()
        self.playergroup.add(self.player)

        self.bomblist = pygame.sprite.Group()
        self.bomb_refreshspan = 400
        self.bomb_refresh = 0

        self.enemylist = pygame.sprite.Group()

        self.title = Title()
        self.all_sprites_list.add(self.title)

        pygame.font.init()
        self.infofont = pygame.font.SysFont('arial', 30)
        self.fpsfont = pygame.font.SysFont('courier new', 10)

        self.goldlist = pygame.sprite.Group()

        # random.seed(None) # reinitialize seed gen
        """
        side note: This is where I'm kind of stuck with the terrain generator, it has more so
                   to do with the way seeds are seleted to initialize (where and when) the random
                   function call - when i set the seed to none, it uses exact system time, but what if
                   I want to play on the "Daniel" seed every time? - I also assign seed to null in
                   the enemy class - this is totally running on theory (hasn't exactly been tested
                   yet). So, time will tell if I have to delete this note or not
        """

        level_data = terrain_data_generator.terrainmap((random.random()), self.rows) # seed, rows
        foodcolors = ['red', 'green', 'blue', 'yellow']

        for row_index, row in enumerate(level_data):
            for str_index, char in enumerate(row):
                x, y = str_index, row_index
                if char == 'X':
                    chunk = GroundChunk(x, y)
                    self.chunklist.add(chunk)
                    self.all_sprites_list.add(chunk)

                elif char == '|':
                    chunk = BorderChunk(x, y)
                    self.chunklist.add(chunk)
                    self.all_sprites_list.add(chunk)

                elif char == '$':
                    color = random.choice(foodcolors)
                    gold = Gold(x, y, color)
                    self.goldlist.add(gold)
                    self.entitylist.add(gold)
                    self.all_sprites_list.add(gold)

                elif char == '%':
                    enemy = Enemy(x, y)
                    self.enemylist.add(enemy)
                    self.entitylist.add(enemy)
                    self.all_sprites_list.add(enemy)
                    print("enemy spawned at: ", x, y)


    def get_camera_offset(self, player):
        return SCREEN_HEIGHT / 2 - player.rect.y

    def poll(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
        key = pygame.key.get_pressed()

        if self.bomb_refresh <= 0:
            if key[pygame.K_DOWN]:
                x = self.player.rect.centerx
                y = self.player.rect.centery
                bomb = Bomb(x, y)
                self.bomblist.add(bomb)
                self.all_sprites_list.add(bomb)
                self.bomb_refresh = self.bomb_refreshspan

    def update(self):

        timedelta = self.clock.tick(60)
        self.bomb_refresh -= timedelta

        visible_range = [self.player.rect.y - SCREEN_HEIGHT, self.player.rect.y + SCREEN_HEIGHT]

        # remove dead chunks
        for chunk in self.visible_chunks:
            if chunk.blownup and chunk.canbreak:
                self.visible_chunks.remove(chunk)
                self.chunklist.remove(chunk)
                self.all_sprites_list.remove(chunk)

            if not (visible_range[0] < chunk.rect.y < visible_range[1]):
                self.visible_chunks.remove(chunk)

        # add/revive chunks in range
        for chunk in self.chunklist:
            if visible_range[0] < chunk.rect.y < visible_range[1] and chunk not in self.visible_chunks:
                self.visible_chunks.add(chunk)

        self.visible_chunks.update()

        self.player.update(self.visible_chunks, timedelta)

        for bomb in self.bomblist:
            if not bomb.remove:
                bomb.update(self.visible_chunks, timedelta, self.player)
            else:
                self.bomblist.remove(bomb)
                self.all_sprites_list.remove(bomb)


        for entity in self.entitylist:
            if visible_range[0] < entity.rect.y < visible_range[1]:
                self.frozen = False
                entity.update(self.visible_chunks, self.player) # entities falling thru ground when off screen/// dunno y 
            else:
                self.frozen = True
       
            if entity in self.goldlist:
                if entity.iskill:
                    self.entitylist.remove(entity)
                    self.goldlist.remove(entity)
                    self.all_sprites_list.remove(entity)
        
        current_time = pygame.time.get_ticks()
        if self.player.levelupdisplay and (current_time - self.player.levelup_start_time > self.player.levelup_message_duration):
            self.player.levelupdisplay = False


    def draw(self):

        # Calculate the camera offset
        camera_offset = self.get_camera_offset(self.player)

        # Fill the screen with black
        self.screen.blit(self.background, (0, 0))

        # moving everything along y with player
        for sprite in self.all_sprites_list:
            offset_rect = sprite.rect.copy() # create copy of sprite
            offset_rect.y += camera_offset # apply camera offset
            self.screen.blit(sprite.image, offset_rect) 

        player_offset_rect = self.player.rect.copy() # this is the only way i could get the player to draw
        player_offset_rect.y += camera_offset # I dont think its the best way but if it fits it ships
        self.screen.blit(self.player.image, player_offset_rect)

        self.score_text = self.infofont.render('Next Level Points Needed: ' + str(self.player.score_needed), True, (255, 255, 255), (0,0,0))
        self.screen.blit(self.score_text, [15, SCREEN_HEIGHT- 80])

        self.health_text = self.infofont.render('Health: ' + str(self.player.health), True, (255, 0, 0), (0,0,0))
        self.screen.blit(self.health_text, [15, SCREEN_HEIGHT-40])

        self.health_text = self.infofont.render('Food Left: ' + str(len(self.goldlist)), True, (255, 0, 0), (0,0,0))
        self.screen.blit(self.health_text, [15, SCREEN_HEIGHT-120])

        self.lvlmsg = self.infofont.render('Level Up!' + self.player.levelupmsg, True, (255, 255, 255), (0,0,0))

        if self.player.levelupdisplay:
            self.screen.blit(self.lvlmsg, [SCREEN_WIDTH/2, SCREEN_HEIGHT/2])



    def run(self):
        # Main program loop
        while self.running:

            if self.player.health <= 0:
                break

            # Event processing
            self.poll()

            # Game logic
            self.update()

            # Draw a frame
            self.draw()

            # Update the screen
            pygame.display.flip()

            # Limit frames per second
            self.clock.tick(60)

            # print("FPS:", int(self.clock.get_fps()))

            # debug info

if __name__ == '__main__':
    g = Game()
    print("starting...")
    g.run()
    print("shutting down...")
    pygame.quit()
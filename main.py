
import pygame
import random
import terrain_data_generator

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

"""------------------------------------------------ Supp Formulas ------------------------------------------------"""

def distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """ Calc squared distance between two points """
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


    # try except in event of 0div

def roundeddiv(x: int, y: int) -> int:
    """ Return a rounded division between two int"""
    try: return round(x/y)
    except: pass

# 1 Unit of measurement, each tile is gcxgc
gridchunk = roundeddiv(SCREEN_WIDTH, 33)

"""------------------------------------------------ Entities ------------------------------------------------"""

class Entity(pygame.sprite.Sprite):
    """ Anything that has gravity and collisions, Pretty much """
    def __init__(self):
        super().__init__()
        self.gravity = 1
        self.velocity_y = 1
        self.velocity_x = 0
        self.MAX_FALL_SPEED = 20

        # flags
        self.onground = False
        self.jumping = False
        self.frozen = False
        self.reflectx = False
        self.vertcol = False
        self.horcol = False

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


class Player(Entity):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/entity/player.png")
        self.image = pygame.transform.scale(self.image, (gridchunk*0.4, gridchunk*0.5))
        self.rect = self.image.get_rect()

        self.rect.x = SCREEN_WIDTH / 2
        self.rect.y = gridchunk * 10

        self.speed = 4
        self.jumpheight = -10
        self.max_velocity_y = None

        self.health = 100
        self.score = 0
        self.level = 0

        self.damagecooldown = 1000
        self.takedamage = False
        self.damagetaken = 0

        self.score_needed = 100
        self.levelup_message_duration = None
        self.levelupdisplay = False
        self.levelupmsg = ''

    def update(self, chunks, timedelta, enemies):

        self.levelup()
        self.handle_damage(timedelta, enemies)
        self.process_input()

        self.onground = False
        super().update_y(chunks)

        self.rect.x += self.velocity_x
        super().update_x(chunks)

    def process_input(self):
        """ Take Player inputs """
        key = pygame.key.get_pressed()
        if not self.jumping and self.vertcol and not self.horcol and key[pygame.K_SPACE]:
            self.velocity_y += self.jumpheight
            self.jumping = True

        if key[pygame.K_a]:
            self.velocity_x = -self.speed
        elif key[pygame.K_d]:
            self.velocity_x = self.speed
        else:
            self.velocity_x = 0

    def levelup(self):
        """ Handle leveling system """
        self.score_needed = 100*(2**self.level) - self.score

        if self.score_needed <= 0:
            self.level += 1
            self.levelup_start_time = pygame.time.get_ticks()
            self.levelup_message_duration = 3000
            self.levelupdisplay = True

            match self.level:
                case 1:
                    self.levelupmsg = ' 2x Jump Height!'
                    self.jumpheight = -15
                case 2:
                    self.levelupmsg = ' +50HP'
                    self.health += 50
                case 3:
                    self.levelupmsg = ' 2x Speed!'
                    self.speed *= 2
                case 4:
                    self.levelupmsg = ' Sticky Bombs!'
                    # logic handled in bombs
                case 5:
                    self.levelupmsg = ' 1.5x Jump Height'
                    self.jumpheight *= 1.5
                case _:
                    self.levelupmsg = ' +50HP'
                    self.health += 50


    def handle_damage(self, timedelta, enemies):
        """ Process damage """
        self.damagecooldown -= timedelta
        if self.damagecooldown <= 0:
            self.ouch(enemies)
            if self.takedamage:
                self.health -= self.damagetaken
                self.takedamage = False
                self.damagetaken = 0
                self.damagecooldown = 1000  # Reset cooldown

    def ouch(self, enemies):
        for enemy in enemies:
            if distance(self.rect.x, self.rect.y, enemy.rect.x, enemy.rect.y) < 500: # basically overlapping
                self.takedamage = True
                self.damagetaken += 30

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
        self.bombdamage = 10 #damage per tick (I am NOT messing around with any mroe timers)

    def update(self, chunks, timedelta, player, enemies):

        self.bombtimer -= timedelta # bomb timer

        if self.bombtimer <= 300:
            self.explode(chunks, player, enemies)
        else:
            if not player.level >= 4:
                Entity.update_y(self, chunks)
            # Update the sprite based on remaining time
            if self.bombtimer <= 600:  # Last second
                self.state = "countdown_1"
            elif self.bombtimer <= 900:  # Second second
                self.state = "countdown_2"
            elif self.bombtimer <= 1200: # Third second
                self.state = "countdown_3"

            self.image = self.sprites[self.state]

    def explode(self, chunks, player, enemies):
        self.state = "boom"
        self.image = self.sprites["flame"]
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.bombtimer <= 0:
            self.remove = True

        for chunk in chunks:
            if self.rect.colliderect(chunk.rect):
                chunk.blownup = True

        if self.rect.colliderect(player.rect) and not player.takedamage:
            player.takedamage = True
            player.damagetaken = self.bombdamage * 0.2

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.receive_damage(self.bombdamage)

class Gold(Entity):

    def __init__(self, x, y, color):
        super().__init__()

        self.image = pygame.image.load("assets/entity/foodstuffs/{color}.png".format(color=color))
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH/34, SCREEN_WIDTH/34))

        self.rect = self.image.get_rect()

        self.rect.x = x*roundeddiv(SCREEN_WIDTH, 34)
        self.rect.y = y*roundeddiv(SCREEN_WIDTH, 34)

        self.worth = 50
        self.iskill = False

    def update(self, chunks, player):
        Entity.update_y(self, chunks) # only needs y checks

        if self.rect.colliderect(player):
            self.iskill = True

class Enemy(Entity):
    """General enemy class that other enemy types can inherit from."""
    def __init__(self, x, y, image_path, gridmultiple, health=50, worth=100, speed=1, jumpheight=-10):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (gridchunk * gridmultiple, gridchunk * gridmultiple))
        self.rect = self.image.get_rect()
        self.rect.x = x * roundeddiv(SCREEN_WIDTH, 34) - 1
        self.rect.y = y * roundeddiv(SCREEN_WIDTH, 34)

        self.speed = speed
        self.jumpheight = jumpheight
        self.health = health
        self.worth = worth

        self.velocity_x = 2
        self.VX = 2  # Constant for velocity reset/switch

        self.player_in_range = False
        self.iskill = False
        self.take_damage = False
        self.damagetaken = 0
        self.dojump = False
        self.randomjump = None

    def update(self, chunks, player, bomblist=None, all_sprites_list=None):
        """ Determine walk cycle -> check collisions -> die"""

        if distance(self.rect.x, self.rect.y, player.rect.x, player.rect.y) < (SCREEN_WIDTH / 6) ** 2:
            if isinstance(self, Grunts): self.seek(player)
            if isinstance(self, Boss): self.seek(player, bomblist=bomblist, all_sprites_list=all_sprites_list)
        else:
            self.wander()
        
        # Handling jump action
        if self.dojump and not self.jumping and self.onground:
            self.velocity_y = self.jumpheight
            self.dojump = False

        # Update vertical position and check for x-axis reflection
        super().update_y(chunks)
        if self.reflectx:
            self.velocity_x = -self.velocity_x

        # Move and update horizontal position
        self.rect.x += self.velocity_x * self.speed
        super().update_x(chunks)
        self.reflectx = False

    def receive_damage(self, damage):
        self.take_damage = True
        self.damagetaken += damage
        self.get_hurt()

    def get_hurt(self):
        if self.health <= 0:
            self.iskill = True
        else:
            self.apply_damage()

    def apply_damage(self):
        self.health -= self.damagetaken
        self.takedamage = False
        self.damagetaken = 0

    def seek(self, player):
        if player.rect.y in range(self.rect.y - gridchunk * 3, self.rect.y + gridchunk * 3 + 1):
            self.velocity_x = -self.VX if self.rect.x > player.rect.x else self.VX

        if random.randrange(1, 20) == 1:
            self.dojump = True

    def wander(self):
        if random.randrange(20) == 1:
            self.reflectx = True
        elif random.randrange(20) == 2:
            self.dojump = True


class Grunts(Enemy):
    """ Entity > Enemy > Boss """
    def __init__(self, x, y):
        super().__init__(x, y, "assets/entity/enemy.png", 0.75)

class Boss(Enemy):
    """ Entity > Enemy > Boss """
    def __init__(self, x, y):
        super().__init__(x, y, "assets/entity/player.png", 3, health=1000, worth=1000)
        self.image = pygame.transform.scale(self.image, (gridchunk*3, gridchunk*3))
    
    def update(self, chunks, player, bomblist, all_sprites_list):
        super().update(chunks, player, bomblist, all_sprites_list)

    def seek(self, player, bomblist, all_sprites_list): # boss override (better seeking)
        if player.rect.y in range(self.rect.y - gridchunk * 6, self.rect.y + gridchunk * 6):
            self.velocity_x = -self.VX if self.rect.x > player.rect.x else self.VX
            
        action = random.randrange(1, 30)

        match action:
            case 1: self.dojump = True
            case 2: 
                if random.randrange(1,6) == 1: # additional odds, agian, not messing w/ timers
                    self.place_bomb(bomblist, all_sprites_list)

    def place_bomb(self, bomblist, all_sprites_list):
        """Boss can place a bomb"""
        x = self.rect.centerx
        y = self.rect.centery
        bomb = Bomb(x, y)
        bomblist.add(bomb)
        all_sprites_list.add(bomb)


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

        pygame.display.set_caption('Cave Game 2D: Baka Edition')
        icon = pygame.image.load('assets/text/icon.png')
        pygame.display.set_icon(icon)

        self.background = pygame.image.load('assets/text/background.png').convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.startup_screen = pygame.image.load('assets/text/logo.png').convert_alpha()
        self.startup_screen = pygame.transform.scale(self.startup_screen, (SCREEN_WIDTH*0.5, SCREEN_HEIGHT*0.3))

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
        self.boss_spawned = False
        self.boss_defeated = False

        self.title = Title()
        self.all_sprites_list.add(self.title)

        pygame.font.init()
        self.infofont = pygame.font.SysFont('arial', 30)
        self.fpsfont = pygame.font.SysFont('courier new', 10)

        self.goldlist = pygame.sprite.Group()

        random.seed(None) # reinit seed as none (takes system time, pretty neat)
        self.seed = terrain_data_generator.ftd()

        level_data = terrain_data_generator.terrainmap((self.seed), self.rows) # seed, rows
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
                    enemy = Grunts(x, y)
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


        self.visible_chunks = {chunk for chunk in self.chunklist if visible_range[0] < chunk.rect.y < visible_range[1]}
        
        # remove blown up chunks
        for chunk in self.visible_chunks.copy():
            if chunk.blownup and chunk.canbreak:
                self.chunk_removal(chunk)

        # Update player
        self.player.update(self.visible_chunks, timedelta, self.enemylist)

        # Update bombs, update entities, check for levelup
        self.update_bombs(timedelta)
        self.update_entities(visible_range)
        self.levelup_display()

        if self.player.rect.y >= 3100 and not self.boss_spawned:
            self.boss_fight()

    def chunk_removal(self, chunk):
        self.visible_chunks.discard(chunk)
        self.chunklist.remove(chunk)
        self.all_sprites_list.remove(chunk)

    def update_bombs(self, timedelta):
        for bomb in self.bomblist:
            if bomb.remove:
                self.bomblist.remove(bomb)
                self.all_sprites_list.remove(bomb)
            else:
                bomb.update(self.visible_chunks, timedelta, self.player, self.enemylist)

    def update_entities(self, visible_range):
        for entity in self.entitylist:
            if entity.iskill:
                self.entity_removal(entity)
            
            if visible_range[0] < entity.rect.y < visible_range[1]:
                if not isinstance(entity, Boss):
                    entity.update(self.visible_chunks, self.player)

                elif isinstance(entity, Boss):
                    entity.update(self.visible_chunks, self.player, self.bomblist, self.all_sprites_list)

    def entity_removal(self, entity):
        self.player.score += entity.worth
        if isinstance(entity, Gold): self.goldlist.remove(entity)
        if isinstance(entity, Enemy): self.enemylist.remove(entity)
        self.entitylist.remove(entity)
        self.all_sprites_list.remove(entity)

    def levelup_display(self):
        current_time = pygame.time.get_ticks()
        if self.player.levelupdisplay and (current_time - self.player.levelup_start_time > self.player.levelup_message_duration):
            self.player.levelupdisplay = False

    def boss_fight(self):
        boss = Boss(23, 80) # 23, 80 for floor, 23, 6 for top
        self.enemylist.add(boss)
        self.entitylist.add(boss)
        self.all_sprites_list.add(boss)
        self.boss = pygame.sprite.GroupSingle(boss)
        self.boss_spawned = True

        pass

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

        self.lvlmsg = self.infofont.render('Level Up!' + self.player.levelupmsg, True, (255, 255, 255), (0,0,0))
        text_width, text_height = self.lvlmsg.get_size()
        centered_x = (SCREEN_WIDTH - text_width) / 2
        centered_y = (SCREEN_HEIGHT - text_height) / 2

        if self.player.levelupdisplay:
            self.screen.blit(self.lvlmsg, [centered_x, centered_y])

        if self.boss_spawned:
            boss = self.boss.sprite
            if boss.health != 0:
                self.draw_boss_health_bar(self.screen, boss)
            else:
                self.boss_defeated = True

        if self.boss_defeated:
            self.running = False


    def draw_boss_health_bar(self, screen, boss):
        # Health bar dimensions and position
        bar_width = SCREEN_WIDTH/4
        bar_height = 20
        x = SCREEN_WIDTH / 2 - bar_width/2
        y = 20  # Distance from the top of the screen

        # Calculate the width of the red health bar
        health_ratio = boss.health / 500
        health_bar_width = bar_width * health_ratio

        # Draw the grey background bar
        pygame.draw.rect(screen, (128, 128, 128), (x, y, bar_width, bar_height))
        # Draw the red health bar over it
        pygame.draw.rect(screen, (255, 0, 0), (x, y, health_bar_width, bar_height))


    def start_screen(self):
        """Displays the startup screen until any key is pressed."""
        startup = True
        while startup:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    startup = False

            self.screen.fill((0, 0, 0))
            logo_x = SCREEN_WIDTH / 2 - self.startup_screen.get_width() / 2
            logo_y = SCREEN_HEIGHT / 2 - self.startup_screen.get_height() / 2 - 50  # Adjust Y to move logo up from center
            self.screen.blit(self.startup_screen, (logo_x, logo_y))

            # Display startup screen text below the logo
            start_text = self.infofont.render('Press any key to start', True, (255, 255, 255))
            text_x = SCREEN_WIDTH / 2 - start_text.get_width() / 2
            text_y = SCREEN_HEIGHT / 2 + 50  # Adjust Y to position text below the logo
            self.screen.blit(start_text, (text_x, text_y))

            seed_text = self.infofont.render(("seed: {}".format(self.seed)), True, (255, 255, 255))
            text_x = SCREEN_WIDTH / 2 - seed_text.get_width() / 2
            text_y = SCREEN_HEIGHT / 2 + 150  # Adjust Y to position text below the logo
            self.screen.blit(seed_text, (text_x, text_y))

            pygame.display.flip()
            self.clock.tick(60)

    def thanks_screen(self):
        """ win screen """
        startup = True
        while startup:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.screen.fill((0, 0, 0))
            
            logo_x = SCREEN_WIDTH / 2 - self.startup_screen.get_width() / 2
            logo_y = SCREEN_HEIGHT / 2 - self.startup_screen.get_height() / 2 - 50  # Adjust Y to move logo up from center
            self.screen.blit(self.startup_screen, (logo_x, logo_y))

            start_text = self.infofont.render('Thanks for Playing', True, (255, 255, 255))
            text_x = SCREEN_WIDTH / 2 - start_text.get_width() / 2
            text_y = SCREEN_HEIGHT / 2 + 50 
            self.screen.blit(start_text, (text_x, text_y))

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        # anykey screen
        self.start_screen()

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

        self.thanks_screen()
        # and if you've made it this far into reading, thanks for reading too!
        # I'm going to sleep now thx again.
            

if __name__ == '__main__':
    g = Game()
    print("starting...")
    g.run()
    print("shutting down...")
    pygame.quit()
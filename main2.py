import pygame
from pygame import mixer
import random
from pygame.locals import *
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# define fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

# define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)
piratefont = pygame.font.SysFont('xfiles', 40)
# load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

# song_fx = pygame.mixer.Sound("music/Duckshoot.mid")
# song_fx.set_volume(1.00)

pygame.mixer.music.load("music/Duckshoot.mid") # Load an audio file into memory
pygame.mixer.music.play(-1) # Play the audio file in a loop (-1 means infinite loop)


# define game variables
rows = 3
cols = 5
alien_cooldown = 1000  # bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0  # 0 is no game over, 1 means player has won, -1 means player has lost

# define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# load image
bg = pygame.image.load("img/bg.png")
bg_blue = pygame.image.load("img/bg_blue.png")
top_bg = pygame.image.load("img/top_bg.png")
top_bluebg = pygame.image.load("img/top_blue_bg.png")

initial_ammo_count = 50
firebutton_press = False

# def play_music(midi_filename):
#     '''Stream music_file in a blocking manner'''
#     clock = pygame.time.Clock()
#     pygame.mixer.music.load(midi_filename)
#     pygame.mixer.music.play()
#     while pygame.mixer.music.get_busy():
#         clock.tick(30)  # check if playback has finished
#
#
# midi_filename = 'music/song.mid'
#
# # mixer config
# freq = 44100  # audio CD quality
# bitsize = -16  # unsigned 16 bit
# channels = 2  # 1 is mono, 2 is stereo
# buffer = 1024  # number of samples
# pygame.mixer.init(freq, bitsize, channels, buffer)


# optional volume 0 to 1.0
# pygame.mixer.music.set_volume(0.8)

# listen for interruptions
# try:
#   # use the midi file you just saved
#   #play_music(midi_filename)
# except KeyboardInterrupt:
#   # if user hits Ctrl/C then exit
#   # (works only in console mode)
#   pygame.mixer.music.fadeout(1000)
#   pygame.mixer.music.stop()
#   raise SystemExit


def draw_bg():
    screen.blit(bg_blue, (0, 50))


# define function for creating text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))



# create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/gun.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # set movement speed
        speed = 8
        # set a cooldown variable
        cooldown = 500  # milliseconds
        game_over = 0

        # get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now
            # deduct one from ammo count
            ammo_tracker.set_ammo_count(ammo_tracker.get_ammo_count()-1)
            ammo_tracker.set_fire_button_press(True)

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (
            self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)),
            15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

class ScoreBoard():
    def __init__(self, initial_score):
        self.score = initial_score

    def get_score(self):
        return self.score

    def set_score(self, new_score):
        self.score = new_score

    def display_score(self):
        self.level  = 1
        self.hi_score = 1000
       # screen.blit(top_bluebg, (0, 0))
        pygame.draw.line(screen, white, (0, 3), (600, 3), 5)
        draw_text('SC=' + str(self.score), piratefont, white, int(10), int(8))
        draw_text('LEV=' + str(self.level), piratefont, white, int(200), int(8))
        draw_text('HI=' + str(self.hi_score), piratefont, white, int(400), int(8))
        pygame.draw.line(screen, white, (0, 42), (600, 42), 5)
        fonts = pygame.font.get_fonts()
        # for font in fonts:
        #     print(font)

class AmmoTracker():
    def __init__(self):
        self.ammo_count = initial_ammo_count

    def get_ammo_count(self):
        return self.ammo_count

    def set_ammo_count(self, ammo_count):
        self.ammo_count = ammo_count

    def display_score(self):
        ammo = Ammo(self.ammo_count * 10, 200)
        ammo_group.add(ammo)

    def set_fire_button_press(self, button_press):
        self.fire_button_press = button_press

    def get_fire_button_press(self):
        return self.fire_button_press

# create Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
         pygame.sprite.Sprite.__init__(self)
         self.image = pygame.image.load("img/bullet.png")
         self.rect = self.image.get_rect()
         self.rect.center = [x, y]

    def update(self, scoreBoard):
        self.rect.y -= 5
        if self.rect.bottom < 55:
            self.kill()
        if pygame.sprite.spritecollide(self, mysteryship_group, True) or pygame.sprite.spritecollide(self, mysteryrabbit_group, True) or pygame.sprite.spritecollide(self, mysteryscorebox_group, True):
            scoreBoard.set_score(scoreBoard.get_score() + 1)
            scoreBoard.display_score()
            self.kill()

            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

# create Aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

# create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, mysteryship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

        if pygame.sprite.spritecollide(self, mysteryrabbit_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

        if pygame.sprite.spritecollide(self, mysteryscorebox_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

class RowTracker():
    def __init__(self):
        self.startRow = False
    def setStartRow(self):
        self,startRow = True
    def getStartRow(self):
        return self.startRow

class Mysteryship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.init_x_pos = x
        self.init_y_pos = y
        self.image = pygame.image.load("img/alien1.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0
        self.ufo_move_direction = 1


    def update(self):
        self.rect.x += self.ufo_move_direction
        self.ufo_move_counter += 10
        if abs(self.ufo_move_counter) > 6000:
            #self.ufo_move_direction *= -1

            #self.rect = self.image.get_rect()
            #self.rect.center = [self.init_x_pos, self.init_y_pos]
            #self.ufo_move_counter = 0
            #self.ufo_move_direction = 1
            #self.ufo_move_counter *= self.ufo_move_direction
            self.kill()




class MysteryRabbit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien2.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0
        self.ufo_move_direction = 1


    def update(self):
        self.rect.x += self.ufo_move_direction
        self.ufo_move_counter += 10
        if abs(self.ufo_move_counter) > 6000:
            #self.ufo_move_direction *= -1
            #self.ufo_move_counter *= self.ufo_move_direction
            self.kill()

class Ammo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/ammo.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self, remove):
        if remove:
            self.kill()

class EmptyAmmo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/emptyammo.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self, remove):
        if remove:
            self.kill()

class MysteryScoreBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien3.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0
        self.ufo_move_direction = 1


    def update(self):
        self.rect.x += self.ufo_move_direction
        self.ufo_move_counter += 10
        if abs(self.ufo_move_counter) > 6000:
            #self.ufo_move_direction *= -1
            #self.ufo_move_counter *= self.ufo_move_direction
            self.kill()

# create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
mysteryship_group = pygame.sprite.Group()
mysteryrabbit_group = pygame.sprite.Group()
mysteryscorebox_group = pygame.sprite.Group()
ammo_group = pygame.sprite.Group()
ammo_tracker = AmmoTracker()
ammo_tracker.set_fire_button_press(False)

def create_ammo_bar():
    ammo_tracker.get_ammo_count()
    print ("ammo_tracker.get_ammo_count()" +str(ammo_tracker.get_ammo_count()))
    count = ammo_tracker.get_ammo_count()
    print("count" +  str(count))
    for x_position in range(ammo_tracker.get_ammo_count()):
        print("ammo" + str(x_position))
        create_ammo(x_position, "ammo")
    ammo_tracker.display_score()

def create_ammo(x_position, type):
    spacing = 5
    if type == "ammo":
        ammo = Ammo(x_position * spacing, 790)
        ammo_group.add(ammo)
    else:
        empty_ammo = EmptyAmmo(x_position * spacing, 790)
        ammo_group.add(empty_ammo)

def create_ufos():
    # generate ufo
    for row in range(rows):
        for item in range(cols):
            spacing = random.randint(40, 100)
            offset = random.randint(1, 7)
            item_type = random.randint(1, 3)
            if item_type == 1:
                mystery_ship = Mysteryship(offset + item * spacing, 400 + row * 70)
                mysteryship_group.add(mystery_ship)
            elif item_type == 2:
                mystery_rabbit = MysteryRabbit(offset + item * spacing, 400 + row * 70)
                mysteryrabbit_group.add(mystery_rabbit)
            elif item_type == 3:
                mystery_scorebox = MysteryScoreBox(offset + item * spacing, 400 + row * 70)
                mysteryscorebox_group.add(mystery_scorebox)
score = 0
draw_bg()
scoreBoard = ScoreBoard(0)
scoreBoard.display_score()
create_ammo_bar()
create_ufos()


#screen.fill((255,255,0))
#pygame.display.update()
# create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

# create UFO
# mystery = Mysteryship(300, 60)
# mysteryship_group.add(mystery)
# mystery = Mysteryship(400, 60)
# mysteryship_group.add(mystery)
# mystery = Mysteryship(500, 60)
# mysteryship_group.add(mystery)
# mystery = Mysteryship(600, 60)
# mysteryship_group.add(mystery)



run = True
#song_fx.play()
while run:
    ammo_tracker.set_fire_button_press(False)
    clock.tick(fps)

    # draw background
    draw_bg()

    if countdown == 0:
        # create random alien bullets
        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        # check if all the aliens have been killed
        if len(mysteryship_group) == 0:
            create_ufos()

        if len(mysteryship_group) == 0 and len(mysteryrabbit_group) and len(mysteryscorebox_group):
            game_over = 1

        if game_over == 0:
            # update spaceship
            game_over = spaceship.update()

            # update sprite groups
            bullet_group.update(scoreBoard)
            alien_group.update()
            alien_bullet_group.update( )

            mysteryship_group.update()
            mysteryrabbit_group.update()
            mysteryscorebox_group.update()

            if ammo_tracker.get_fire_button_press():
                print("ammo tracker" + str (ammo_tracker.get_ammo_count()))
                ammo_group.update(False)
                create_ammo(ammo_tracker.get_ammo_count(), "emptyammo")
            if ammo_tracker.get_ammo_count()<=0:
                game_over=2

        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
            if game_over == 2:
                draw_text('OUT OF AMMO BASTARD!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))


    if countdown > 0:
        draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    # update explosion group
    explosion_group.update()

    # draw sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    mysteryship_group.draw(screen)
    mysteryrabbit_group.draw(screen)
    mysteryscorebox_group.draw(screen)

    ammo_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

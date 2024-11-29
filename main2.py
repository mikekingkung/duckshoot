import time

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
object_counter = rows * cols
# define colours
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# load image
bg = pygame.image.load("img/bg.png")
bg_blue = pygame.image.load("img/new_bg_blue.png")
top_bg = pygame.image.load("img/top_bg.png")
top_bluebg = pygame.image.load("img/top_blue_bg.png")

initial_ammo_count = 27
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
#   # use the midi file youjust saved
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
class Gun(pygame.sprite.Sprite):
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
        # pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        # if self.health_remaining > 0:
        #     pygame.draw.rect(screen, green, (
        #     self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)),
        #     15))
        # elif self.health_remaining <= 0:
        #     explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
        #     explosion_group.add(explosion)
        #     self.kill()
        #     game_over = -1
        return game_over


class TimeBoard():

    def __init__(self, text, counter):
        self.text = text
        self.counter = counter

    def display_timer(self):
        screen.blit(top_bluebg, (530, screen_height - 50))
        #pygame.draw.line(screen, white, (0, 794), (600, 794), 7)
        draw_text(str(self.text), piratefont, white, int(530), int(760))
        #pygame.draw.line(screen, white, (0, 734), (600, 734), 7)

    def setText(self, text):
        self.text = text


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
        screen.blit(top_bluebg, (0, 0))
        pygame.draw.line(screen, white, (0, 4), (600, 4), 7)
        draw_text('SC=' + str(self.score), piratefont, white, int(10), int(8))
        draw_text('LEV=' + str(self.level), piratefont, white, int(200), int(8))
        draw_text('HS=' + str(self.hi_score), piratefont, white, int(400), int(8))

        pygame.draw.line(screen, white, (0, 45), (600, 45), 7)
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
        print("hello")
        # draw_text('SC=' + str(self.score), piratefont, white, int(10), int(8))
        #ammo = Ammo(self.ammo_count * 10, 200)
        #ammo_group.add(ammo)

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
        if self.rect.bottom < 57:
            self.kill()
        if pygame.sprite.spritecollide(self, duck_group, True) or pygame.sprite.spritecollide(self, rabbit_group, True) or pygame.sprite.spritecollide(self, scorebox5_group, True) or pygame.sprite.spritecollide(self, scorebox10_group, True) or pygame.sprite.spritecollide(self, owl_group, True):
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

class ObjectCount():
    def __init__(self, initial_count):
        self.object_count = initial_count

    def reduce_object_count(self):
        self.object_count = self.object_count - 1
        print("object count:" + str(object_count))

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
        if pygame.sprite.spritecollide(self, duck_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            gun.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            ObjectCount.reduce_object_count()

        if pygame.sprite.spritecollide(self, rabbit_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            gun.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

        if pygame.sprite.spritecollide(self, scorebox5_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            gun.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

        if pygame.sprite.spritecollide(self, scorebox10_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            gun.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

        if pygame.sprite.spritecollide(self, owl_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # reduce spaceship health
            gun.health_remaining -= 1
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

class Duck(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.initial_x = x
        self.initial_y = y
        self.image = pygame.image.load("img/duck.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.duck_move_counter = 0
        self.duck_move_direction = direction

    def reset(self):
        x = generate_random_x()
        y = self.initial_y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.duck_move_counter = 0

    def update(self):
        self.rect.x += self.duck_move_direction
        self.duck_move_counter += 10
        if abs(self.duck_move_counter) > 6000:
            self.reset()


class Owl(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.initial_x = x
        self.initial_y = y
        self.image = pygame.image.load("img/owl.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.owl_move_counter = 0
        self.owl_move_direction = direction

    def reset(self):
        x = generate_random_x()
        y = self.initial_y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.owl_move_counter = 0

    def update(self):
         self.rect.x += self.owl_move_direction
         self.owl_move_counter += 10
         if abs(self.owl_move_counter) > 6000:
            self.reset()


class Rabbit(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.initial_x = x
        self.initial_y = y
        self.image = pygame.image.load("img/rabbit.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0
        self.ufo_move_direction = direction

    def reset(self):
        x = generate_random_x()
        y = self.initial_y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0

    def update(self):
        self.rect.x += self.ufo_move_direction
        self.ufo_move_counter += 10
        if abs(self.ufo_move_counter) > 6000:
            self.reset()



class ScoreBox5(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        self.initial_x = x
        self.initial_y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/5.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0
        self.ufo_move_direction = direction

    def reset(self):
        x = generate_random_x()
        y = self.initial_y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0

    def update(self):
        self.rect.x += self.ufo_move_direction
        self.ufo_move_counter += 10
        if abs(self.ufo_move_counter) > 6000:
            self.reset()

class ScoreBox10(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.initial_x = x
        self.initial_y = y
        self.image = pygame.image.load("img/10.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0
        self.ufo_move_direction = direction

    def reset(self):
        x = generate_random_x()
        y = self.initial_y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.ufo_move_counter = 0

    def update(self):
        self.rect.x += self.ufo_move_direction
        self.ufo_move_counter += 10
        if abs(self.ufo_move_counter) > 6000:
            self.reset()


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

# create sprite groups
gun_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
duck_group = pygame.sprite.Group()
rabbit_group = pygame.sprite.Group()
scorebox5_group = pygame.sprite.Group()
scorebox10_group = pygame.sprite.Group()
owl_group = pygame.sprite.Group()
ammo_group = pygame.sprite.Group()
ammo_tracker = AmmoTracker()
ammo_tracker.set_fire_button_press(False)

def create_ammo_bar():
    #ammo_tracker.get_ammo_count()
    #print ("ammo_tracker.get_ammo_count()" +str(ammo_tracker.get_ammo_count()))
    count = ammo_tracker.get_ammo_count()
    #print("count" +  str(count))
    for x_position in range(ammo_tracker.get_ammo_count()):
        print("mike ammo" + str(x_position))
        create_ammo(x_position, "ammo")
    ammo_tracker.display_score()

def create_ammo(x_position, type):
    #screen.blit(top_bluebg, (0, screen_height - 100))
    spacing = 5
    if type == "ammo":
        ammo = Ammo(x_position * 20 , 790)
        ammo_group.add(ammo)
    else:
        empty_ammo = EmptyAmmo(x_position * 20, 790)
        ammo_group.add(empty_ammo)

def create_artefacts():
    # generate ufo
    for row in range(rows):
        if row == 0:
            direction = 1
        elif row == 1:
            direction = -1
        elif row == 2:
            direction = 1
        else:
            direction = 1
        for item in range(cols):
            spacing = random.randint(60, 120)
            offset = random.randint(1, 30)
            item_type = random.randint(1, 5)
            if item_type == 1:
                duck = Duck(offset + (item * spacing), 400 + row * 70, direction)
                duck_group.add(duck)
            elif item_type == 2:
                rabbit = Rabbit(offset + (item * spacing), 400 + row * 70, direction)
                rabbit_group.add(rabbit)
            elif item_type == 3:
                scorebox5 = ScoreBox5(offset + (item * spacing), 400 + row * 70, direction)
                scorebox5_group.add(scorebox5)
            elif item_type == 4:
                scorebox10 = ScoreBox10(offset + (item * spacing), 400 + row * 70, direction)
                scorebox10_group.add(scorebox10)
            elif item_type == 5:
                owl = Owl(offset + (item * spacing), 400 + row * 70, direction)
                owl_group.add(owl)

def generate_random_x():
    spacing = random.randint(60, 120)
    offset = random.randint(1, 30)
    item =  random.randint(1, cols)
    x_val = offset + (item * spacing)
    return x_val

score = 0
draw_bg()
scoreBoard = ScoreBoard(0)
scoreBoard.display_score()
create_ammo_bar()
object_count = ObjectCount(object_counter)
counter, text = 10, '10'.rjust(3)
timeBoard = TimeBoard(counter, text)

create_artefacts()


#screen.fill((255,255,0))
#pygame.display.update()
# create player
gun = Gun(int(screen_width / 2), screen_height - 100, 3)
gun_group.add(gun)

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

pygame.time.set_timer(pygame.USEREVENT, 1000)
counter, text = 30, '30'.rjust(3)
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
        #if len(duck_group) == 0:
        #    create_artefacts()

        if len(duck_group) == 0 and len(rabbit_group) == 0 and len(scorebox5_group) == 0  and len(scorebox10_group)==0 and len(owl_group) ==0 and len(rabbit_group) == 0:
            game_over = 1

        if game_over == 0:
            # update spaceship
            game_over = gun.update()

            # update sprite groups
            bullet_group.update(scoreBoard)
            alien_group.update()
            alien_bullet_group.update( )

            duck_group.update()
            rabbit_group.update()
            scorebox5_group.update()
            scorebox10_group.update()
            owl_group.update()

            if ammo_tracker.get_fire_button_press():
                #screen.blit(top_bluebg, (0, screen_height - 110))
                print("ammo tracker remove" + str (ammo_tracker.get_ammo_count()))
                ammo_group.update(False)
                create_ammo(ammo_tracker.get_ammo_count(), "emptyammo")
            if ammo_tracker.get_ammo_count()<=0:
                game_over=2

        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2-150))
                time.sleep(3)
                run = False
            if game_over == 1:
                draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 - 150))
                time.sleep(3)
                run = False
            if game_over == 2:
                draw_text('OUT OF AMMO!', font40, white, int(screen_width / 2 - 150), int(screen_height / 2- 150))
                time.sleep(3)
                run = False
            if game_over == 3:
                draw_text('OUT OF TIME!', font40, white, int(screen_width / 2 - 150), int(screen_height / 2- 150))
                time.sleep(3)
                run = False

    if countdown > 0:
        draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 - 150))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 - 125))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    # update explosion group
    explosion_group.update()

    # draw sprite groups
    gun_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    duck_group.draw(screen)
    rabbit_group.draw(screen)
    scorebox5_group.draw(screen)
    scorebox10_group.draw(screen)
    owl_group.draw(screen)

    ammo_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.USEREVENT:
            counter -= 1
            if counter > 0:
                text = str(counter).rjust(3)
            else:
                text = "0"
                game_over = 3
            timeBoard.setText(text)
            timeBoard.display_timer()
    pygame.display.update()

pygame.quit()

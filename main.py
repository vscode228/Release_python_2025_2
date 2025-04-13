import random
import pygame
import sys

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('space.ogg')
pygame.mixer.music.play(-1, 0.0)
fire_sound = pygame.mixer.Sound('fire.ogg')
explosion_sound = pygame.mixer.Sound('8-bit-explosion_F.wav')

screen = pygame.display.set_mode((700, 500))
pygame.display.set_caption("SPACE_SHOOTER")

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

img_back = "galaxy.jpg"
img_hero = "rocket.png"
img_bullet = "bullet.png"
img_enemy = "ufo.png"
img_explosion = "explosion.png"
img_meteor = "asteroid.png" 

background = pygame.image.load(img_back)
hero_img = pygame.image.load(img_hero)
bullet_img = pygame.image.load(img_bullet)
enemy_img = pygame.image.load(img_enemy)
explosion_img = pygame.image.load(img_explosion)
meteor_img = pygame.image.load(img_meteor)

background = pygame.transform.scale(background, (700, 500))
hero_img = pygame.transform.scale(hero_img, (50, 50))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))
explosion_img = pygame.transform.scale(explosion_img, (30, 30))
meteor_img = pygame.transform.scale(meteor_img, (40, 40))

clock = pygame.time.Clock()

def main_menu():
    menu = True
    while menu:
        screen.blit(background, (0, 0))

        font_title = pygame.font.Font(None, 72)
        title_text = font_title.render("SPACE SHOOTER", True, WHITE)
        screen.blit(title_text, (700 // 2 - title_text.get_width() // 2, 150))

        button_rect = pygame.Rect(0, 0, 200, 60)
        button_rect.center = (700 // 2, 350)
        pygame.draw.rect(screen, GREEN, button_rect)
        font_button = pygame.font.Font(None, 36)
        button_text = font_button.render("START", True, WHITE)
        screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                                    button_rect.centery - button_text.get_height() // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    menu = False
        pygame.display.flip()
        clock.tick(60)

main_menu()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = hero_img
        self.rect = self.image.get_rect(center=(700 // 2, 500 - 50))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < 700:
            self.rect.x += 5

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(20, 700 - 20), 0))
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 500:
            self.kill()
            global missed_enemies
            missed_enemies += 1

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = meteor_img.copy()
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=(random.randint(20, 700 - 20), 0))
        self.speed = random.randint(4, 7)
        self.angle = 0
        self.rotation_speed = random.randint(-3, 3)

    def update(self):
        self.rect.y += self.speed
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.top > 500:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 7
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = explosion_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.kill()

player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

enemies = pygame.sprite.Group()
meteors = pygame.sprite.Group() 
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

running = True
score = 0
missed_enemies = 0

while running:
    clock.tick(60)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            new_bullet = Bullet(player.rect.centerx, player.rect.top)
            all_sprites.add(new_bullet)
            bullets.add(new_bullet)
            fire_sound.play()

    if random.randint(1, 40) == 1:
        new_enemy = Enemy()
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)

    if random.randint(1, 80) == 1:
        new_meteor = Meteor()
        all_sprites.add(new_meteor)
        meteors.add(new_meteor)

    all_sprites.update()

    for bullet in bullets:
        enemy_hits = pygame.sprite.spritecollide(bullet, enemies, True)
        if enemy_hits:
            bullet.kill()
            score += 1
            explosion_sound.play()
            exp = Explosion(enemy_hits[0].rect.centerx, enemy_hits[0].rect.centery)
            all_sprites.add(exp)
            explosions.add(exp)
            continue
        meteor_hits = pygame.sprite.spritecollide(bullet, meteors, True)
        if meteor_hits:
            bullet.kill()
            explosion_sound.play()
            exp = Explosion(meteor_hits[0].rect.centerx, meteor_hits[0].rect.centery)
            all_sprites.add(exp)
            explosions.add(exp)

    all_sprites.draw(screen)

    font = pygame.font.Font(None, 36)
    text = font.render(f"Рахунок: {score} | Пропущено: {missed_enemies}", True, WHITE)
    screen.blit(text, (10, 10))

    if score >= 30:
        win_text = font.render("ВИГРАВ!", True, GREEN)
        screen.blit(win_text, (700 // 2 - 50, 500 // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        running = False
    if missed_enemies >= 5:
        lose_text = font.render("ПРОГРАВ!", True, RED)
        screen.blit(lose_text, (700 // 2 - 50, 500 // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        running = False

    pygame.display.flip()

pygame.quit()

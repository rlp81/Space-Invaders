import random
import time
import pygame
import json
from pygame.display import update
#made by coal
from pygame.event import get
pygame.font.init()
assets = "assets"
WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
RED_SPACE_SHIP = pygame.image.load(".\\assets\\pixel_ship_red_small.png")
GREEN_SPACE_SHIP = pygame.image.load(".\\assets\\pixel_ship_green_small.png")
BLUE_SPACE_SHIP = pygame.image.load(".\\assets\\pixel_ship_blue_small.png")
YELLOW_SPACE_SHIP = pygame.image.load(".\\assets\\pixel_ship_yellow.png")
RED_LASER = pygame.image.load(".\\assets\\pixel_laser_red.png")
GREEN_LASER = pygame.image.load(".\\assets\\pixel_laser_green.png")
BLUE_LASER = pygame.image.load(".\\assets\\pixel_laser_blue.png")
YELLOW_LASER = pygame.image.load(".\\assets\\pixel_laser_yellow.png")
back = pygame.image.load(".\\assets\\background-black.png")
BG = pygame.transform.scale(back, (WIDTH, HEIGHT))
pygame.display.set_icon(YELLOW_SPACE_SHIP)
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.score = 0

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100, score=0):
        self.x = x
        self.y = y
        self.health = health
        self.score = score
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100, score = 0):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = score

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.score += 10
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = .5


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(350, 560)

    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))
        hscore_label = main_font.render(f"HighScore: {highscore}", 1, (255,255,255))

        WIN.blit(hscore_label, (10, 20))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 20))
        WIN.blit(score_label, (10, 60))
        WIN.blit(lives_label, (WIDTH - level_label.get_width() - 10, 60))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255,255,255))
            lost_label1 = lost_font.render("Push space to try again", 1, (255,255,255))
            lost_label2 = lost_font.render("Push ESCAPE to quit", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
            WIN.blit(lost_label1, (WIDTH/2 - lost_label1.get_width()/2, 350))
            WIN.blit(lost_label2, (WIDTH/2 - lost_label2.get_width()/2, 400))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        main()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()


        pygame.display.update()

    while run is True:
        with open(f".\\{assets}\\highscore.score", "r") as f:
            hscore = f.read()
        with open(".\\assets\\control.json") as f:
            controls = json.load(f)
        cup = pygame.key.key_code(controls["up"])
        cdown = pygame.key.key_code(controls["down"])
        cleft = pygame.key.key_code(controls["left"])
        cright = pygame.key.key_code(controls["right"])
        cshoot = pygame.key.key_code(controls["shoot"])
        cquit = pygame.key.key_code(controls["quit"])
        cmenu = pygame.key.key_code(controls["menu"])
        
        highscore = hscore
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0:
            lost = True
            lost_count += 1
        if player.health <= 0:
            lives -= 1
            player.health = 100
        if lost:
            score = str(player.score)
            if int(highscore) < player.score:
                with open(f".\\{assets}\\highscore.score", "w") as f:
                    f.write(score)
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            if not level == 0:
                player.score += 100
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[cleft] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[cright] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[cup] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[cdown] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[cshoot]:
            player.shoot()
        if keys[cmenu]:
            score = str(player.score)
            if int(highscore) < player.score:
                with open(f".\\{assets}\\highscore.score", "w") as f:
                    f.write(score)
            run = False
            main_menu()
        if keys[cquit]:
            score = str(player.score)
            if int(highscore) < player.score:
                with open(f".\\{assets}\\highscore.score", "w") as f:
                    f.write(score)
            pygame.quit()
            quit()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot()
            if event.type == pygame.QUIT:
                run = False
                time.sleep(2)

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                player.score += 10
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

    pygame.quit()
def get_key():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = event.key
                if not key == None:
                    run = False
                    return key
def control():
    title_font = pygame.font.SysFont("Arial", 30)
    run = True
    while run:
        with open(".\\assets\\control.json", "r") as f:
            controls = json.load(f)
        WIN.blit(BG, (0,0))
        up = title_font.render(f"Up: {controls['up']}", 1, (0,0,0))
        down = title_font.render(f"Down: {controls['down']}", 1, (0,0,0))
        left = title_font.render(f"Left: {controls['left']}", 1, (0,0,0))
        right = title_font.render(f"Right: {controls['right']}", 1, (0,0,0))
        shoot = title_font.render(f"Shoot: {controls['shoot']}", 1, (0,0,0))
        quit = title_font.render(f"Quit: {controls['quit']}", 1, (0,0,0))
        menu = title_font.render(f"Menu: {controls['menu']}", 1, (0,0,0))
        back = title_font.render("Back", 1, (0,0,0))
        lcontrols = [up, down, left, right, shoot, quit, menu]
        yv = 0
        for con in lcontrols:
            if con == up:
                upb = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], upb)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
            if con == down:
                downb = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], downb)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
            if con == left:
                leftb = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], leftb)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
            if con == right:
                rightb = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], rightb)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
            if con == shoot:
                shootb = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], shootb)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
            if con == quit:
                quitb = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], quitb)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
            if con == menu:
                menub = pygame.Rect(WIDTH/2 - con.get_width()/2-20, 30+yv, 20, 35)
                pygame.draw.rect(WIN, [255, 255, 255], menub)
                WIN.blit(con, (WIDTH/2 - con.get_width()/2, 30+yv))
                yv += 40
        button = pygame.Rect(260, 500, 290, 50)
        pygame.draw.rect(WIN, [255, 255, 255], button)
        WIN.blit(back, (WIDTH/2 - back.get_width()/2, 507))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button.collidepoint(mouse_pos):
                    run = False
                    cmenu()
                if upb.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["up"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                if downb.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["down"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                if leftb.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["left"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                if rightb.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["right"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                if shootb.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["shoot"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                if quitb.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["quit"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                if menub.collidepoint(mouse_pos):
                    key = get_key()
                    name = pygame.key.name(key)
                    controls["menu"] = name
                    with open(".\\assets\\control.json", "w") as f:
                        json.dump(controls,f)
                
                    
def cmenu():
    title_font = pygame.font.SysFont("comicsans", 30)
    back_font = pygame.font.SysFont("Arial", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label2 = title_font.render("Game Controls", 1, (255,255,255))
        title_label = title_font.render("WASD & Arrow keys to move, escape to quit, and MB1 to shoot.", 1, (255,255,255))
        title_label1 = title_font.render("M to go back to menu", 1, (255,255,255))
        menu_label = back_font.render("Back", 1, (0,0,0))
        control_label = back_font.render("Edit_Controls", 1, (0,0,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WIN.blit(title_label2, (WIDTH/2 - title_label2.get_width()/2, 320))
        WIN.blit(title_label1, (WIDTH/2 - title_label1.get_width()/2, 370))
        button = pygame.Rect(260, 500, 290, 50)
        button1 = pygame.Rect(260, 607, 290, 50)
        pygame.draw.rect(WIN, [255, 255, 255], button)
        pygame.draw.rect(WIN, [255, 255, 255], button1)
        WIN.blit(menu_label, (WIDTH/2 - menu_label.get_width()/2, 507))
        WIN.blit(control_label, (WIDTH/2 - control_label.get_width()/2, 615))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button.collidepoint(mouse_pos):
                    run = False
                    main_menu()
                if button1.collidepoint(mouse_pos):
                    run = False
                    control()
    pygame.quit()

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    menu_font = pygame.font.SysFont("Arial", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Space Invaders But Python", 1, (0,0,255))
        title_label1 = title_font.render("By Coal", 1, (255,255,0))
        play_label = title_font.render("Play", 1, (0,0,0))
        menu_label = menu_font.render("Controls", 1, (0,0,0))
        button = pygame.Rect(260, 500, 290, 50)
        button1 = pygame.Rect(260, 350, 280, 50)
        pygame.draw.rect(WIN, [255, 255, 255], button)
        pygame.draw.rect(WIN, [255, 255, 255], button1)
        WIN.blit(title_label1, (WIDTH/2 - title_label1.get_width()/2, 210))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 150))
        WIN.blit(menu_label, (WIDTH/2 - menu_label.get_width()/2, 507))
        WIN.blit(play_label, (WIDTH/2 - play_label.get_width()/2, 350))
        WIN.blit(YELLOW_SPACE_SHIP, (WIDTH/2 - play_label.get_width()/2, 50))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button.collidepoint(mouse_pos):
                    run = False
                    cmenu()
                if button1.collidepoint(mouse_pos):
                    run = False
                    main()


    pygame.quit()


main_menu()

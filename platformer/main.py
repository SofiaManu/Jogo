import random
import math
from pygame import Rect
import pgzrun

WIDTH = 600
HEIGHT = 600

game_state = "menu"
music_on = True
score = 0

ground_blocks = []
ground_block_width = 64
ground_block_height = 64
ground_start_x = 0
ground_end_x = 1650

for x in range(ground_start_x, ground_end_x, ground_block_width):
    ground_blocks.append(Actor("block_green", (x + ground_block_width // 2, 350 + ground_block_height // 2)))

platforms = [
    Actor("block_blue", (300, 280)),
    Actor("block_blue", (500, 200)),
    Actor("block_blue", (750, 320)),
    Actor("block_blue", (900, 260)),
    Actor("block_blue", (1100, 220)),
    Actor("block_blue", (1300, 280)),
    Actor("block_blue", (1500, 250)),
]

coins = []
for plat in platforms:
    coin = Actor("coin_gold", (plat.x, plat.y - 40))
    coins.append(coin)

goal = Actor("flag_red_a", (1600, 300))

hero = Actor("character_beige_front", (100, 300))
hero.vy = 0
on_ground = True
hero.frame_idle = ["character_beige_front"]
hero.frame_walk = ["character_beige_walk_a"]
hero.frame_hit = ["character_beige_hit"]
hero.anim_counter = 0

camera_offset_x = 0

class Bee:
    def __init__(self, x, y):
        self.actor = Actor("bee_rest", (x, y))
        self.frames = ["bee_a", "bee_b"]
        self.frame_index = 0

    def update(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.actor.image = self.frames[self.frame_index]
        self.actor.x += 1.5
        if self.actor.x - camera_offset_x > WIDTH + 50:
            self.actor.x = camera_offset_x - 50
        self.actor.y = ground.top - 50

    def draw(self):
        x_on_screen = self.actor.x - camera_offset_x
        screen.blit(self.actor.image, (x_on_screen, self.actor.y))

bees = [Bee(600, 300), Bee(400, 300)]
ground = Rect(0, 350, ground_end_x, ground_block_height)

menu_buttons = {
    "start": (200, 180),
    "music": (200, 240),
    "exit": (200, 300),
}

goal_reached = False

def draw():
    screen.clear()
    screen.blit("fundo", (0, 0))

    if game_state == "menu":
        draw_menu()
    elif game_state == "play":
        draw_game()
        screen.draw.text(f"Score: {score}", topleft=(10, 10), fontsize=40, color="yellow")
    elif game_state == "gameover":
        draw_game()
        screen.draw.text("YOU WON!" if goal_reached else "GAME OVER",
                         center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60,
                         color="green" if goal_reached else "red")
        if goal_reached:
            screen.draw.text("Back to Menu", center=(WIDTH // 2, HEIGHT // 2 + 20),
                             fontsize=40, color="blue")
        else:
            screen.draw.text("Click to restart", center=(WIDTH // 2, HEIGHT // 2 + 20),
                             fontsize=40, color="black")

def draw_menu():
    screen.draw.text("PLATFORMER GAME", center=(WIDTH // 2, 100), fontsize=60, color=(0, 0, 0))
    screen.draw.text("Start", topleft=menu_buttons["start"], fontsize=40, color=(0, 0, 0))
    screen.draw.text(f"Music: {'ON' if music_on else 'OFF'}", topleft=menu_buttons["music"], fontsize=40, color=(0, 0, 0))
    screen.draw.text("Exit", topleft=menu_buttons["exit"], fontsize=40, color=(0, 0, 0))

def draw_game():
    for block in ground_blocks:
        block_x_on_screen = block.x - camera_offset_x
        screen.blit(block.image, (block_x_on_screen, block.y))

    for plat in platforms:
        plat_x_on_screen = plat.x - camera_offset_x
        screen.blit(plat.image, (plat_x_on_screen, plat.y))

    for coin in coins:
        coin_x = coin.x - camera_offset_x
        screen.blit(coin.image, (coin_x, coin.y))

    hero_screen_x = hero.x - camera_offset_x
    screen.blit(hero.image, (hero_screen_x, hero.y))

    for bee in bees:
        bee.draw()

    goal_screen_x = goal.x - camera_offset_x
    screen.blit(goal.image, (goal_screen_x, goal.y))

def update():
    if game_state == "play":
        update_hero()
        for bee in bees:
            bee.update()
        check_collisions()
        check_goal()
        check_coins()

def update_hero():
    global on_ground, camera_offset_x

    if keyboard.left:
        hero.x -= 4
    if keyboard.right:
        hero.x += 4

    camera_offset_x = hero.x - WIDTH // 2

    if keyboard.up and on_ground:
        hero.vy = -10
        on_ground = False

    hero.vy += 0.5
    hero.y += hero.vy

    hero_rect = Rect(hero.x - hero.width // 2, hero.y - hero.height // 2, hero.width, hero.height)

    if hero.y + hero.height // 2 >= ground.top:
        hero.y = ground.top - hero.height // 2
        hero.vy = 0
        on_ground = True
    else:
        on_ground = False
        for plat in platforms:
            plat_rect = Rect(plat.x - plat.width // 2, plat.y - plat.height // 2, plat.width, plat.height)
            if hero.vy >= 0 and hero_rect.colliderect(plat_rect) and (hero.y + hero.height // 2) <= plat_rect.top + 10:
                hero.y = plat_rect.top - hero.height // 2
                hero.vy = 0
                on_ground = True
                break

    hero.anim_counter = (hero.anim_counter + 1) % 20
    hero.image = hero.frame_idle[0] if hero.anim_counter < 10 else hero.frame_walk[0]

def check_collisions():
    global game_state, goal_reached
    for bee in bees:
        if hero.colliderect(bee.actor):
            game_state = "gameover"
            goal_reached = False

def check_goal():
    global game_state, goal_reached
    hero_rect = Rect(hero.x, hero.y, hero.width, hero.height)
    goal_rect = Rect(goal.x - goal.width // 2, goal.y - goal.height // 2, goal.width, goal.height)
    if hero_rect.colliderect(goal_rect):
        game_state = "gameover"
        goal_reached = True

def check_coins():
    global score
    for coin in coins[:]:
        if hero.colliderect(coin):
            coins.remove(coin)
            score += 1
            try:
                sounds.sfx_coin.play()
            except:
                print("⚠️ Som 'coin.mp3' não encontrado.")

def restart_game():
    global game_state, camera_offset_x, on_ground, goal_reached, score

    hero.x = 100
    hero.y = 300
    hero.vy = 0
    on_ground = True
    camera_offset_x = 0
    goal_reached = False
    score = 0

    bees.clear()
    bees.append(Bee(600, 300))
    bees.append(Bee(400, 300))

    # Reiniciar moedas
    coins.clear()
    for plat in platforms:
        coin = Actor("coin_gold", (plat.x, plat.y - 40))
        coins.append(coin)

    game_state = "play"

    if music_on:
        try:
            music.play("temasom")
            music.set_volume(0.5)
        except:
            print("⚠️ Música 'temasom' não encontrada.")

def go_to_menu():
    global game_state, goal_reached, camera_offset_x, on_ground
    game_state = "menu"
    goal_reached = False
    hero.x = 100
    hero.y = 300
    hero.vy = 0
    camera_offset_x = 0
    on_ground = True
    music.stop()

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        if Rect(menu_buttons["start"], (200, 40)).collidepoint(pos):
            restart_game()
        elif Rect(menu_buttons["music"], (200, 40)).collidepoint(pos):
            music_on = not music_on
            if not music_on:
                music.stop()
        elif Rect(menu_buttons["exit"], (200, 40)).collidepoint(pos):
            exit()
    elif game_state == "gameover":
        if goal_reached:
            menu_button_rect = Rect((WIDTH // 2 - 100, HEIGHT // 2 + 10), (200, 40))
            if menu_button_rect.collidepoint(pos):
                go_to_menu()
        else:
            restart_game()

pgzrun.go()

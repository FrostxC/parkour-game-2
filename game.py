import sys
import math
import random
import time

import pygame
from pygame import mixer
mixer.init()

from scripts.utilis import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
pygame.font.init()

from tkinter import *
from tkinter import simpledialog, messagebox

font = pygame.font.Font("data/Ubuntu-Italic.ttf", 31)
font2 = pygame.font.Font("data/Ubuntu-Italic.ttf", 50)
font_small = pygame.font.Font("data/Ubuntu-Italic.ttf", 16)  # Add smaller font for boxes

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)

def create_transparent_surface(width, height, alpha=128):
    """Create a transparent surface with given dimensions and alpha value"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, alpha))  # Black with alpha transparency
    return surface

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def generate_advanced_math_question():
    """Generate a secondary school level math question"""
    question_type = random.randint(1, 4)
    
    if question_type == 1:
        # Quadratic equation
        a = random.randint(1, 5)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        x = random.randint(-5, 5)
        answer = a*x*x + b*x + c
        question = f"If f(x) = {a}x² + {b}x + {c}, what is f({x})?"
    
    elif question_type == 2:
        # Trigonometry
        angle = random.choice([30, 45, 60])
        func = random.choice(['sin', 'cos'])
        if func == 'sin':
            answer = round(math.sin(angle * math.pi / 180), 2)
        else:
            answer = round(math.cos(angle * math.pi / 180), 2)
        question = f"What is {func}({angle}°)? (round to 2 decimal places)"
    
    elif question_type == 3:
        # Square root
        num = random.randint(1, 10)
        answer = round(math.sqrt(num), 2)
        question = f"What is √{num}? (round to 2 decimal places)"
    
    else:
        # Basic algebra
        x = random.randint(1, 10)
        y = random.randint(1, 10)
        answer = x * y + x + y
        question = f"If x = {x} and y = {y}, what is xy + x + y?"
    
    return question, answer

def show_math_question():
    """Show math question dialog and return True if answered correctly"""
    question, correct_answer = generate_advanced_math_question()
    
    root = Tk()
    root.withdraw()
    
    user_answer = simpledialog.askstring("Math Question", 
                                       question + "\nAnswer correctly to continue playing!")
    
    try:
        user_answer = float(user_answer)
        is_correct = abs(user_answer - correct_answer) < 0.1  # Allow small rounding differences
    except (ValueError, TypeError):
        is_correct = False
    
    root.destroy()
    return is_correct

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.load_level(0)
        
        # Timer initialization
        self.start_time = time.time()
        self.time_limit = 10  # 1 minute in seconds
        
        self.lives = 2  # Initialize with 2 lives
        self.questions_asked = 0
        self.questions_correct = 0
        self.points = 0
        
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        self.scroll = [0, 0]
        self.dead = 0
        
    def show_game_over_screen(self):
        """Display the game over screen with statistics"""
        overlay = create_transparent_surface(self.display.get_width(), self.display.get_height(), 180)
        self.display.blit(overlay, (0, 0))
        
        # Game Over text
        draw_text("GAME OVER!", font2, (255, 0, 0), self.display, 
                 self.display.get_width()//2 - 100, 50)
        
        # Statistics
        stats_y = 120
        spacing = 40
        draw_text(f"Final Score: {self.points}", font, WHITE, self.display, 
                 self.display.get_width()//2 - 80, stats_y)
        draw_text(f"Questions: {self.questions_correct}/{self.questions_asked}", font, WHITE, self.display, 
                 self.display.get_width()//2 - 80, stats_y + spacing)
        
        # Press any key message
        draw_text("Game closing in 3 seconds...", font, (150, 150, 150), self.display,
                 self.display.get_width()//2 - 100, stats_y + spacing * 3)
        
        pygame.display.update()
        
        # Wait 3 seconds then close
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()
    
    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            
            # Make boxes one-third smaller
            box_width = int(80 * (2/3))  # Reduced from 80 to about 53
            box_height = int(30 * (2/3))  # Reduced from 30 to about 20
            box_spacing = 2
            box_x = 5  # Position from left edge
            timer_box_y = 5
            points_box_y = timer_box_y + box_height + box_spacing
            lives_box_y = points_box_y + box_height + box_spacing
            
            # Calculate floating animation
            float_offset = math.sin(time.time() * 1.5) * 1
            
            # Create transparent surfaces for smaller boxes
            timer_surface = create_transparent_surface(box_width, box_height, 100)
            points_surface = create_transparent_surface(box_width, box_height, 100)
            lives_surface = create_transparent_surface(box_width, box_height, 100)
            
            # Subtle border for smaller boxes
            border_color = (255, 255, 255, 20)
            pygame.draw.rect(timer_surface, border_color, (0, 0, box_width, box_height), 1)
            pygame.draw.rect(points_surface, border_color, (0, 0, box_width, box_height), 1)
            pygame.draw.rect(lives_surface, border_color, (0, 0, box_width, box_height), 1)
            
            # Timer logic and text
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.time_limit - int(elapsed_time))
            timer_text = f"{remaining_time}s"
            text_width, text_height = font_small.size(timer_text)
            text_x = (box_width - text_width) // 2
            text_y = (box_height - text_height) // 2
            draw_text(timer_text, font_small, WHITE, timer_surface, text_x, text_y)
            
            # Points text
            points_text = f"{self.points}"
            text_width, text_height = font_small.size(points_text)
            text_x = (box_width - text_width) // 2
            text_y = (box_height - text_height) // 2
            draw_text(points_text, font_small, WHITE, points_surface, text_x, text_y)
            
            # Lives text
            lives_text = f"Lives: {self.lives}"
            text_width, text_height = font_small.size(lives_text)
            text_x = (box_width - text_width) // 2
            text_y = (box_height - text_height) // 2
            draw_text(lives_text, font_small, WHITE, lives_surface, text_x, text_y)
            
            # Blit all surfaces with the float offset
            self.display.blit(timer_surface, (box_x, timer_box_y + float_offset))
            self.display.blit(points_surface, (box_x, points_box_y + float_offset))
            self.display.blit(lives_surface, (box_x, lives_box_y + float_offset))
            
            if remaining_time <= 0:
                pygame.display.update()
                self.questions_asked += 1
                if show_math_question():
                    self.start_time = time.time()
                    self.questions_correct += 1
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.show_game_over_screen()
                        return
                    else:
                        self.start_time = time.time()  # Reset timer and continue
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
                    self.points += 100  # Add 100 points for killing an enemy
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)
            
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.lives -= 1
                        if self.lives <= 0:
                            self.show_game_over_screen()
                            return
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, 
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5, 
                                                                 math.sin(angle + math.pi) * speed * 0.5], 
                                                        frame=random.randint(0, 7)))
            
            if self.player.rect().top > self.display.get_height():  # Player fell off map
                self.lives -= 1
                if self.lives <= 0:
                    self.show_game_over_screen()
                    return
                else:
                    self.load_level(0)  # Restart current level
            
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


background = pygame.image.load("data/images/background.png")
music_button = pygame.image.load("data/images/mutebutton.jpg")
width = 640
height = 480
background = pygame.transform.scale(background,(width, height))
music_button = pygame.transform.scale(music_button,(100, 50))

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("menu")
clock = pygame.time.Clock()

Music = True
if Music == True :
    mixer.music.load("data/music.wav")
    mixer.music.play()

def Leaderboard():
    running = True
    # Example leaderboard data: List of tuples (name, score)
    leaderboard_data = [("Player1", 100), ("Player2", 90), ("Player3", 80), ("Player4", 80), ("Player5", 80), ("Player6", 80), ("Player7", 80)]

    while running:
        screen.blit(background, (0, 0))
       
        # Draw the leaderboard header
        draw_text("Leaderboard", font, (0, 255, 255), screen, 20, 20)
        draw_text("Name", font, (0, 0, 0), screen, 50, 60)
        draw_text("Score", font, (0, 0, 0), screen, 400, 60)
        pygame.draw.line(screen, (0, 0, 0), (50, 90), (750, 90), 2)

        # Dynamic row rendering
        y_offset = 100  # Starting Y position for rows
        for idx, (name, score) in enumerate(leaderboard_data):
            # Alternate row colors for better readability
            row_color = (200, 200, 200) if idx % 2 == 0 else (240, 240, 240)
            pygame.draw.rect(screen, row_color, (50, y_offset, 540, 40))  # Full row background
            pygame.draw.line(screen, (0, 0, 0), (50, y_offset + 40), (590, y_offset + 40), 1)  # Row divider
           
            # Render name and score
            draw_text(name, font, (0, 0, 0), screen, 50, y_offset + 10)
            draw_text(str(score), font, (0, 0, 0), screen, 400, y_offset + 10)
           
            # Increment Y offset for the next row
            y_offset += 50

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.update()
        clock.tick(60)        

blue =(0,255,255)

def main_menu():
    global click  # Declare click as global
    click = False  # Initialize click here
    running = True
    while running:
        screen.blit(background,(0,0))
        screen.blit(music_button,(500,25))
        draw_text("Parkour Game", font2, (0, 255, 255), screen, 150, 100)

        pos = pygame.mouse.get_pos()
        BORDERWIDTH = 3

        button1 = pygame.Rect(200,300, 200,50) #game button
        button2 = pygame.Rect(206,400, 200,50) #leaderboard button 
        button3 = pygame.Rect(500,25, 100,50) #music button 
        
        pygame.draw.rect(screen,BLACK,button1,BORDERWIDTH)
        pygame.draw.rect(screen,BLACK,button2,BORDERWIDTH)
        pygame.draw.rect(screen,BLACK,button3,BORDERWIDTH)
        screen.blit(music_button,(500,25))

        if button1.collidepoint(pos):
            pygame.draw.rect(screen,blue,button1)
            if click:
                Game().run()

        if button2.collidepoint(pos):
            pygame.draw.rect(screen,blue,button2)
            if click:
                Leaderboard()

        if button3.collidepoint(pos):
            if click:
                mixer.music.set_volume(0)

        draw_text("start now",font,(0,0,0),screen,220,300)
        draw_text("Leaderboard",font,(0,0,0),screen,220,400)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60)


main_menu()    
import pygame 
from game import Game
import pygame.locals as pl

pygame.init()

pygame.font.init()

screen_width = 500
screen_height = 400

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (200,200,200)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Log-in Page")

font = pygame.font.Font(None,32)
input_box_width = 200
input_box_height= 40

username_box = pygame.Rect(150,100,input_box_width,input_box_height)

password_box = pygame.Rect(150,100,input_box_width,input_box_height)

username =""
password = ""

user_active = False
pass_active = False

valid_username = "george"
valid_password =" 123"

def draw_textbox(text, rect, active):
    colour = GRAY if active else BLACK 
    pygame.draw.rect(screen,colour,rect,2)
    text_surface = font.render(text,True, BLACK)
    screen.blit(text_surface, (rect.x+5, rect.y+5))
    pygame.draw.rect(screen, BLACK, rect,2)

running = True
login_successful = False
while running :
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type== pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if username_box.collidepoint(event.pos):
                user_active = True
                pass_active = False

            elif password_box.collidepoint(event.pos):
                user_active = False
                pass_active = True

            else:
                user_active = False
                pass_active = False
        
        if event.type == pygame.KEYDOWN:
            if user_active:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

            if pass_active:
                if event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode
            
            if event.key == pygame.K_RETURN:
                if username == valid_username and password == valid_password:
                    print("LOG-IN Successful")
                    running = False
                    login_successful = True

                else:
                    print("INVALID LOG-IN")
    
    draw_textbox(username,username_box,user_active)
    draw_textbox("+"*len(password),password_box,pass_active)

    user_label = font.render("username:",True, BLACK)
    pass_label = font.render("password:",True, BLACK)

    screen.blit(user_label,(50,100))
    screen.blit(pass_label,(50,200))

    pygame.display.flip()

pygame.quit()


if login_successful:
    Game().run()




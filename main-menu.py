import sys
import pygame 

background = pygame.image.load("data/images/background.png")
width = 640
height = 480
background = pygame.transform.scale(background,(width, height))

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("menu")
clock = pygame.time.Clock()

click = False
def main_menu():
    running = True
    while running:
        screen.blit(background,(0,0))
        pos= pygame.mouse.get_pos()
        button1 =pygame.Rect(425,300, 200,50) #leadboard button 
        if button1.collidepoint((pos)):
            if click:
                leaderboard()

        pygame.draw.rect(screen,(0,0,255),button1)
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 :
                    click = True

        pygame.display.update()
        clock.tick(60)


main_menu()
        
import sys

import pygame

from scripts.utilis import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0  

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
        }
        
        self.movement = [False, False, False, False]
        
        self.tilemap = Tilemap(self, tile_size=16)

        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass



        

        self.scroll = [0, 0]  #  makes you scroll the tiles
        
        self.tile_list = list(self.assets)
        self.tile_group = 0  # which group are you using (grass or stone or decor)
        self.tile_variant = 0  #whch tile in that group are you using

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True
        
        
    def run(self):
        while True:
            self.display.fill((0, 0, 0))    # background is black

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2 #it helps move the camera
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.tilemap.render(self.display, offset=render_scroll)

            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy() # shows the current tile while scolling 

            current_tile_img.set_alpha(100)
            
            mousepos = pygame.mouse.get_pos() # it will give the mouse position 
            mousepos = (mousepos[0] / RENDER_SCALE, mousepos[1] / RENDER_SCALE) # ist scalse down the mouse position 

            #this will give the mouse position in terms of tile coordinate
            tile_pos = (int((mousepos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mousepos[1] + self.scroll[1]) // self.tilemap.tile_size))
            
            #you can hover on the screen and see where the tile you can you putting
            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mousepos)


            
            if self.clicking and self.ongrid:
                #coverting string selection onto the actual tile groups
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}

            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]  # it deletes the tile where the mouse it shovering on 

                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mousepos):
                        self.tilemap.offgrid_tiles.remove(tile)
            
            self.display.blit(current_tile_img, (5, 5))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mousepos[0] + self.scroll[0], mousepos[1] + self.scroll[1])})

                    if event.button == 3:
                        self.right_clicking = True

                    if self.shift:
                        if event.button == 4:                  #if you pressing shift it will scroll the variant
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]]) #give no. of variants in that list 
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])

                    else:                                       #if you dont press shift it will scroll through the group
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN: 

                    if event.key == pygame.K_a:        #makes you move the camera left
                        self.movement[0] = True
                    if event.key == pygame.K_d:        #makes you move the camera right       
                        self.movement[1] = True
                    if event.key == pygame.K_w:        #makes you move the camera up
                        self.movement[2] = True
                    if event.key == pygame.K_s:        #makes you move the camera down
                        self.movement[3] = True

                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid

                    if event.key == pygame.K_t:      # if you press't' it will autotile
                        self.tilemap.autotile()

                    if event.key == pygame.K_o:     #if you 'o' it will save the map in jason format
                        self.tilemap.save('map.json')



                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
            
                        
                
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Editor().run()       

                    
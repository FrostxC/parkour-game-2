import os
import pygame

BASE_IMG_PATH ='data/images/'

def load_image(path):
    img  = pygame.image.load(BASE_IMG_PATH + path).convert()  #its converts internal representation of image in pygame and make it more effiecnt for rendering 
    img.set_colorkey((0,0,0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):# this will  sort the images in ascending order
        images.append(load_image(path + '/' + img_name))
    return images



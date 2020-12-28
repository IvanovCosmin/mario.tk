import pygame, sys
from pygame.locals import *
import random
 
pygame.init()
 
FPS = 60
FramePerSec = pygame.time.Clock()
 
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

S_WIDTH = 600
S_HEIGHT = 600
 
DISPLAYSURF = pygame.display.set_mode((S_WIDTH,S_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("The bald plumber")


# EXEMPLU
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("enemy.png")
        self.surf = pygame.Surface((50, 100))
        self.rect = self.surf.get_rect()
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()
       #if pressed_keys[K_UP]:
            #self.rect.move_ip(0, -5)
       #if pressed_keys[K_DOWN]:
            #self.rect.move_ip(0,5)
         
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
        if self.rect.right < S_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(5, 0)
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)     

P1 = Player()
         
 
while True:     
    for event in pygame.event.get():              
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    P1.update()
     
    DISPLAYSURF.fill(WHITE)
    P1.draw(DISPLAYSURF)
         
    pygame.display.update()
    print(len(pygame.display.get_surface().get_buffer().raw))
    FramePerSec.tick(FPS)
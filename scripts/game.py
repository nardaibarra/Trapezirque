import pygame
import sys
from acrobat import Acrobat
from tilemap import Tilemap
from utils import load_image, load_images
from baloons import Baloons

class Trapezirque:
    W = 640 #320 
    H = 480 #240

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("trapezirque")
        self.screen = pygame.display.set_mode((self.W,self.H))
        self.display = pygame.Surface((self.W/2, self.H/2))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.points = 0
        self.game_over = False 

        self.assets = {
            'sand': load_images('tiles/sand'),
            'acrobat': load_image('acrobat/acrobat_idle2.png'),
            'background': load_image('bg.png'),
            'game_over': load_image('game_over.png'),
            'baloons': load_images('baloons'),
        }

        self.baloons = Baloons(self.assets['baloons'], count=10)
        self.acrobat = Acrobat(self, 'acrobat', (50,50), (16,16))
        self.tilemap = Tilemap(self, tile_size=16)
        self.scroll = [0,0]
        #self.trapezes = Trapezes(self,(100,120), 80, 5)

    def run(self) -> None:
        while True:

            self.display.blit(self.assets['background'], (0,0))
            self.scroll[0] += (self.acrobat.rect().centerx - self.display.get_width() / 10 - self.scroll[0])
            #self.scroll[1] += (self.acrobat.rect().centery - self.display.get_height() / 1.1 - self.scroll[1])
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)
            self.baloons.update()
            self.baloons.render(self.display, offset=render_scroll)
            self.acrobat.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.acrobat.render(self.display, offset=render_scroll)
            # self.rod.update()
            # self.rod.draw(self.display, offset=self.scroll)
            # self.rod1.update()
            # self.rod1.draw(self.display, offset=self.scroll)

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
                        self.acrobat.velocity[1] = -3
                        
                    # if event.key == pygame.K_SPACE:
                    #     # Check for collision with the pendulum when space is pressed
                    #     if self.rod.rect().colliderect(self.acrobat.rect()):
                    #         self.rod.attach_entity(self.acrobat)
                    #     if self.rod1.rect().colliderect(self.acrobat.rect()):
                    #         self.rod1.attach_entity(self.acrobat)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    # if event.key == pygame.K_SPACE and self.rod.attached_entity:
                    #     # Detach the acrobat when space is released
                    #     self.rod.detach_entity()
                    # if event.key == pygame.K_SPACE and self.rod1.attached_entity:
                    #     # Detach the acrobat when space is released
                    #     self.rod1.detach_entity()
            if self.game_over == True:
                break
            
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)
        

Trapezirque().run()
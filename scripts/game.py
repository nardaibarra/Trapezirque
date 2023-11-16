import pygame
import sys
from acrobat import Acrobat
from tilemap import Tilemap
from utils import load_image, load_images, Animation
from balloons import Balloons
from trapezes import Trapezes

class Trapezirque:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("trapezirque")
        self.record = 0
        self.W = 640 #320 
        self.H = 480 #240
        self.screen = pygame.display.set_mode((self.W,self.H))
        self.display = pygame.Surface((self.W/2, self.H/2))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.font = pygame.font.Font(None, 20)

        self.assets = {
            'welcome': load_images('welcome'),
            'sand': load_images('tiles/floor'),
            # 'acrobat': load_image('acrobat/acrobat_idle.png'),
            'background': load_image('bg.png'),
            'game_over': load_image('game_over_2.png'),
            'baloons': load_images('balloons'),
            'acrobat/jump': Animation(load_images('acrobat/jump')),
            'acrobat/idle': Animation(load_images('acrobat/idle')),
            'acrobat/walking': Animation(load_images('acrobat/walking'))
        }
        

        self.baloons = Balloons(self,self.assets['baloons'], 16, count=15)
        self.acrobat = Acrobat(self, 'acrobat', (50,208), (16,16))
        self.tilemap = Tilemap(self, tile_size=16)
        self.scroll = [0,0]
        self.trapezes = Trapezes(self, 2)

    def reset_game(self):
        self.movement = [False, False]
        self.score = 0
        self.lives = 3 
        self.game_over = False
        self.scroll = [0, 0]
        self.acrobat.reset()  
        self.trapezes.reset()


    def run(self) -> None:
        self.game_over == False
        intro_running = True
        index = 0
        last_switch_time = pygame.time.get_ticks()

        while intro_running:
            current_time = pygame.time.get_ticks()

            if current_time - last_switch_time > 500:
                index = 1 - index  
                last_switch_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        intro_running = False

            # Display the intro image
            self.display.blit(self.assets['welcome'][index], (0, 0))

            record_text = self.font.render(f'Record: {self.record}', True, (0,0,0))
            self.display.blit(record_text, (10, 10))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

        print(self.game_over)
        while True:
           

            self.display.blit(self.assets['background'], (0,0))

            # Horizontal Scrolling (Right)
            right_edge_x = self.display.get_width() * 0.5
            if self.acrobat.rect().centerx > right_edge_x + self.scroll[0]:
                self.scroll[0] += (self.acrobat.rect().centerx - right_edge_x - self.scroll[0])

            # Horizontal Scrolling (Left)
            left_edge_x = self.display.get_width() * 0.2
            if self.acrobat.rect().centerx < left_edge_x + self.scroll[0]:
                self.scroll[0] -= (left_edge_x + self.scroll[0] - self.acrobat.rect().centerx)

            # Vertical Scrolling (Down)
            bottom_edge_y = self.display.get_height() * 0.9
            if self.acrobat.rect().centery > bottom_edge_y + self.scroll[1]:
                self.scroll[1] += (self.acrobat.rect().centery - bottom_edge_y - self.scroll[1])

            # Vertical Scrolling (Up)
            top_edge_y = self.display.get_height() * 0.2
            if self.acrobat.rect().centery < top_edge_y + self.scroll[1]:
                self.scroll[1] -= (top_edge_y + self.scroll[1] - self.acrobat.rect().centery)


            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)
            self.baloons.update()
            self.baloons.render(self.display, offset=render_scroll)
            self.acrobat.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.acrobat.render(self.display, offset=render_scroll)
            # Draw the score to the screen
            score_text = self.font.render(f'Score: {self.score}', True, (0,0,0))
            self.display.blit(score_text, (10, 10))
            self.trapezes.render(self.display, offset=self.scroll)
            self.trapezes.update()


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
                        self.acrobat.jump()
                        
                    if event.key == pygame.K_SPACE:
                        # Check for collision with the pendulum when space is pressed
                        for trapeze in self.trapezes.trapezes:
                            if trapeze.rect().colliderect(self.acrobat.rect()):
                                trapeze.attach_entity(self.acrobat)
                                self.acrobat.trapeze = trapeze
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_SPACE and self.acrobat.trapeze:
                        self.acrobat.trapeze.detach_entity()
                
            if self.game_over == True:
                self.record = max(self.record, self.score)
                break
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

        # Game Over Loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        return self.run()

            self.display.blit(self.assets['game_over'], (0,0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

        




Trapezirque().run()
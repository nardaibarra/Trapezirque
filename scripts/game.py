import random
import pygame
import sys
from entity import EntityCreator, Player, PlayerJumpDecorator, TripleJumpDecorator
from tilemap import Tilemap
from utils import load_image, load_images, play_music,  Animation
from balloons import Balloons
from trapezes import Trapeze
from pygame.locals import *
from pygame import mixer
from enum import Enum
from memento import GameMemento, GameCaretaker

class SpawnerVariant(Enum):
    
    ACROBAT = 0
    CLOWN = 1
    MONKEY = 2
    COIN = 3
    TRAPEZE = 4


class Trapezirque:        
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("trapezirque")
        
        self.record = None
        self.W = 640 #320 
        self.H = 480 #240
        self.screen = pygame.display.set_mode((self.W,self.H))
        self.display = pygame.Surface((self.W/2, self.H/2))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.score = 0
        self.game_over = False
        self.font = pygame.font.Font(None, 20)
        self.decorator = None
        mixer.init()

        self.assets = self.getAssets()
        self.creator = EntityCreator()
        
        self.acrobat : Player = self.creator.createEntity(self, self.creator.EntityType.PLAYER, (50, 208), (16,16), 'acrobat')
        self.balloons = Balloons(self,self.assets['balloons'], 16, count=10)
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')
        self.characters =[]
        self.trapezes: Trapeze = []
        self.collectables = []
        
        for spawner in self.tilemap.extract([('spawners', 0),('spawners', 1),('spawners',2),('spawners',3),('spawners',4)]):
            self.handle_spawner(spawner)       
        
        self.scroll = [0,0]

    def reset_game(self):
        self.movement = [False, False]
        self.score = 0
        self.game_over = False
        self.scroll = [0, 0]

    def run(self) -> None:
        
        self.record = caretaker.load_game().get_last_record()
        self.game_over == False
        intro_running = True
        index = 0
        last_switch_time = pygame.time.get_ticks()
        
        play_music(self, 'start')
       
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
                    if event.key == pygame.K_r:
                        memento = caretaker.load_game()
                        if memento:
                            player_x, player_y, player_score = memento.get_saved_state()
                            self.acrobat.pos[0] = player_x
                            self.acrobat.pos[1] = player_y
                            self.score = player_score
                            intro_running = False
                    if event.key == pygame.K_RETURN:
                        intro_running = False

            # Display the intro image
            self.displayIntro(index)
            
        
        while pygame.mixer.get_busy():
            pygame.time.wait(10)
        
        play_music(self, 'main')

        
        while True:
            self.display.blit(self.assets['background'], (0,0))

            # Horizontal Scrolling (Right)
            self.rightScroll()

            # Horizontal Scrolling (Left)
            self.leftScroll()

            # Vertical Scrolling (Down)
            self.downScroll()

            # Vertical Scrolling (Up)
            self.upScroll()

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            #update and Render


            self.tilemap.render(self.display, offset=render_scroll)

            for character in self.characters.copy():
                character.update(self.tilemap, (0,0))
                character.render(self.display, offset = render_scroll)
            
            for collectable in self.collectables.copy():
                collectable.update(self.tilemap, (0,0))
                collectable.render(self.display, offset = render_scroll)
            
            for trapeze in self.trapezes.copy():
                trapeze.update()
                trapeze.draw(self.display, offset = render_scroll)
            
            self.balloons.update()
            self.balloons.render(self.display, offset=render_scroll)

            self.acrobat.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.acrobat.render(self.display, offset=render_scroll)
            # Draw the score to the screen
            score_text = self.font.render(f'Score: {self.score}', True, (0,0,0))
            self.display.blit(score_text, (10, 10))
        
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
                        if self.decorator:
                            self.decorator.jump()                        
                        else:
                            self.acrobat.jump()
                            
                            
                    if event.key == pygame.K_q:
                        caretaker.save_game(self.acrobat.pos[0], self.acrobat.pos[1], self.score, self.record, False)
                        pygame.quit()
                        sys.exit()
                        
                    if event.key == pygame.K_SPACE:
                        # Check for collision with the pendulum when space is pressed
                        for trapeze in self.trapezes:
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
                caretaker.save_game(self.acrobat.pos[0], self.acrobat.pos[1], self.score, self.record, True)
                break
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)
        
        play_music(self, 'game_over')

        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        Trapezirque().run()

            self.display.blit(self.assets['game_over'], (0,0))
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)
            
    def getAssets(self):
        assets = {
                'welcome': load_images('welcome'),
                'game_over': load_image('game_over_2.png'),
                'background': load_image('bg.png'),
                'floor': load_images('tiles/floor'),
                'circus': load_images('tiles/circus'),
                'balloons': load_images('balloons'),
                'spawners': load_images('tiles/spawners'),
                'coin/idle': Animation(load_images('coin/idle'),10),
                'monkey/idle': Animation(load_images('monkey/idle'),10),
                'clown/idle': Animation(load_images('clown/idle'),10),
                'acrobat/jump': Animation(load_images('player/jump')),
                'acrobat/idle': Animation(load_images('player/idle')),
                'acrobat/walking': Animation(load_images('player/walking')),
                'music': {
                    'start': './assets/music/Trapeqzirque_start_screen.mp3',
                    'main': './assets/music/Trapeqzirque_main.mp3',
                    'game_over': './assets/music/Trapeqzirque_game_over.mp3'},
                'sounds': {
                    'collect': './assets/sounds/collect.mp3',
                    'collision':'./assets/sounds/collapse.mp3',
                    'jump':'./assets/sounds/jump.wav',
                    'balloon':'./assets/sounds/balloon.wav',
                }
                
            }
        
        return assets
    
    def handle_spawner(self, spawner):
        variant = spawner['variant']
        
        if variant == SpawnerVariant.ACROBAT.value:
            self.acrobat.pos = spawner['pos']
        elif variant ==  SpawnerVariant.CLOWN.value:
            character = self.creator.createEntity(self, self.creator.EntityType.CHARACTER, spawner['pos'], (16,16), 'clown')
            self.characters.append(character)
        elif variant == SpawnerVariant.MONKEY.value:
            character = self.creator.createEntity(self, self.creator.EntityType.CHARACTER, spawner['pos'], (16,16), 'monkey')
            self.characters.append(character)
        elif variant == SpawnerVariant.COIN.value:
            collectable = self.creator.createEntity(self, self.creator.EntityType.COLLECTABLE, spawner['pos'], (16,16), 'coin')
            self.collectables.append(collectable)
        elif variant == SpawnerVariant.TRAPEZE.value:
            self.trapezes.append(Trapeze(self, spawner['pos'], 62, 5))
            

    def displayIntro(self, index):
        self.display.blit(self.assets['welcome'][index], (0, 0))
        record_text = self.font.render(f'Record: {self.record}', True, (0,0,0))
        self.display.blit(record_text, (10, 10))
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
        pygame.display.update()
        self.clock.tick(60)
        
    def leftScroll(self):
        left_edge_x = self.display.get_width() * 0.2
        if self.acrobat.rect().centerx < left_edge_x + self.scroll[0]:
            self.scroll[0] -= (left_edge_x + self.scroll[0] - self.acrobat.rect().centerx)
        
    
    def rightScroll(self):
        right_edge_x = self.display.get_width() * 0.5
        if self.acrobat.rect().centerx > right_edge_x + self.scroll[0]:
            self.scroll[0] += (self.acrobat.rect().centerx - right_edge_x - self.scroll[0])
    
    def upScroll(self):
        top_edge_y = self.display.get_height() * 0.2
        if self.acrobat.rect().centery < top_edge_y + self.scroll[1]:
            self.scroll[1] -= (top_edge_y + self.scroll[1] - self.acrobat.rect().centery)
     
    def downScroll(self):
        bottom_edge_y = self.display.get_height() * 0.9
        if self.acrobat.rect().centery > bottom_edge_y + self.scroll[1]:
            self.scroll[1] += (self.acrobat.rect().centery - bottom_edge_y - self.scroll[1])
       
    def save_state(self,player_x, player_y, score, record):
        return GameMemento(player_x, player_y, score, record)
    
    def decorate(self):
        print("Entré a decorate")
        self.decorator = TripleJumpDecorator(self.acrobat)


game = Trapezirque()
caretaker = GameCaretaker(game)
game.run()




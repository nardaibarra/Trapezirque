import random
import pygame
import sys
from factory import EntityCreator, Player
from decorator import TripleJumpDecorator
from tilemap import Tilemap
from utils import get_assets, play_music,  Animation
from balloons import Balloons
from trapezes import Trapeze
from pygame.locals import *
from pygame import mixer
from enum import Enum
from memento import GameMemento, GameCaretaker

class Spawner(Enum):
    
    ACROBAT = 0
    CLOWN = 1
    MONKEY = 2
    COIN = 3
    TRAPEZE = 4


class Trapezirque:
    
    WIDTH = 640
    HEIGHT = 480        

    def __init__(self) -> None:
        self.initialize_libs()

        self.W = self.WIDTH
        self.H = self.HEIGHT

        #game settings attr
        self.screen = pygame.display.set_mode((self.W,self.H))
        self.display = pygame.Surface((self.W/2, self.H/2))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.score = 0
        self.game_over = False
        self.decorator = None
        mixer.init()

        self.assets = get_assets()
        self.creator = EntityCreator()
        
        self.acrobat : Player = self.creator.create_entity(self, self.creator.EntityType.PLAYER, (50, 208), (16,16), 'acrobat')
        self.balloons = Balloons(self,self.assets['balloons'], 16, count=10)
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')
        self.characters =[]
        self.trapezes: Trapeze = []
        self.collectables = []
        
        for spawner in self.tilemap.extract([('spawners', Spawner.ACROBAT.value),('spawners', Spawner.CLOWN.value),('spawners',Spawner.MONKEY.value),('spawners',Spawner.COIN.value),('spawners',Spawner.TRAPEZE.value)]):
            self.handle_spawner(spawner)       
        
        self.scroll = [0,0]

    def initialize_libs(self):
        pygame.init()
        pygame.font.init()
        mixer.init()
        pygame.display.set_caption("trapezirque")

    def handle_spawner(self, spawner):
        variant = spawner['variant']
        spawner_actions = {
            Spawner.ACROBAT.value: lambda: setattr(self.acrobat, 'pos', spawner['pos']),
            Spawner.CLOWN.value: lambda: self.spawn_entity('clown', self.creator.EntityType.CHARACTER, self.characters, spawner),
            Spawner.MONKEY.value: lambda: self.spawn_entity('monkey', self.creator.EntityType.CHARACTER, self.characters, spawner),
            Spawner.COIN.value: lambda: self.spawn_entity('coin', self.creator.EntityType.COLLECTABLE, self.collectables, spawner),
            Spawner.TRAPEZE.value: lambda: self.trapezes.append(Trapeze(self, spawner['pos'], 62, 5))
        }

        if variant in spawner_actions:
            spawner_actions[variant]()

    def spawn_entity(self, entity_type, entity_enum, entity_list, spawner):
        entity = self.creator.create_entity(self, entity_enum, spawner['pos'], (16, 16), entity_type)
        entity_list.append(entity)


    #run game
    def run(self) -> None:
        self.reset_game()
        self.run_intro()
        self.start_game()
        self.run_game_over()

    #Reset Game
    def reset_game(self):
        self.record = caretaker.load_game().get_last_record()
        self.game_over == False


    
    #run intro
    def run_intro(self):
        play_music(self, 'start')
        self.intro_running = True
        self.intro_animation_index = 0
        self.last_switch_time = pygame.time.get_ticks()

        while self.intro_running:
            self.update_intro_animation()

            for event in pygame.event.get():
              self.handle_intro_events(event)

            self.display_intro(self.intro_animation_index)
            self.update_display()

    def handle_intro_events(self, event):
        if event.type == pygame.QUIT:
            self.quit_game()
        elif event.type == pygame.KEYDOWN:
            self.handle_intro_keydown(event)


    def handle_intro_keydown(self, event):
        if event.key == pygame.K_r:
            self.load_game()
        if event.key == pygame.K_RETURN:
            self.intro_running = False

    def update_intro_animation(self):
        SWITCH_INTERVAL = 500  
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time > SWITCH_INTERVAL:
            self.intro_animation_index = 1 - self.intro_animation_index
            self.last_switch_time = current_time

    def display_intro(self, index):
        self.display.blit(self.assets['welcome'][index], (0, 0))
        self.render_intro_text()

    def render_intro_text(self):
        font = pygame.font.Font(None, 20)
        record_text = font.render(f'Record: {self.record}', True, (0,0,0))
        self.display.blit(record_text, (10, 10))
        font = pygame.font.Font(None, 15)
        load_game_text = font.render(f'Press "r" to load game', True, (0,0,0))
        self.display.blit(load_game_text, (200, 3))


    #start game
    def start_game(self):
        play_music(self, 'main')
        while True:
            self.display.blit(self.assets['background'], (0,0))
            self.handle_camera_scroll()
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)
            self.update_and_render_elements(render_scroll)
            self.render_game_text()

        
            for event in pygame.event.get(): 
                self.handle_game_events(event)

            if self.game_over:
                self.handle_gameover()
                break
            
            self.update_display()

    def handle_camera_scroll(self):
        self.rightScroll()
        self.leftScroll()
        self.downScroll()
        self.upScroll()

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

    def update_and_render_elements(self, render_scroll):
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


    def render_game_text(self):
        font = pygame.font.Font(None, 20)
        score_text = font.render(f'Score: {self.score}', True, (0,0,0))
        self.display.blit(score_text, (10, 10))
        font = pygame.font.Font(None, 15)
        save_game_text = font.render(f'"q" to save and exit', True, (0,0,0))
        self.display.blit(save_game_text, (110, 3))

    def handle_game_events(self, event):
        if event.type == pygame.QUIT:
            self.quit_game()
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        if event.type == pygame.KEYUP:
            self.handle_keyup(event)

    def decorate(self):
        self.decorator = TripleJumpDecorator(self.acrobat)

    def handle_jump(self):
        if self.decorator:
            self.decorator.jump()                        
        else:
            self.acrobat.jump()
    
    def handle_swing(self):
        for trapeze in self.trapezes:
            if trapeze.rect().colliderect(self.acrobat.rect()):
                trapeze.attach_entity(self.acrobat)
                self.acrobat.trapeze = trapeze
    
    def handle_keydown(self, event):
        if event.key == pygame.K_LEFT:
            self.movement[0] = True
        if event.key == pygame.K_RIGHT:
            self.movement[1] = True
        if event.key == pygame.K_UP:
            self.handle_jump()
        if event.key == pygame.K_q:
            caretaker.save_game(self.acrobat.pos[0], self.acrobat.pos[1], self.score, self.record, False)
            self.quit_game()
        if event.key == pygame.K_SPACE:
            self.handle_swing()

    def handle_keyup(self, event):
        if event.key == pygame.K_LEFT:
            self.movement[0] = False
        if event.key == pygame.K_RIGHT:
            self.movement[1] = False
        if event.key == pygame.K_SPACE and self.acrobat.trapeze:
            self.acrobat.trapeze.detach_entity()


    def handle_gameover(self):
        self.record = max(self.record, self.score)
        caretaker.save_game(self.acrobat.pos[0], self.acrobat.pos[1], self.score, self.record, True)


    #run game over
    def run_game_over(self):
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
            self.update_display()


    #Memento load and save
    def load_game(self):
        memento = caretaker.load_game()
        if memento:
            player_x, player_y, player_score = memento.get_saved_state()
            self.acrobat.pos[0] = player_x
            self.acrobat.pos[1] = player_y
            self.score = player_score
            self.intro_running = False

    def save_state(self,player_x, player_y, score, record):
        return GameMemento(player_x, player_y, score, record)
    

    #shared methods
    def update_display(self):
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
        pygame.display.update()
        self.clock.tick(60)

    def quit_game(self):
        pygame.quit()
        sys.exit()


#main 
game = Trapezirque()
caretaker = GameCaretaker(game)
game.run()




import random
import pygame
import sys
from factory import EntityCreator, Player
from decorator import DoubleJumpDecorator
from tilemap import Tilemap
from utils import get_assets, play_music,  Animation
from balloons import Balloons
from trapezes import Trapeze
from pygame.locals import *
from pygame import mixer
from enum import Enum
from memento import GameMemento, GameCaretaker

class Spawner(Enum):
    ''' Enum class used for entities values '''
    
    ACROBAT = 0
    CLOWN = 1
    MONKEY = 2
    COIN = 3
    TRAPEZE = 4


class Trapezirque:
    ''' Main class of the game '''
    
    WIDTH = 640
    HEIGHT = 480        

    def __init__(self) -> None:
        self.initialize_libs()

        self.W: int = self.WIDTH
        self.H: int = self.HEIGHT

        #game settings attr
        self.screen: pygame.display = pygame.display.set_mode((self.W,self.H))
        self.display: pygame.surface = pygame.Surface((self.W/2, self.H/2))
        self.clock = pygame.time.Clock()
        self.movement: list = [False, False]
        self.score: int = 0
        self.game_over: bool = False
        self.decorator: DoubleJumpDecorator = None
        mixer.init()

        self.assets: dict = get_assets()
        self.creator: EntityCreator = EntityCreator()
        
        self.acrobat : Player = self.creator.create_entity(self, self.creator.EntityType.PLAYER, (50, 208), (16,16), 'acrobat')
        self.balloons: Balloons = Balloons(self,self.assets['balloons'], 16, count=10)
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')
        self.characters: list = []
        self.trapezes: list[Trapeze] = []
        self.collectables: list[EntityCreator.EntityType.COLLECTABLE] = []
        
        for spawner in self.tilemap.extract([('spawners', Spawner.ACROBAT.value),('spawners', Spawner.CLOWN.value),('spawners',Spawner.MONKEY.value),('spawners',Spawner.COIN.value),('spawners',Spawner.TRAPEZE.value)]):
            self.handle_spawner(spawner)       
        
        self.scroll = [0,0]

    def initialize_libs(self) -> None:
        ''' Several resources initializer '''
        pygame.init()
        pygame.font.init()
        mixer.init()
        pygame.display.set_caption("trapezirque")

    def handle_spawner(self, spawner) -> None:
        ''' Encharge of managing the different kind of elements present in the game '''
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

    def spawn_entity(self, entity_type: str, entity_enum: EntityCreator.EntityType , entity_list: list, spawner) -> None:
        ''' Encharge of spawning the differnt kind of elements present in the game '''
        entity = self.creator.create_entity(self, entity_enum, spawner['pos'], (16, 16), entity_type)
        entity_list.append(entity)


    #run game
    def run(self) -> None:
        ''' Principal method that runs the entire game '''
        self.reset_game()
        self.run_intro()
        self.start_game()
        self.run_game_over()

    #Reset Game
    def reset_game(self) -> None:
        ''' Resets game by getting the max record and finishing the game'''
        self.record: int = caretaker.load_game().get_last_record()
        self.game_over: bool == False
    
    #run intro
    def run_intro(self) -> None:
        ''' Runs the game´s Intro Menu'''
        
        play_music(self, 'start')
        self.intro_running: bool = True
        self.intro_animation_index: int = 0
        self.last_switch_time: int = pygame.time.get_ticks()

        while self.intro_running:
            self.update_intro_animation()

            for event in pygame.event.get():
              self.handle_intro_events(event)

            self.display_intro(self.intro_animation_index)
            self.update_display()

    def handle_intro_events(self, event) -> None:
        ''' Handles de events when the game is closed or any key is pressed on the intro screen'''
        if event.type == pygame.QUIT:
            self.quit_game()
        elif event.type == pygame.KEYDOWN:
            self.handle_intro_keydown(event)


    def handle_intro_keydown(self, event) -> None:
        ''' Handles de keydown events on the intro screen. Load game or Start Game'''
        if event.key == pygame.K_r:
            self.load_game()
        if event.key == pygame.K_RETURN:
            self.intro_running = False

    def update_intro_animation(self) -> None:
        ''' Makes the "Press Start" ad to tick '''
        SWITCH_INTERVAL = 500  
        current_time = pygame.time.get_ticks()
        if current_time - self.last_switch_time > SWITCH_INTERVAL:
            self.intro_animation_index = 1 - self.intro_animation_index
            self.last_switch_time = current_time

    def display_intro(self, index: int) -> None:
        ''' Renders the Intro screen with the Welcome and several extra text announcements'''
        self.display.blit(self.assets['welcome'][index], (0, 0))
        self.render_intro_text()

    def render_intro_text(self) -> None:
        ''' Render on the intro screen the Record and instructions for loading game'''
        font = pygame.font.Font(None, 20)
        record_text = font.render(f'Record: {self.record}', True, (0,0,0))
        self.display.blit(record_text, (10, 10))
        font = pygame.font.Font(None, 15)
        load_game_text = font.render(f'Press "r" to load game', True, (0,0,0))
        self.display.blit(load_game_text, (200, 3))


    #start game
    def start_game(self) -> None:
        ''' Handles all the main Game initializers, rendering and events'''
        play_music(self, 'main')
        
        while True:
            self.display.blit(self.assets['background'], (0,0))
            self.handle_camera_scroll()
            render_scroll: tuple = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)
            self.update_and_render_elements(render_scroll)
            self.render_game_text()

        
            for event in pygame.event.get(): 
                self.handle_game_events(event)

            if self.game_over:
                self.handle_gameover()
                break
            
            self.update_display()

    def handle_camera_scroll(self) -> None:
        ''' Handles every camera scroll for when the player moves through the game '''
        self.rightScroll()
        self.leftScroll()
        self.downScroll()
        self.upScroll()

    def leftScroll(self)-> None:
        ''' Handles left screen movement when following the player'''
        left_edge_x = self.display.get_width() * 0.2
        if self.acrobat.rect().centerx < left_edge_x + self.scroll[0]:
            self.scroll[0] -= (left_edge_x + self.scroll[0] - self.acrobat.rect().centerx)
        
    
    def rightScroll(self)-> None:
        ''' Handles right screen movement when following the player'''
        right_edge_x = self.display.get_width() * 0.5
        if self.acrobat.rect().centerx > right_edge_x + self.scroll[0]:
            self.scroll[0] += (self.acrobat.rect().centerx - right_edge_x - self.scroll[0])
    
    def upScroll(self)-> None:
        ''' Handles up screen movement when following the player'''
        top_edge_y = self.display.get_height() * 0.2
        if self.acrobat.rect().centery < top_edge_y + self.scroll[1]:
            self.scroll[1] -= (top_edge_y + self.scroll[1] - self.acrobat.rect().centery)
     
    def downScroll(self)-> None:
        ''' Handles down screen movement when following the player'''
        bottom_edge_y = self.display.get_height() * 0.9
        if self.acrobat.rect().centery > bottom_edge_y + self.scroll[1]:
            self.scroll[1] += (self.acrobat.rect().centery - bottom_edge_y - self.scroll[1])

    def update_and_render_elements(self, render_scroll) -> None:
        ''' Encharge of rendering and updating the different elements present in the game '''
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


    def render_game_text(self) -> None:
        ''' On Game screen, renders de Score and instructions for saving current game'''
        font = pygame.font.Font(None, 20)
        score_text = font.render(f'Score: {self.score}', True, (0,0,0))
        self.display.blit(score_text, (10, 10))
        font = pygame.font.Font(None, 15)
        save_game_text = font.render(f'"q" to save and exit', True, (0,0,0))
        self.display.blit(save_game_text, (110, 3))

    def handle_game_events(self, event) -> None:
        ''' Handles que game´s events when exiting or pressing the keys'''
        if event.type == pygame.QUIT:
            self.quit_game()
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        if event.type == pygame.KEYUP:
            self.handle_keyup(event)

    def decorate(self) -> None:
        ''' Method encharge of calling the decorator for the DoubleJump that happens when a coin is grabbed'''
        self.decorator = DoubleJumpDecorator(self.acrobat)

    def handle_jump(self) -> None:
        ''' Checks what type of jump the player should perfrom depending on the decorator.'''
        if self.decorator:
            self.decorator.jump()                        
        else:
            self.acrobat.jump()
    
    def handle_swing(self) -> None:
        ''' Encharge of managing the interaction of the player with the trapezes when swinging '''
        for trapeze in self.trapezes:
            if trapeze.rect().colliderect(self.acrobat.rect()):
                trapeze.attach_entity(self.acrobat)
                self.acrobat.trapeze = trapeze
    
    def handle_keydown(self, event) -> None:
        ''' Handles the key down events on the main game, for player movement, jumping, swinging and saving game'''
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

    def handle_keyup(self, event) -> None:
        ''' Handles all key up events to stop moving or detach from trapezes'''
        if event.key == pygame.K_LEFT:
            self.movement[0] = False
        if event.key == pygame.K_RIGHT:
            self.movement[1] = False
        if event.key == pygame.K_SPACE and self.acrobat.trapeze:
            self.acrobat.trapeze.detach_entity()


    def handle_gameover(self) -> None:
        ''' Used for saving max record if set or saving game if needed '''
        self.record = max(self.record, self.score)
        caretaker.save_game(self.acrobat.pos[0], self.acrobat.pos[1], self.score, self.record, True)


    #run game over
    def run_game_over(self) -> None:
        ''' Runs the game over settings and event checking. If closing the tab or restarting the game'''
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
    def load_game(self) -> None:
        ''' Memento method that loads the game when the user hits "r" on the intro screen'''
        memento = caretaker.load_game()
        if memento:
            player_x, player_y, player_score = memento.get_saved_state()
            self.acrobat.pos[0] = player_x
            self.acrobat.pos[1] = player_y
            self.score = player_score
            self.intro_running = False

    def save_state(self,player_x, player_y, score, record) -> GameMemento:
        ''' Returns a Memento with the current state of the game to be stored '''
        return GameMemento(player_x, player_y, score, record)
    

    #shared methods
    def update_display(self) -> None:
        ''' Encarge of updating the screen of the game'''
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
        pygame.display.update()
        self.clock.tick(60)

    def quit_game(self) -> None:
        ''' When closing the tab or exiting the game '''
        pygame.quit()
        sys.exit()


#main 
game = Trapezirque()
caretaker = GameCaretaker(game)
game.run()




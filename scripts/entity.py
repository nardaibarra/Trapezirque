
from __future__ import annotations

import pygame
from abc import ABC, abstractmethod
from trapezes import Trapeze
from tilemap import Tilemap
from utils import play_sound
from enum import Enum
import random

class IDecorable(ABC):
    ''' Abstract base class representing an object that can be decorated with additional behavior, specifically focused on a jump behavior.'''
    @abstractmethod
    def jump(self) -> None:
        pass

class PlayerJumpDecorator(IDecorable):
    ''' A decorator class for IDecorable objects that enhances the jumping ability of the player.'''
    def __init__(self, player: IDecorable):
        self.player: IDecorable = player
        self.extraJumps: int = 5

    def jump(self) -> None:
        ''' Overrides the jump method to provide additional jumping functionality.'''
        self.player.jump()

class TripleJumpDecorator(PlayerJumpDecorator):
    ''' A decorator class that extends PlayerJumpDecorator to allow for multiple jumps (triple jump).'''
    def jump(self) -> None:
        '''Implements the jump method to allow for a triple jump. Reduces the number of extra jumps with each jump.'''
        if self.extraJumps:
            self.player.velocity[1] = -3
            self.extraJumps -= 1
            self.player.air_time = 5
        else:
            self.player.game.decorator = None
        

class IRenderable(ABC):
    ''' Abstract base class representing an object that can be rendered in the game.'''
    def update(self, tilemap: Tilemap, movement: tuple = (0,0)) -> None:
        pass

class Entity(IRenderable):
    GRAVITY = 0.1
    ''' Class Entity that implements the interface renderable used for players and characters'''
    def __init__(self, game, pos: tuple, size: int, e_type: str) -> None:
        self.game = game
        self.size: int = size
        self.e_type: str = e_type
        self.pos: tuple = pos        
        self.velocity: list = [0, 0]
        self.collisions: dict = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.action: str = ''
        self.animation: str = ''        
        self.anim_offset: tuple = (-1, -1)
        self.flip: bool = False
        self.set_action('idle')   
      
        
    def rect(self) -> pygame.Rect:
        ''' Returns a pygame Rect representing the entity´s current position and size'''
        return pygame.Rect(self.pos[0] , self.pos[1] , self.size[0], self.size[1])
    
    def set_action(self, action: str) -> None:
        ''' Select the action for different animations '''
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.e_type + '/' + self.action].copy()
            
    def render(self, surf: pygame.display, offset=(0,0)) -> None:
        ''' Render the element on screen with certain animation and position '''        
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - 8 - offset[1]))
            
    def update(self, tilemap: Tilemap, movement:tuple = (0,0)) -> None:
        ''' Update element´s position and identify interaction with the floor'''
        frame_movement = self.calculate_frame_movement(movement)
        self.reset_collisions()     
        self.handle_movements(tilemap, frame_movement)
        self.handle_flips(movement)
        self.apply_gravity_and_collision_effects()
        self.animation.update()  
    
    def calculate_frame_movement(self, movement: tuple) -> tuple:
        ''' Calculate overall movement for the current frame. '''
        return (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

    def reset_collisions(self):
        ''' Reset collision states for the new frame. '''
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
    
    def handle_movements(self, tilemap: Tilemap, frame_movement: tuple):
        ''' Handle horizontal and vertical movements. '''
        self.handle_movement('horizontal', tilemap, frame_movement)
        self.handle_movement('vertical', tilemap, frame_movement)
    
    def apply_gravity_and_collision_effects(self):
        ''' Apply gravity and adjust velocity based on collision states. '''
        self.velocity[1] += self.GRAVITY
        if self.collisions['bottom'] or self.collisions['top']:
            self.velocity[1] = 0

    def handle_movement(self, direction: str, tilemap: Tilemap, frame_movement: tuple) -> None:
        ''' Handle movement of the player in vertical and horizontal axis'''
        if direction == 'vertical':
            self.handle_vertical_movement(tilemap, frame_movement)
        else:
            self.handle_horizontal_movement(tilemap, frame_movement)

    def handle_vertical_movement(self, tilemap: Tilemap, frame_movement: tuple) -> None:
        '''Handle vertical movement of the player.'''
        self.update_position_and_collisions(tilemap, frame_movement, axis=1, 
                                             collision_front='bottom', collision_rear='top', axis_letter='y')
        
    def handle_horizontal_movement(self, tilemap: Tilemap, frame_movement: tuple) -> None:
        '''Handle horizontal movement of the player.'''
        self.update_position_and_collisions(tilemap, frame_movement, axis=0, 
                                             collision_front='right', collision_rear='left', axis_letter='x')
    
    def update_position_and_collisions(self, tilemap: Tilemap, frame_movement: tuple, axis: int, 
                                    collision_front: str, collision_rear: str, axis_letter: str) -> None:
        '''Update the position and detect collisions.'''
        self.pos[axis] += frame_movement[axis]
        entity_rect = self.rect()
        for rect in tilemap.physics_recs_around(self.pos):
            if entity_rect.colliderect(rect):
                self.handle_collision(entity_rect, rect, frame_movement, axis, 
                                       collision_front, collision_rear, axis_letter)

    def handle_collision(self, entity_rect, rect, frame_movement, axis, 
                          collision_front, collision_rear, axis_letter):
        '''Handle collision with another object.'''
        if frame_movement[axis] > 0:
            setattr(entity_rect, collision_front, getattr(rect, collision_rear))
            self.collisions[collision_front] = True
        if frame_movement[axis] < 0:
            setattr(entity_rect, collision_rear, getattr(rect, collision_front))
            self.collisions[collision_rear] = True
        self.pos[axis] = getattr(entity_rect, axis_letter)
                
    def handle_flips(self, movement: tuple) -> None:
        ''' Determines if the player turned to any side'''
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True  
                    
class Player(Entity, IDecorable):

    MAX_JUMPS = 2
    AIR_TIME_THRESHOLD = 4
    Y_VELOCITY_ON_JUMP = -3
    DAMPING_FACTOR = 0.98
    GAME_OVER_HEIGHT = 300
    COLLISION_VELOCITY_X = 3
    COLLISION_VELOCITY_Y = -2

    ''' Class player that inherits from Entity. Adds jump hability and manages player actions'''
    def __init__(self, game, pos: tuple, size: int, e_type: str) -> None:
        super().__init__(game, pos, size, e_type)
        self.trapeze: Trapeze = None
        self.jumps = self.MAX_JUMPS
        self.air_time = 0
        
    def update(self, tilemap: Tilemap, movement: tuple=(0, 0)) -> None:
        '''Update players position, jumps, velocity and interactions with the floor'''
        super().update(tilemap, movement)
        self.check_collision_with_characters()
        self.check_collision_with_collectables()
        self.handle_game_over_condition()
        self.reset_jumps()        
        self.velocity[0] *= self.DAMPING_FACTOR
        self.select_action(movement)
    
    def check_collision_with_collectables(self) -> None:
        '''Check for collision with characters and react accordingly'''
        for collectable in self.game.collectables:  
            if self.rect().colliderect(collectable.rect()):
                play_sound(self.game, 'collect')
                self.game.decorate()
                self.game.collectables.remove(collectable)

    def check_collision_with_characters(self) -> None:
        '''Check for collision with collectable and react accordingly'''
        for character in self.game.characters:  
            if self.rect().colliderect(character.rect()):
                self.jumps = self.MAX_JUMPS
                self.react_to_collision()

    def handle_game_over_condition(self) -> None:
        '''Check and handle the condition for the game over scenario.'''
        if self.pos[1] > self.GAME_OVER_HEIGHT:
            self.game.game_over = True
    
    def react_to_collision(self) -> None:
        '''React to collision with a character'''
        play_sound(self.game, 'collision')
        # Determine horizontal velocity based on flip state
        horizontal_velocity = self.COLLISION_VELOCITY_X if not self.flip else -self.COLLISION_VELOCITY_X
        # Set the player's velocity
        self.velocity[0] = horizontal_velocity
        self.velocity[1] = self.COLLISION_VELOCITY_Y 


    def select_action(self, movement: tuple) -> None:
        ''' Sets animation depending if the player is moving, jumping or static'''
        if self.air_time > self.AIR_TIME_THRESHOLD:
            self.set_action('jump')
        elif movement[0] == 0:
            self.set_action('idle')
            self.velocity[0] = 0
        else:
            self.set_action('walking')
                
    def reset_jumps(self) -> None:
        ''' Reset jumps when touching the ground'''
        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = self.MAX_JUMPS
    
    def jump(self) -> None:
        '''Sets conditions when jumping'''
        if self.jumps:
            self.velocity[1] = self.Y_VELOCITY_ON_JUMP
            self.jumps -= 1
            self.air_time = 5


class Character(Entity):
    ''' Class Character that inherits from Entity'''
    def __init__(self, game, pos: tuple, size: int, e_type: str) -> None:
        super().__init__(game, pos, size, e_type)    
        self.walking: int = 0
    
    def update(self, tilemap, movement=(0, 0)) -> None:
        '''Update character position, jumps, velocity and interactions with the floor'''
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1]+23)):
                if(self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking)
        elif random.random() < 0.01:
            self.walking = random.randint(30,120)
        super().update(tilemap, movement = movement)
    
    
    
class Collectable(Entity):
    ''' Class Collectable that inherits from Entity'''
    def __init__(self, game, pos: tuple, size: int, e_type: str) -> None:
        super().__init__(game, pos, size, e_type)    

    def update(self, tilemap: Tilemap, movement: tuple=(0, 0)) -> None:
        '''Update collectable animation'''
        self.animation.update()  
        
        
class Creator: 
    ''' Creator class that manages any type of entity creation'''
    def __init__(self) -> None:
        self._game = None
        self._type: str = None
        self._pos: tuple = None
        self._size: int = None
    
    @abstractmethod
    def create_entity(self, game, type: str, pos: tuple, size: int, e_type: str) -> Entity:
        ''' Generate the entity to be displayed on screen'''
        pass  

class EntityCreator(Creator): 
    ''' Concrete creator for entities'''
    class EntityType(Enum):
        # name           # value
        PLAYER           = Player
        CHARACTER        = Character
        COLLECTABLE      = Collectable
        
    def create_entity(self, game, type: str, pos: tuple, size: int, e_type: str) -> Entity:
        ''' Generate the entity to be displayed on screen'''        
        return type.value(game, pos, size, e_type)
            

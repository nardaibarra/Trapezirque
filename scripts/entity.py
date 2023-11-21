
from __future__ import annotations

import pygame
from abc import ABC, abstractmethod
from enum import Enum
import random

 
class IRenderable(ABC):
    ''' All renderable items interface'''
    def update(self, tilemap, movement = (0,0)) -> None:
        pass
        

class Entity(IRenderable):
    ''' Class Entity that implements the interface renderable used for players and characters'''
    def __init__(self, game, pos, size, e_type) -> None:
        self.game = game
        
        self.size = size
        self.e_type = e_type
        
        self.pos = pos        
        self.velocity = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        
        self.action = ''
        self.animation = ''        
        self.anim_offset = (-1, -1)
        self.flip = False
        
        self.set_action('idle')   
      
        
    def rect(self) -> pygame.Rect:
        ''' Returns a pygame Rect representing the entity´s current position and size'''
        return pygame.Rect(self.pos[0] , self.pos[1] , self.size[0], self.size[1])
    
    def set_action(self, action) -> None:
        ''' Select the action for different animations '''
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.e_type + '/' + self.action].copy()
            
    def render(self, surf, offset=(0,0)) -> None:
        ''' Render the element on screen with certain animation and position '''        
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - 8 - offset[1]))
            
    def update(self, tilemap, movement = (0,0)) -> None:
        ''' Update element´s position and identify interaction with the floor'''
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}        
        
        self.handle_movement('horizontal', tilemap, frame_movement)        
        self.handle_movement('vertical', tilemap, frame_movement)
        self.handle_flips(movement)
        
        self.velocity[1] = self.velocity[1] + 0.1 
            
        if self.collisions['bottom'] or self.collisions['top'] :
            self.velocity[1] = 0
        
        
        self.animation.update()  
                
    
    def handle_movement(self, direction, tilemap, frame_movement) -> None:
        ''' Handle movement of the player in vertical and horizontal axis'''
        if direction == 'vertical':
            axis = 1; orientation1 = 'bottom'; orientation2 = 'top'; axisletter = 'y'
        else:
            axis = 0; orientation1 = 'right'; orientation2 = 'left'; axisletter = 'x'
            
        self.pos[axis] +=frame_movement[axis]
        entity_rect = self.rect()
        for rect in tilemap.physics_recs_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[axis] > 0:
                    setattr(entity_rect, orientation1, getattr(rect, orientation2))
                    self.collisions[orientation1 if direction == 'vertical' else orientation2] = True
                if frame_movement[axis] < 0:
                    setattr(entity_rect, orientation2, getattr(rect, orientation1))
                    self.collisions[orientation2 if direction == 'vertical' else orientation2] = True
                self.pos[axis] = getattr(entity_rect, axisletter)
                
    def handle_flips(self, movement) -> None:
        ''' Determines if the player turned to any side'''
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True  
            
        
                            

class Player(Entity):
    ''' Class player that inherits from Entity. Adds jump hability and manages player actions'''
    
    def __init__(self, game, pos, size, e_type) -> None:
        super().__init__(game, pos, size, e_type)
        
        self.trapeze = None
        self.jumps = 2
        self.air_time = 0
        
    def update(self, tilemap, movement=(0, 0)) -> None:
        '''Update players position, jumps, velocity and interactions with the floor'''
        super().update(tilemap, movement)
        
        if self.pos[1] > 300:
            self.game.game_over = True
            
        self.reset_jumps()        
        
        damping_factor = 0.98
        self.velocity[0] *= damping_factor
            
        self.select_action(movement)
    
    def select_action(self, movement) ->None:
        ''' Sets animation depending if the player is moving, jumping or static'''
        if self.air_time > 4:
            self.set_action('jump')
        else:
            if movement[0] == 0:
                self.set_action('idle')
                self.velocity[0] = 0
            else:
                self.set_action('walking')
                
    def reset_jumps(self):
        ''' Reset jumps when touching the ground'''
        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = 2
    
    def jump(self) -> None:
        '''Sets conditions when jumping'''
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5


class Character(Entity):
    ''' Class Character that inherits from Entity'''
    def __init__(self, game, pos, size, e_type) -> None:
        super().__init__(game, pos, size, e_type)    

        
class Creator: #Creator Class
    ''' Creator class that manages any type of entity creation'''
    
    def __init__(self) -> None:
        self._game = None
        self._type = None
        self._pos = None
        self._size = None
    
    @abstractmethod
    def createEntity(self, game, type, pos, size, e_type):
        ''' Generate the entity to be displayed on screen'''
        pass  

class EntityCreator(Creator): #Concrete Creator
    ''' Concrete creator for entities (Player and Characters)'''
    class EntityType(Enum):
        # name           # value
        PLAYER           = Player
        CHARACTER        = Character
        # COLLECTABLE      = Collectable()
        
    def createEntity(self, game, type, pos, size, e_type):
        ''' Generate the entity to be displayed on screen'''        
        return type.value(game, pos, size, e_type)
            
        
        
        
    
    


    
    
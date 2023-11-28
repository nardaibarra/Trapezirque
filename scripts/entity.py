
from __future__ import annotations

import pygame
from abc import ABC, abstractmethod
from utils import play_sound
from enum import Enum
import random

class IDecorable(ABC):
    ''' All Decorable functions interface'''
    
    @abstractmethod
    def jump(self) -> None:
        pass

class PlayerJumpDecorator(IDecorable):
    def __init__(self, player: IDecorable):
        self.player = player
        self.extraJumps = 5

    def jump(self) -> None:
        self.player.jump()

class TripleJumpDecorator(PlayerJumpDecorator):
        
    def jump(self) -> None:
        print("Jumping from decorator")
        if self.extraJumps:
            self.player.velocity[1] = -3
            self.extraJumps -= 1
            self.player.air_time = 5
        else:
            self.player.game.decorator = None
        


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
            
        self.pos[axis] += frame_movement[axis]
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
            
        
                            

class Player(Entity, IDecorable):
    ''' Class player that inherits from Entity. Adds jump hability and manages player actions'''
    
    def __init__(self, game, pos, size, e_type) -> None:
        super().__init__(game, pos, size, e_type)
        
        self.trapeze = None
        self.jumps = 2
        self.air_time = 0
        
    def update(self, tilemap, movement=(0, 0)) -> None:
        '''Update players position, jumps, velocity and interactions with the floor'''
        super().update(tilemap, movement)
        self.check_collision_with_characters()
        self.check_collision_with_collectables()
        if self.pos[1] > 300:
            self.game.game_over = True
            
        self.reset_jumps()        
        
        damping_factor = 0.98
        self.velocity[0] *= damping_factor
            
        self.select_action(movement)
    
    def check_collision_with_collectables(self):
        '''Check for collision with characters and react accordingly'''
        for collectable in self.game.collectables:  
            if self.rect().colliderect(collectable.rect()):
                play_sound(self.game, 'collect')
                self.game.decorate()
                self.game.collectables.remove(collectable)

    def check_collision_with_characters(self):
        '''Check for collision with collectable and react accordingly'''
        for character in self.game.characters:  
            if self.rect().colliderect(character.rect()):
                self.jumps = 3
                self.react_to_collision()
    
    def react_to_collision(self):
        '''React to collision with a character'''
        # Apply a force in the opposite direction
        play_sound(self.game, 'collision')
        if(self.flip):
            self.velocity[0] =  3
            self.velocity[1] = - 2
        else:
            self.velocity[0] = - 3
            self.velocity[1] = - 2


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
        self.walking = 0
    
    def update(self, tilemap, movement=(0, 0)) -> None:
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
    def __init__(self, game, pos, size, e_type) -> None:
        super().__init__(game, pos, size, e_type)    

    def update(self, tilemap, movement=(0, 0)) -> None:
        self.animation.update()  
        
        
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
        COLLECTABLE      = Collectable
        
    def createEntity(self, game, type, pos, size, e_type):
        ''' Generate the entity to be displayed on screen'''        
        return type.value(game, pos, size, e_type)
            


    
    
    # def render(self, surf, offset=(0,0)) -> None:
    #     print("rendering balloon")
    #     img = self.assets['baloons'][0]
    #     surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
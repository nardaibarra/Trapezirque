
from __future__ import annotations

import pygame
from abc import ABC
from decorator import IDecorable
from trapezes import Trapeze
from tilemap import Tilemap
from utils import play_sound
from enum import Enum
import random


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
        self.pos: list = list(pos)        
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
    
    FLIP_CHECK_OFFSET_X = 7  
    GROUND_CHECK_Y_OFFSET = 23  
    WALKING_SPEED_ADJUSTMENT = 0.5  
    RANDOM_WALK_CHANCE = 0.01  
    MIN_WALKING_TIME = 30 
    MAX_WALKING_TIME = 120

    ''' Class Character that inherits from Entity'''
    def __init__(self, game, pos: tuple, size: int, e_type: str) -> None:
        super().__init__(game, pos, size, e_type)    
        self.walking: int = 0
    
    def update(self, tilemap, movement=(0, 0)) -> None:
        '''Update character position, jumps, velocity and interactions with the floor'''
        movement = self.determine_movement(tilemap, movement)
        super().update(tilemap, movement=movement)

    def determine_movement(self, tilemap, movement):
        '''Determine character movement based on walking status and tilemap interaction.'''
        if self.walking:
            movement = self.handle_walking_logic(tilemap, movement)
        elif random.random() < self.RANDOM_WALK_CHANCE:
            self.walking = random.randint(self.MIN_WALKING_TIME, self.MAX_WALKING_TIME)
        return movement
    
    def handle_walking_logic(self, tilemap, movement):
        '''Handle walking logic including flipping direction and adjusting movement.'''

        next_position = self.calculate_next_position()
        is_solid_ground = tilemap.solid_check(next_position)

        if is_solid_ground:
            movement = self.adjust_movement_if_not_colliding(movement)
        else:
            self.flip_direction()

        return movement

    def calculate_next_position(self) -> tuple:
        '''Calculate the character's next horizontal and vertical positions.'''
        horizontal_direction = -1 if self.flip else 1
        horizontal_offset = self.FLIP_CHECK_OFFSET_X * horizontal_direction
        next_horizontal_position = self.rect().centerx + horizontal_offset
        next_vertical_position = self.pos[1] + self.GROUND_CHECK_Y_OFFSET

        return (next_horizontal_position, next_vertical_position)

    def adjust_movement_if_not_colliding(self, movement) -> tuple:
        '''Adjust movement if the character is not colliding.'''
        if not self.is_colliding_horizontally():
            movement = self.get_adjusted_movement(movement)
        else:
            self.flip_direction()
        return movement

    def is_colliding_horizontally(self) -> bool:
        '''Check if the character is colliding horizontally.'''
        return self.collisions['right'] or self.collisions['left']

    def get_adjusted_movement(self, movement: tuple) -> bool:
        '''Calculate adjusted movement based on walking speed.'''
        direction_multiplier = -1 if self.flip else 1
        horizontal_adjustment = self.WALKING_SPEED_ADJUSTMENT * direction_multiplier
        adjusted_horizontal_movement = movement[0] + horizontal_adjustment
        return (adjusted_horizontal_movement, movement[1])

    def flip_direction(self) -> None:
        '''Flip the character's direction.'''
        self.flip = not self.flip
        
    
    
class Collectable(Entity):
    ''' Class Collectable that inherits from Entity'''
    def __init__(self, game, pos: tuple, size: int, e_type: str) -> None:
        super().__init__(game, pos, size, e_type)    

    def update(self, tilemap: Tilemap, movement: tuple=(0, 0)) -> None:
        '''Update collectable animation'''
        self.animation.update()  
        
        

            

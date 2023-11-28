import pygame
import math as m
import random

class Trapeze:
    ''' Create a trapeze object '''
    ANGLE = 5.5
    ANGULAR_VELOCITY = -0.002
    GRAVITY = 0.01
    VERTICAL_VELOCITY = 0   
    LINE_WIDTH = 4
    
    def __init__(self, game, position: tuple, length: int, radius:int) -> None:
        self.game = game
        self.position: tuple = position
        self.length: int = length
        self.radius: int = radius
        self.angle: float = self.ANGLE 
        self.angular_velocity: float = self.ANGULAR_VELOCITY
        self.swinging: bool = True
        self.attached_entity: bool = None
        self.gravity: float = self.GRAVITY 
        self.vertical_velocity: int = self.VERTICAL_VELOCITY 

    def rect(self) -> pygame.Rect:
        ''' Returns a pygame Rect representing the trapeze´s current position and size'''
        
        end_x: float = self.position[0] + self.length * m.sin(self.angle)
        end_y: float = self.position[1] + self.length * m.cos(self.angle)
        return pygame.Rect(end_x - self.radius, end_y - self.radius, self.radius * 2, self.radius * 2)

    def attach_entity(self, entity) -> None:
        ''' Attaches and entity to a trapeze '''
        self.attached_entity = entity
        self.swinging = True
        self.angular_velocity = self.attached_entity.velocity[0] * 2

    def detach_entity(self) -> None:
        ''' Detaches any entity currently attached to a trapeze'''
        if self.attached_entity:
            horizontal_velocity = self.length * self.angular_velocity * m.cos(self.angle)
            vertical_velocity = -self.length * self.angular_velocity * m.sin(self.angle)

            self.attached_entity.velocity[0] = horizontal_velocity * 2
            self.attached_entity.velocity[1] = vertical_velocity * 2

            self.attached_entity = None
            self.swinging = False

    def update(self) -> None:
        ''' Updates the state of the trapeze, including its angle and attached entity'''
        if self.swinging and self.attached_entity:            
            self.handle_physics()
            self.handle_gravity()
            self.update_attached_entity()
            
    def handle_physics(self) -> None:
        ''' Handles the physics of the trapeze swing '''
        g = 0.3 
        angular_acceleration = -(g / self.length) * m.sin(self.angle)
        next_av = (self.angular_velocity + angular_acceleration)
        top_av = 0.1
        self.angular_velocity = min(next_av, top_av)
        self.angle += min(0.3, self.angular_velocity)
        
    def handle_gravity(self) -> None:
        ''' Handles gravity effect on the trapeze and atached entity'''
        self.vertical_velocity = min(3, self.vertical_velocity + self.gravity)
        if self.attached_entity.collisions['bottom']:
            self.vertical_velocity = self.VERTICAL_VELOCITY
            
    def update_attached_entity(self) -> None:
        ''' Updates the position of the entity attached to the trapeze'''
        attached_x = self.position[0] + self.length * m.sin(self.angle)
        attached_y = self.position[1] + self.length * m.cos(self.angle)

        self.attached_entity.pos = [attached_x - (self.radius*2), attached_y - self.radius]
            
        
    def draw(self, surface, offset=(0, 0)) -> None:
        ''' Draws the trapeze on the specified surface and position '''
        
        end_x: float = self.position[0] + self.length * m.sin(self.angle)
        end_y: float = self.position[1] + self.length * m.cos(self.angle)

        pygame.draw.line(surface, (0, 0, 10), self.calculate_start_position(offset), self.calculate_bottom_position(offset, end_x, end_y), self.LINE_WIDTH)
        pygame.draw.circle(surface, (30, 0, 0), (round(end_x - offset[0]), round(end_y - offset[1])), self.radius, 2)

    
    def calculate_start_position(self, offset):
        return (self.position[0] - offset[0], self.position[1] - offset[1])
    
    def calculate_bottom_position(self, offset, end_x, end_y):
        return (end_x - offset[0], end_y - offset[1])
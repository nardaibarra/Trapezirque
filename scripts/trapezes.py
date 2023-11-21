import pygame
import math as m
import random

class Trapeze:
    ''' Create a trapeze object '''
    def __init__(self, game, position, length, radius) -> None:
        self.game = game
        self.position = position  # Position of the pendulum's anchor point
        self.length = length
        self.radius = radius
        self.angle = 5.5  # Initial angle
        self.angular_velocity = -0.002
        self.swinging = True
        self.attached_entity = None
        self.gravity = 0.01  # Gravity effect
        self.vertical_velocity = 0  # Vertical velocity

    def reset(self) -> None:
        ''' Resets the trapeze on its original state'''
        self.angle = 1.6  # Initial angle
        self.angular_velocity = 0.3
        self.swinging = True
        self.attached_entity = None
        self.vertical_velocity = 0  # Vertical velocity

    def rect(self) -> pygame.Rect:
        ''' Returns a pygame Rect representing the trapeze´s current position and size'''
        
        end_x = self.position[0] + self.length * m.sin(self.angle)
        end_y = self.position[1] + self.length * m.cos(self.angle)
        return pygame.Rect(end_x - self.radius, end_y - self.radius, self.radius * 2, self.radius * 2)

    def attach_entity(self, entity) -> None:
        ''' Attaches and entity to a trapeze '''
        self.attached_entity = entity
        self.swinging = True
        self.angular_velocity = self.attached_entity.velocity[0] * 2

    def detach_entity(self) -> None:
        ''' Detaches any entity currently attached to a trapeze'''
        if self.attached_entity:
            # Calculate the pendulum's velocity components
            horizontal_velocity = self.length * self.angular_velocity * m.cos(self.angle)
            vertical_velocity = -self.length * self.angular_velocity * m.sin(self.angle)

            # Apply this velocity to the attached entity
            self.attached_entity.velocity[0] = horizontal_velocity * 2
            self.attached_entity.velocity[1] = vertical_velocity * 2

            # Detach the entity
            self.attached_entity = None
            self.swinging = False

    def update(self) -> None:
        ''' Updates the state of the trapeze, including its angle and attached entity'''
        if self.swinging and self.attached_entity:
            # Pendulum physics
            g = 0.3  # Acceleration due to gravity
            angular_acceleration = -(g / self.length) * m.sin(self.angle)
            next_av = (self.angular_velocity + angular_acceleration)
            top_av = 0.1
            self.angular_velocity = min(next_av, top_av)
            self.angle += min(0.3, self.angular_velocity)

            # Gravity effect on the attached entity
            self.vertical_velocity = min(3, self.vertical_velocity + self.gravity)
            if self.attached_entity.collisions['bottom']:
                self.vertical_velocity = 0

            # Update the position of the attached entity
            attached_x = self.position[0] + self.length * m.sin(self.angle)
            attached_y = self.position[1] + self.length * m.cos(self.angle)

            self.attached_entity.pos = [attached_x - (self.radius*2), attached_y - self.radius]
            

    def draw(self, surface, offset=(0, 0)) -> None:
        # Calculate pendulum's end position based on angle
        end_x = self.position[0] + self.length * m.sin(self.angle)
        end_y = self.position[1] + self.length * m.cos(self.angle)
        # Draw the pendulum
        pygame.draw.line(surface, (0, 0, 10), (self.position[0] - offset[0], self.position[1] - offset[1]), (end_x - offset[0], end_y - offset[1]), 4)
        pygame.draw.circle(surface, (30, 0, 0), (round(end_x - offset[0]), round(end_y - offset[1])), self.radius, 2)

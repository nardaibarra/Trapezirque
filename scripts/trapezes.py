import pygame
import math as m

class Trapezes:
    def __init__(self, game, position, length, radius):
        self.game = game
        self.position = position  # Position of the pendulum's anchor point
        self.length = length
        self.radius = radius
        self.angle = -20  # Initial angle
        self.angular_velocity = -0.002
        self.swinging = True
        self.attached_entity = None
        self.gravity = 0.01  # Gravity effect
        self.vertical_velocity = 0  # Vertical velocity

    def rect(self):
        # Coordinates of one end of the rod
        end_x = self.position[0] + self.length * m.sin(self.angle)
        end_y = self.position[1] + self.length * m.cos(self.angle)

        # Top-left corner of the rectangle
        top_left_x = min(self.position[0], end_x) - self.radius
        top_left_y = min(self.position[1], end_y) - self.radius

        # Dimensions of the rectangle
        rect_width = abs(end_x - self.position[0]) + 2 * self.radius
        rect_height = abs(end_y - self.position[1]) + 2 * self.radius

        return pygame.Rect(top_left_x, top_left_y, rect_width, rect_height)

    def attach_entity(self, entity):
        self.attached_entity = entity
        self.swinging = True
        # Calculate the attachment point based on the collision
        collision_point = entity.pos
        self.attachment_fraction = self.calculate_attachment_fraction(collision_point)

    def calculate_attachment_fraction(self, collision_point):
        # Calculate the distance from the rod's pivot to the collision point
        distance = m.sqrt((collision_point[0] - self.position[0])**2 + (collision_point[1] - self.position[1])**2)
        # Calculate the fraction along the rod's length
        return distance / self.length

    def detach_entity(self):
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

    def update(self):
        if self.swinging and self.attached_entity:
            # Pendulum physics
            g = 0.3  # Acceleration due to gravity
            angular_acceleration = -(g / self.length) * m.sin(self.angle)
            self.angular_velocity += angular_acceleration
            self.angle += self.angular_velocity

            # # Damping (optional)
            # self.angular_velocity *= 0.99

            # Gravity effect on the attached entity
            self.vertical_velocity = min(3, self.vertical_velocity + self.gravity)
            if self.attached_entity.collisions['down']:
                self.vertical_velocity = 0

            # Update the position of the attached entity
            attached_x = self.position[0] + self.length * self.attachment_fraction * m.sin(self.angle)
            attached_y = self.position[1] + self.length * self.attachment_fraction * m.cos(self.angle) + self.vertical_velocity

            self.attached_entity.pos = [attached_x - self.radius, attached_y - self.radius]

    def draw(self, surface, offset=(0, 0)):
        # Calculate pendulum's end position based on angle
        end_x = self.position[0] + self.length * m.sin(self.angle)
        end_y = self.position[1] + self.length * m.cos(self.angle)
        # Draw the pendulum
        pygame.draw.line(surface, (255, 255, 255), (self.position[0] - offset[0], self.position[1] - offset[1]), (end_x - offset[0], end_y - offset[1]), 4)
        pygame.draw.circle(surface, (255, 0, 0), (round(end_x - offset[0]), round(end_y - offset[1])), self.radius)

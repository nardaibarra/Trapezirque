from abc import ABC
import random
import pygame
from utils import play_sound


# class IDecorable(ABC):
#     ''' All Decorable functions interface'''
#     def render(self, surf, offset=(0,0)) -> None:
#         ''' Renders the ballon on the given surface and position '''
#         pass

class Balloon:
    ''' Creates a new Ballon object '''
    def __init__(self, game, pos, img, speed_x, speed_y, size) -> None:
        self.pos = list(pos)
        self.img = img
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.game = game

    def update(self) -> None:
        ''' Updates the ballon´s position based on speed '''
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

    def render(self, surf, offset=(0,0)) -> None:
        ''' Renders the ballon on the given surface and position '''
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def rect(self) -> pygame.Rect:
        ''' Returns a pygame Rect representing the balloon´s current position and size'''
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

class Balloons:
    ''' Class used for Ballons collections '''

    def __init__(self, game, balloons_images, size, count = 20) -> None:
        self.balloons_images = balloons_images
        self.balloons = []
        self.game = game
        self.size = size

        for _ in range(count):
            x = random.randrange(0, self.game.W/2)
            y = random.randrange(0, self.game.H/2)
            img = random.choice(self.balloons_images)
            speed_x = -(random.random() * 0.05 + 0.05)
            speed_y = -(random.random() * 0.05 + 0.15) 
            self.balloons.append(Balloon(self.game, (x, y), img, speed_x, speed_y, self.size))
    
    def update(self) -> None:
        ''' Updates all ballons in the collection '''
        for balloon in self.balloons:
            balloon.update()
            
            if balloon.pos[0] < 0 or self.game.acrobat.pos[0] - balloon.pos[0] > 165:
                balloon.pos[0] = balloon.pos[0] + self.game.W/2 + random.randrange(10, 50)  # Off-screen to the right
                balloon.pos[1] = random.randrange(0,240)
            

    def render(self, surf, offset=(0,0)) -> None:
        ''' Renders all ballons in the collection on the given surface and position'''
        for balloon in self.balloons:           
            
            balloon.render(surf, offset)
            balloon_rect = balloon.rect()

            if balloon_rect.colliderect(self.game.acrobat.rect()):
                play_sound(self.game, 'balloon')
                self.game.score += 1
                balloon.pos[0] = balloon.pos[0] + self.game.W/2 + random.randrange(10, 50)  # Off-screen to the right
                balloon.pos[1] = random.randrange(0,240)

    # def decorate_balloons(self):
    #     for i in range(len(self.balloons)):
    #         self.balloons[i] = ColorBalloonDecoartor(self.balloons[i])



# class BalloonDecorator(IDecorable):
#     def __init__(self, balloon):
#         self.balloon = balloon

#     def __getattr__(self, name):
#         return getattr(self.player, name)

#     def render(self):
#         pass

# class ColorBalloonDecoartor(BalloonDecorator):
#     def render(self, surf, offset=(0,0)) -> None:
#         print("rendering balloon")
#         img = self.assets['baloons'][0]
#         surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
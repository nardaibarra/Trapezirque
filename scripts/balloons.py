import random
import pygame
from utils import play_sound


class Balloon:
    ''' Creates a new Ballon object '''
    def __init__(self, game, pos: tuple, img: str, speed_x: int, speed_y: int, size:int ) -> None:
        self.pos: list(tuple) = list(pos)
        self.img: str = img
        self.speed_x: int = speed_x
        self.speed_y: int = speed_y
        self.size: int = size
        self.game = game
        self.alreadycollide: bool = False

    def update(self) -> None:
        ''' Updates the ballon´s position based on speed '''
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

    def render(self, surf: pygame.display, offset: tuple =(0,0)) -> None:
        ''' Renders the ballon on the given surface and position '''
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def rect(self) -> pygame.Rect:
        ''' Returns a pygame Rect representing the balloon´s current position and size'''
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

class Balloons:
    ''' Class used for Ballons collections '''
    BALLOON_MIN_POSITION = 0
    BALLOON_MAX_POSITION = 165
    SPEED_FACTOR_X = 0.05
    SPEED_FACTOR_Y = 0.15
    MAX_HEIGHT = 240
    MIN_HEIGHT = 0
    OFF_SCREEN_MIN = 10
    OFF_SCREEN_MAX = 50

    def __init__(self, game, balloons_images, size, count = 20) -> None:
        self.balloons_images: list(pygame.image) = balloons_images
        self.game = game
        self.size: int = size
        self.balloons: list[Balloon] = self.initialize_ballons(count)

       
    
    def initialize_ballons(self, count):
        balloons = []
        for _ in range(count):
            x = random.randrange(0, self.game.W/2)
            y = random.randrange(0, self.game.H/2)
            img = random.choice(self.balloons_images)
            speed_x = -(random.random() * self.SPEED_FACTOR_X + self.SPEED_FACTOR_X)
            speed_y = -(random.random() * self.SPEED_FACTOR_X + self.SPEED_FACTOR_Y) 
            
            balloons.append(Balloon(self.game, (x, y), img, speed_x, speed_y, self.size))
        
        return balloons
        
    
    
    def update(self) -> None:
        ''' Updates all ballons in the collection '''
        for balloon in self.balloons:
            balloon.update()
            
            position_difference = self.game.acrobat.pos[0] - balloon.pos[0]
                        
            if balloon.pos[0] < self.BALLOON_MIN_POSITION or position_difference > self.BALLOON_MAX_POSITION:
                off_screen = random.randrange(self.OFF_SCREEN_MIN, self.OFF_SCREEN_MAX) 
                
                balloon.pos[0] = balloon.pos[0] + self.game.W/2 + off_screen 
                balloon.pos[1] = random.randrange(self.MIN_HEIGHT, self.MAX_HEIGHT)
            

    def render(self, surf, offset=(0,0)) -> None:
        ''' Renders all ballons in the collection on the given surface and position'''
        for balloon in self.balloons:           
            
            balloon.render(surf, offset)
            balloon_rect = balloon.rect()

            if balloon_rect.colliderect(self.game.acrobat.rect()):
                play_sound(self.game, 'balloon')
                self.increase_points()                    
                    
                self.alreadycollide = True  
                off_screen = random.randrange(self.OFF_SCREEN_MIN, self.OFF_SCREEN_MAX)             
                balloon.pos[0] = balloon.pos[0] + self.game.W/2 + off_screen  
                balloon.pos[1] = random.randrange(self.MIN_HEIGHT,self.MAX_HEIGHT)

    def increase_points(self) -> None:
        ''' Increases points of the score when grabing ballons '''
        self.game.score += 1
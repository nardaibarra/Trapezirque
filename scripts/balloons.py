import random
import pygame

class Balloon:
    def __init__(self, game, pos, img, speed_x, speed_y, size) -> None:
        self.pos = list(pos)
        self.img = img
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.game = game

    def update(self):
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

    def render(self, surf, offset=(0,0)):
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)
class Balloons:

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
    
    def update(self):
        for balloon in self.balloons:
            balloon.update()
            
            if balloon.pos[0] < 0 or self.game.acrobat.pos[0] - balloon.pos[0] > 165:
                balloon.pos[0] = balloon.pos[0] + self.game.W/2 + random.randrange(10, 50)  # Off-screen to the right
                balloon.pos[1] = random.randrange(0,240)
            

    def render(self, surf, offset=(0,0)):
        for balloon in self.balloons:
            print(f'{balloon.pos[0]}, {balloon.pos[1]}')
            print(f'Acrobat: {self.game.acrobat.pos[0]}, {self.game.acrobat.pos[1]}')
            
            
            balloon.render(surf, offset)
            balloon_rect = balloon.rect()
            # print(balloon_rect)
            # print(self.game.acrobat.rect())
            if balloon_rect.colliderect(self.game.acrobat.rect()):
                self.game.score += 1
                balloon.pos[0] = balloon.pos[0] + self.game.W/2 + random.randrange(10, 50)  # Off-screen to the right
                balloon.pos[1] = random.randrange(0,240)

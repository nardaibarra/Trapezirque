import pygame

class Acrobat:
    def __init__(self, game, e_type, pos, size) -> None:
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.points = 0
        self.trapeze = None


    def rect(self):
        return pygame.Rect(self.pos[0] , self.pos[1] , self.size[0], self.size[1])

    def update(self, tilemap, movement = (0,0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        
        #manage horizontal 
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_recs_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['left'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['right'] = True
                self.pos[0] = entity_rect.x

        #manage vertical 
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_recs_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y


        self.velocity[1] = self.velocity[1] + 0.1 

        damping_factor = 0.98
        self.velocity[0] *= damping_factor
        self.velocity[1] *= damping_factor

        # Stop movement if velocity is very low
        if abs(self.velocity[0]) < 0.01:
            self.velocity[0] = 0
        if abs(self.velocity[1]) < 0.01:
            self.velocity[1] = 0


        if self.collisions['down'] or self.collisions['up'] :
            self.velocity[1] = 0

        if self.pos[1] > 300:
            self.game.game_over = True
    
    def render(self, surf,  offset=(0,0)):
        surf.blit(self.game.assets['acrobat'], (self.pos[0] - offset[0], self.pos[1] - 8 - offset[1]))
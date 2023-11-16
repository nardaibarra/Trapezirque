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
        self.jumps = 2
        
        self.air_time = 0
        
        self.action = ''
        self.anim_offset = (-1, -1)
        self.flip = False
        
        self.set_action('idle')
        

    def rect(self):
        return pygame.Rect(self.pos[0] , self.pos[1] , self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            
            

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

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True        

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
        
        self.animation.update()
        
            
        if self.pos[1] > 300:
            self.game.game_over = True
            
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2
        
        if self.air_time > 4:
            self.set_action('jump')
        else:
            self.set_action('idle')
        
          
    
    def render(self, surf,  offset=(0,0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - 8 - offset[1] + self.anim_offset[1]))
        # surf.blit(self.game.assets['acrobat'], (self.pos[0] - offset[0], self.pos[1] - 8 - offset[1]))
        
    def jump(self):
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
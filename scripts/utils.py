import os
import pygame

BASE_IMG_PATH = 'assets/'

def get_assets():
    assets = {
            'welcome': load_images('welcome'),
            'game_over': load_image('game_over_2.png'),
            'background': load_image('bg.png'),
            'floor': load_images('tiles/floor'),
            'circus': load_images('tiles/circus'),
            'balloons': load_images('balloons'),
            'spawners': load_images('tiles/spawners'),
            'coin/idle': Animation(load_images('coin/idle'),10),
            'monkey/idle': Animation(load_images('monkey/idle'),10),
            'clown/idle': Animation(load_images('clown/idle'),10),
            'acrobat/jump': Animation(load_images('player/jump')),
            'acrobat/idle': Animation(load_images('player/idle')),
            'acrobat/walking': Animation(load_images('player/walking')),
            'music': {
                'start': './assets/music/Trapeqzirque_start_screen.mp3',
                'main': './assets/music/Trapeqzirque_main.mp3',
                'game_over': './assets/music/Trapeqzirque_game_over.mp3'},
            'sounds': {
                'collect': './assets/sounds/collect.mp3',
                'collision':'./assets/sounds/collapse.mp3',
                'jump':'./assets/sounds/jump.wav',
                'balloon':'./assets/sounds/balloon.wav',
            }
            
        }
    
    return assets

def load_image(path: str) -> pygame.Surface:
    ''' Loads an image from the specified path '''
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0 ,0))
    return img

def load_images(path: str) -> list[pygame.Surface]:
    ''' Loads all images from an specified directory '''
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def play_sound(game, effectName: str) -> None:
    effectPath = game.assets['sounds'][effectName]
    soundEffect = pygame.mixer.Sound(effectPath)
    soundEffect.set_volume(0.5)
    soundEffect.play()

def play_music(game, song_name: str) -> None:
    ''' Play the music of the game'''
    pygame.mixer.music.load(game.assets['music'][song_name])
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)


class Animation:
    ''' Class animation to add movement on elements '''
    def __init__(self, images: list , img_dur: int=5, loop: bool =True) -> None:
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
        
    def copy(self) -> 'Animation':
        ''' Creates copy of the current Animation object'''
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self) -> None:
        ''' Updates the animation frame. Should be called periodically to animate'''
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self) -> pygame.Surface:
        ''' Gets the current image of the animation '''
        return self.images[int(self.frame/self.img_duration)]
    
    
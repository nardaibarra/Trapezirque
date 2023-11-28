import pygame
import random
import json

NEIGHBOR_TILES = [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(0,0)]
#   - 1  0  1
# - 1 x  x  x
#   0 x  x  x 
#   1 x  x  x
PHYSICS_TILES = {'floor','circus'}

class Tilemap:
    
    '''A class to represent a tilemap in a game. Each tile is assumed to be 16x16 pixels by default.'''
    
    def __init__(self, game, tile_size: int =16) -> None:
        self.game = game
        self.tile_size: int = tile_size
        self.tilemap : dict = {}
        self.offgrid_tiles: list = []

    def extract(self, id_pairs: list, keep: bool =False) -> list:
        ''' Extracts tiles matching the given id_pairs from the tilemap '''
        matches = []
        
        self.build_offgrid(id_pairs, matches, keep)
        self.build_ongrid(id_pairs, matches, keep)      
        
        return matches
    
    def build_offgrid(self, id_pairs: list, matches: list, keep) -> None:
        ''' Helper method to extract tiles from offgrid_tiles. '''
        for tile in self.offgrid_tiles.copy():
            if(tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
                    
    def build_ongrid(self, id_pairs: list, matches: list, keep) -> None:
        ''' Helper method to extract tiles from the main tilemap. '''
        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if(tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        
        
    def tiles_around(self, pos: tuple) -> None:
        ''' Returns a list of tiles surrounding a given position. '''
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size),int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_TILES:
            check_lock = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_lock in self.tilemap:
                tiles.append(self.tilemap[check_lock])
        return tiles
    
    def save(self, path: str) -> None:
        ''' Saves the current state of the tilemap to a file. '''
        print('saving')
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    def load(self, path: str) -> None:
        ''' Loads a tilemap from a file. '''
        f = open(path, 'r')
        map_data = json.load(f)
        f.close

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles= map_data['offgrid']

    def solid_check(self, pos) -> dict:
        ''' Checks if a tile at a given position is solid. '''
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]


    def physics_recs_around(self, pos: tuple) -> list:
        ''' Returns a list of rectangles for physics interactions around a given position. '''
        recs = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                left = tile['pos'][0] * self.tile_size
                top = tile['pos'][1] * self.tile_size
                width = self.tile_size
                height = self.tile_size
                recs.append(pygame.Rect(left, top, width, height))
        return recs

    def render(self, surf, offset=(0,0)) -> None:
        ''' Renders the tilemap onto a given surface. '''
        self.render_offgrid(surf, offset)  
        self.render_ongrid(surf, offset)  
        
    def render_offgrid(self, surf, offset) -> None:
        '''Helper method to render offgrid tiles.'''
        for tile in self.offgrid_tiles:
            pos_x = tile['pos'][0] - offset[0]
            pos_y = tile['pos'][1] - offset[1]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (pos_x,pos_y))[tile['variant']]
            
    def render_ongrid(self, surf, offset) -> None:
        ''' Helper method to render ongrid tiles. '''
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            pos_x = tile['pos'][0] * self.tile_size - offset[0]
            pos_y = tile['pos'][1] * self.tile_size - offset[1]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (pos_x,pos_y ))
        
        
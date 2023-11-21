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
    #each tile is 16 pix x 16 pix
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False) -> list:
        matches = []
        for tile in self.offgrid_tiles.copy():
            if(tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if(tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        return matches
        
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size),int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_TILES:
            check_lock = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_lock in self.tilemap:
                tiles.append(self.tilemap[check_lock])
        return tiles
    
    def save(self, path):
        print('saving')
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles= map_data['offgrid']



    def physics_recs_around(self, pos):
        recs = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                recs.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return recs

    def render(self, surf, offset=(0,0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0],tile['pos'][1] - offset[1]))[tile['variant']]
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
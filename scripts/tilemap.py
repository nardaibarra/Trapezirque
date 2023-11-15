import pygame

NEIGHBOR_TILES = [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(0,0)]
#   - 1  0  1
# - 1 x  x  x
#   0 x  x  x 
#   1 x  x  x
PHYSICS_TILES = {'sand'}

class Tilemap:
    #each tile is 16 pix x 16 pix
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        
        for i in range(10):
            self.tilemap[str(i) + ';14'] = {'type': 'sand','variant': 0, 'pos':(i, 14)}
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size),int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_TILES:
            check_lock = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_lock in self.tilemap:
                tiles.append(self.tilemap[check_lock])
        return tiles
    
    def physics_recs_around(self, pos):
        recs = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                recs.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return recs

    def render(self, surf, offset=(0,0)):
        #this is to render tiles that have No contact with the player
        # for tile in self.offgrid_tiles:
        #     surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0],tile['pos'][1] - offset[1]))
    #[tile['variant']]


        #this is to render tiles that have contact with the player
        #for each location in the dictionary
        for loc in self.tilemap:
            
            #get the values from de dict
            print(self.tilemap[loc])
            tile = self.tilemap[loc]
            print(self.game.assets)
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
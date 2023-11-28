
from abc import abstractmethod
from enum import Enum

from entity import Character, Collectable, Entity, Player


class Creator: 
    ''' Creator class that manages any type of entity creation'''
    def __init__(self) -> None:
        self._game = None
        self._type: str = None
        self._pos: tuple = None
        self._size: int = None
    
    @abstractmethod
    def create_entity(self, game, type: str, pos: tuple, size: int, e_type: str) -> Entity:
        ''' Generate the entity to be displayed on screen'''
        pass  

class EntityCreator(Creator): 
    ''' Concrete creator for entities'''
    class EntityType(Enum):
        # name           # value
        PLAYER           = Player
        CHARACTER        = Character
        COLLECTABLE      = Collectable
        
    def create_entity(self, game, type: str, pos: tuple, size: int, e_type: str) -> Entity:
        ''' Generate the entity to be displayed on screen'''        
        return type.value(game, pos, size, e_type)
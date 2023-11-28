from abc import ABC, abstractmethod


class IDecorable(ABC):
    ''' Abstract base class representing an object that can be decorated with additional behavior, specifically focused on a jump behavior.'''
    @abstractmethod
    def jump(self) -> None:
        pass

class PlayerJumpDecorator(IDecorable):
    ''' A decorator class for IDecorable objects that enhances the jumping ability of the player.'''
    def __init__(self, player: IDecorable):
        self.player: IDecorable = player
        self.extraJumps: int = 5

    def jump(self) -> None:
        ''' Overrides the jump method to provide additional jumping functionality.'''
        self.player.jump()

class TripleJumpDecorator(PlayerJumpDecorator):
    ''' A decorator class that extends PlayerJumpDecorator to allow for multiple jumps (triple jump).'''
    def jump(self) -> None:
        '''Implements the jump method to allow for a triple jump. Reduces the number of extra jumps with each jump.'''
        if self.extraJumps:
            self.player.velocity[1] = -3
            self.extraJumps -= 1
            self.player.air_time = 5
        else:
            self.player.game.decorator = None
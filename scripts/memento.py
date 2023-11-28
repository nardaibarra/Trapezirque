import json

class GameMemento: 
    def __init__(self, x: int, y: int, score: int, record: int) -> None:
        self.player_x: int = x
        self.player_y: int = y
        self.score: int = score
        self.record: int = record

    def get_saved_state(self):
        return self.player_x, self.player_y, self.score
    
    def get_last_record(self):
        return self.record

    
class GameCaretaker: 
    def __init__(self, game, filepath: str = 'game_save.json') -> None:
        self.filepath: str= filepath
        self.game = game
        self.last_state_memento: GameMemento = self.load_game()

    def save_game(self, player_x: int, player_y: int, score: int, record: int, newRecord: int) -> None:
        if newRecord:
            self.last_state_memento = self.game.save_state(self.last_state_memento.player_x, self.last_state_memento.player_y, self.last_state_memento.score, record)
        else:
            self.last_state_memento = self.game.save_state(player_x, player_y, score, self.last_state_memento.record)

        with open(self.filepath, 'w') as file:
            json.dump({
                'player_x': self.last_state_memento.player_x,
                'player_y': self.last_state_memento.player_y,
                'score': self.last_state_memento.score,
                'record': self.last_state_memento.record
            }, file)

    def load_game(self) -> GameMemento:
        try:
            with open(self.filepath, 'r') as file:
                data = json.load(file)
                return GameMemento(data['player_x'], data['player_y'], data['score'], data['record'])
        except FileNotFoundError:
            return None
        
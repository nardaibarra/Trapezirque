import json

class GameMemento: 
    def __init__(self, x, y, score, record) -> None:
        self.player_x = x
        self.player_y = y
        self.score = score
        self.record = record

    def get_saved_state(self):
        return self.player_x, self.player_y, self.score
    
    def get_last_record(self):
        return self.record

    
class GameCaretaker: 
    def __init__(self, game, filepath = 'game_save.json') -> None:
        self.filepath = filepath
        self.game = game
        self.last_state_memento = self.load_game()

    def save_game(self, player_x, player_y, score, record, newRecord):
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

    def load_game(self):
        try:
            with open(self.filepath, 'r') as file:
                data = json.load(file)
                return GameMemento(data['player_x'], data['player_y'], data['score'], data['record'])
        except FileNotFoundError:
            return None
        
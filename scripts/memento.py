import json

class GameMemento: 
    def __init__(self, x, y, score) -> None:
        self.player_x = x
        self.player_y = y
        self.record = score
    
    def get_saved_state(self):
        return self.player_x, self.player_y, self.record
    
class GameCaretaker: 
    def __init__(self, filepath = 'game_save.json') -> None:
        self.filepath = filepath
        memento = None
        
    def save_memento(self, memento):
        with open(self.filepath, 'w') as file:
            json.dump({
                'player_x': memento.player_x,
                'player_y': memento.player_y,
                'record': memento.record
            }, file)

    def load_memento(self):
        try:
            with open(self.filepath, 'r') as file:
                data = json.load(file)
                return GameMemento(data['player_x'], data['player_y'], data['record'])
            
        except FileNotFoundError:
            return None
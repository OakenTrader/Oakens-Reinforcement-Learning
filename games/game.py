class Game:
    def __init__(self):
        self.players = []
        self.screen = None
        self.winner = None

    def add_player(self, player):
        self.players.append(
            {"Name": player.name,
             "player": player,
             "status": "added",
             "score": 0
             }
        )


class Player:
    def __init__(self, name):
        self.name = name

    def get_response(self):
        pass

    def send_message(self):
        pass


class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.prompt = f"{name} enters:"
        self.send_message = print

    def get_response(self, prompt=None):
        return input(self.prompt)

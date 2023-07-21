import asyncio
import time
import numpy as np
import inspect
from PIL import Image
class Game:
    def __init__(self):
        self.id = time.time()
        self.players = []
        self.screen = None
        self.winner = None
        self.status = "Waiting"
        self.player_limit = 65536
        self.min_players = 1
        self.console_channel = dict()

    def console(self, message):
        for channel in self.console_channel:
            self.send_message(self.console_channel[channel], message)

    def add_player(self, player):
        if len(self.players) < self.player_limit:
            player_info = {"Name": player.name,
                 "id":time.time(),
                 "player": player,
                 "status": "added",
                 "score": 0
                 }
            self.players.append(player_info)
            self.console_channel[player.channel] = player_info
        else:
            self.console("Player limit reached!")

    def send_message(self, player, message):
        result = player["player"].send_message(message)
        if inspect.isawaitable(result):
            asyncio.get_event_loop().create_task(result)
            # asyncio.get_event_loop().run_until_complete(result)

    def ask_response(self, player, prompt):
        result = player["player"].get_response(prompt)
        if inspect.isawaitable(result):
            print("Awaiting task")
            loop = asyncio.get_event_loop()
            task = loop.create_task(result)
            loop.run_until_complete(task)
            result = task.result()

        return result

    def send_image(self, player, path):
        result = player["player"].display_image(path)
        if inspect.isawaitable(result):
            asyncio.get_event_loop().create_task(result)
class Player:
    def __init__(self, name):
        self.name = name
        self.channel = "stdout"

    def get_response(self, prompt=None):
        pass

    def send_message(self, message):
        print(message)

    def display_image(self, path):
        img = Image.open(path)
        img.show()


class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.prompt = f"{name} enters:"

    def get_response(self, prompt=None):
        if prompt is None:
            prompt = self.prompt
        return input(prompt)


class Random_Player(Player):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.action_space = None

    def send_message(self, message):
        if type(message) == dict:
            self.action_space = message
        else:
            print(message)

    def get_response(self, prompt=None):
        if self.action_space is None:
            return "check"
        else:
            print(list(self.action_space.keys()))
            c1 = np.random.choice(list(self.action_space.keys()))
            while len(self.action_space[c1]) == 0:
                c1 = np.random.choice(list(self.action_space.keys()))
            c2 = np.random.choice(list(self.action_space[c1]))
            self.action_space = None
            return ' '.join([c1, c2])



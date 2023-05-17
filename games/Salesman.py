from .game import Game, Player
import numpy as np
import matplotlib.pyplot as plt


class Node:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.connections = dict()

    def connect(self, node):
        self.connections[node.name] = node


class Graph:
    def __init__(self, values, mt=None):
        pass


class Salesman(Game):
    def __init__(self):
        super().__init__()
        self.n_points = 10
        self.name = "Traveling_Salesman"
        self.poses = np.random.uniform(-1, 1, (self.n_points, 2))

    def initialize(self, player):
        player["status"] = "playing"
        player["score"] = 0
        player["values"] = np.array([1 for i in range(self.n_points)])
        player["pos"] = 0
        player["history"] = [self.poses[0]]

    def traverse(self, player, pos):
        dist = np.sum((self.poses[pos] - self.poses[player["pos"]]) ** 2) ** 0.5
        player["pos"] = pos
        player["score"] -= dist + 1
        player["values"][pos] = 0
        player["history"].append(self.poses[pos])

    def take_turn(self, player):
        response = player["player"].get_response()
        response = int(response)
        self.traverse(player, response)
        if np.sum(player["values"]) == 0:
            player["status"] = "finished"

    def display(self, player, show=False, save=False):
        self.screen = plt.figure()
        ax = self.screen.add_subplot()
        ax.scatter(self.poses[:, 0], self.poses[:, 1])
        ax.plot(*np.stack(player["history"], 1))
        for i, pos in enumerate(self.poses):
            ax.text(pos[0] + 0.02, pos[1] + 0.02, f'{i}')
        if show:
            self.screen.show()
        if save:
            self.screen.savefig(f"{self.name}.png")
        return self.screen

    def play(self):
        if len(self.players) == 0:
            print("No player")
            return
        for player in self.players:
            self.initialize(player)
            while player["status"] == "playing":
                self.display(player, save=True)
                self.take_turn(player)


            print(f"Total Score: {player['score']}")

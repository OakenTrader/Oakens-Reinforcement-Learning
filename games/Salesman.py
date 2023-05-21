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
        player["values"][0] = 0
        player["history"] = [self.poses[0]]

    def distance(self, pos1, pos2):
        return np.linalg.norm(pos1 - pos2)

    def score(dist, value):
        return value - dist
        
    
    def traverse(self, player, pos):
        dist = self.distance(self.poses[pos], self.poses[player["pos"]])
        player["pos"] = pos
        player["score"] += self.score(dist, player["values"][pos])
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

class Salesman_RL(Salesman):
    def __init__(self):
        super().__init__()
        self.states = None
        self.encoder = dict()

    def get_action_space(self):
        return np.arange(0,self.n_points)
    
    def create_table(self):
        n = self.n_points
        return np.zeros(((2 ** n) * n, n))

    def state_encoding(self, state, action):
        def encode(pos, mark):
            ncp = 0
            for i,m in enumerate(mark):
                ncp += 2 ** i * m
            ncp += (pos) * 2 ** (len(mark))
            self.encoder[mark][pos] = ncp
        mark, pos = state
        mark = tuple(mark)
        encoder = self.encoder
        if mark in encoder.keys():
            if pos not in encoder[mark]:
                encode(pos, mark)
        else:
            self.encoder[mark] = dict()
            encode(pos, mark)
            
        return encoder[mark][pos], action


    def transition(self, state, action):
        mark, pos = state
        mark_new = mark.copy()
        mark_new[action] = 0
        new_pos = action
        new_state, _ = self.state_encoding(mark_new, new_pos, action)
        trans_prob = dict()
        trans_prob[new_state] = {"prob": 1, "new_pos":action, "new_mark":mark_new}
        return trans_prob

    def reward(self, state, action):
        mark, pos = state
        trans_prob = self.transition(mark, pos, action)
        reward = 0
        for state in trans_prob:
            new_pos = state["new_pos"]
            new_mark = state["new_mark"]
            dist = self.distance(pos, new_pos)
            score = np.sum(np.abs(mark - new_mark))
            reward += state["prob"] * (score - dist)
        return reward
        
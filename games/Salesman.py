from game import Game, Player
import numpy as np
import matplotlib.pyplot as plt

class Node:
  def __init__(self, name, value):
    self.name = name
    self.value = value
    self.connections = dict()

  def connect(self,node):
    self.connections[node.name] = node

class Graph:
  def __init__(self, values, mt=None):
    pass

class Salesman(Game):
  def __init__(self):
    super().__init__()
    self.n_points = 10
    self.name = "Traveling_Salesman"
    self.poses = np.random.uniform(-1,1,(self.n_points, 2))
    self.values = np.array([1 for i in range(self.n_points)])
    self.score = 0
    self.pos = 0
    self.history = [self.poses[0]]

  def initialize(self, player):
    self.values = np.array([1 for i in range(self.n_points)])
    self.score = 0
    self.pos = 0
    self.history = [self.poses[0]]

  def traverse(self, pos):
    dist = np.sum((self.poses[pos] - self.poses[self.pos]) ** 2) ** 0.5
    self.pos = pos
    self.score -= dist + 1
    self.values[pos] = 0
    self.history.append(self.poses[pos])


  def take_turn(self, player):
    response = player.get_response()
    response = int(response)
    self.traverse(response)
    if np.sum(self.values) == 0:
      self.winner = self.players[0]

  def display(self, show=False, save=False):
    self.screen = plt.figure()
    ax = self.screen.add_subplot()
    ax.scatter(self.poses[:,0], self.poses[:, 1])
    print(self.history)
    ff = np.stack(self.history)
    print(ff)
    ax.plot(*np.stack(self.history, 1))
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
      self.score = 0
      player["status"] = "playing"
      while player["status"] == "playing":
        self.take_turn(player)
        self.display()
      
      print(f"Total Score: {self.score}")

      
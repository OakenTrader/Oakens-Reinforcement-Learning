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
  def __init__(self, player: Player):
    super().__init__()
    points = 10
    self.name = "Traveling_Salesman"
    self.poses = np.random.uniform(-1,1,(points, 2))
    self.values = np.array([1 for i in range(points)])
    self.score = 0
    self.pos = 0
    self.add_player(player)
    self.winner = None
    self.screen = None
    self.history = [self.poses[0]]

  def traverse(self, pos):
    dist = np.sum((self.poses[pos] - self.poses[self.pos]) ** 2) ** 0.5
    self.pos = pos
    self.score -= dist + 1
    self.values[pos] = 0
    self.history.append(self.poses[pos])
    self.screen = plt.figure()
    ax = self.screen.add_subplot()
    ax.scatter(self.poses[:,0], self.poses[:, 1])
    print(self.history)
    ff = np.stack(self.history)
    print(ff)
    ax.plot(*np.stack(self.history, 1))

  def take_turn(self):
    player = self.players[0]["player"]
    response = player.get_response()
    response = int(response)
    self.traverse(response)
    if np.sum(self.values) == 0:
      self.winner = self.players[0]

  def display(self, show=True, save=True):
    if show:
      self.screen.show()
    if save:
      self.screen.savefig(f"{self.name}.png")
    return self.screen

  def play(self):
    while self.winner is None:
      self.take_turn()
      self.display()
    print(f"Total Score: {self.score}")

      
import numpy as np
import matplotlib.pyplot as plt
from ..game import Game, Player
import matplotlib.pylab as pl
import time as time
from copy import deepcopy
import pandas as pd


class Node:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.links = []

    def traverse(self, v):
        variance = 2
        direction = int(v * len(self.links) * variance) % len(self.links)
        return self.links[direction]

    def linkin(self, link):
        for l in self.links:
            if link[0] == l[0]:
                l[1] = link[1]
                return
        self.links.append(link)

    def unlinkin(self, link):
        for i, l in enumerate(self.links):
            if link[0] == l[0]:
                del self.links[i]
                break


class Hub(Node):
    def __init__(self, name, pos, value, roads=None):
        super().__init__(name, value)
        self.pos = pos
        self.state = value
        if roads is not None:
            self.build_roads(roads)

    def get_links(self):
        for link in self.links:
            print(f"{self.name} {self.pos} -", link[0].name, link[0].pos, link[1])

    def build_road(self, link):
        dist = np.sum((link.pos - self.pos) ** 2) ** 0.5
        self.linkin([link, dist])
        link.linkin([self, dist])

    def build_roads(self, links):
        for link in links:
            self.build_road(link)

    def gather(self):
        value = self.state
        if self.state > 0:
            self.state = 0
        else:
            self.state -= 0.01
        return value


class Village:
    def __init__(self, hubs, initial=0):
        self.hubs = hubs
        self.start = hubs[initial]

    def get_links(self):
        for hub in self.hubs:
            hub.get_links()

    def plot_city(self, show=True):
        fig, ax = plt.subplots()
        for hub in self.hubs:
            for link in hub.links:
                line = np.stack([hub.pos, link[0].pos], axis=1)
                ax.plot(*line, color="black", zorder=0)
            ax.scatter(*hub.pos, color="blue", zorder=1, s=hub.value * 100)
        if show:
            plt.show()
        return fig, ax

    def plot_line(self, route, show=True):
        fig, ax = self.plot_city(show=False)
        place = self.start
        poses = [place.pos]
        for v in route:
            place, dist = place.traverse(v)
            poses.append(place.pos)
        poses = np.stack(poses, axis=1)

        ax.plot(*poses, color='red', zorder=10)
        if show:
            plt.show()

        return fig

    def restore_state(self):
        for hub in self.hubs:
            hub.state = hub.value

    def get_route(self, route, start=None):
        place = start
        if start is None:
            place = self.start
        places = []
        for v in route:
            place, dist = place.traverse(v)
            places.append(place)
        return places


class Rect_Village(Village):
    def __init__(self, width, height, value_func, initial=0):
        self.shape = (height, width)
        hubs = self.construct(value_func)
        super().__init__(hubs, initial)

    def construct(self, value_func):
        height, width = self.shape
        hubs = [[] for i in range(height)]

        for i in range(height):
            for j in range(width):
                hub = Hub(f"{i}_{j}", np.array([j, i]), value_func())
                hubs[i].append(hub)

        for i in range(height):
            for j in range(width):
                num = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
                roads = [1 for i in range(num)] + [0 for i in range(4 - num)]
                np.random.shuffle(roads)

                if i > 0 and roads[0] == 1:
                    hubs[i][j].build_road(hubs[i - 1][j])
                if i < height - 1 and roads[1] == 1:
                    hubs[i][j].build_road(hubs[i + 1][j])
                if j > 0 and roads[2] == 1:
                    hubs[i][j].build_road(hubs[i][j - 1])
                if j < width - 1 and roads[3] == 1:
                    hubs[i][j].build_road(hubs[i][j + 1])

        if len(hubs[0][0].links) == 0:
            hubs[0][0].build_road(hubs[0][1])
            hubs[0][0].build_road(hubs[1][0])

        hubs_flat = []
        for row in hubs:
            hubs_flat += row

        return hubs_flat

def get_point(p):
    def point():
        a = np.random.uniform(0, 1)
        if a < p:
            return 1
        return 0
    return point


village = Rect_Village(20,10,get_point(0.1))
village.plot_city()

class Maze_Runner_Board:

    action_space = [0,1,2,3]
    def __init__(self, maze):
        self.maze = maze



class Main(Game):

    def __init__(self):
        super().__init__()
        self.name = "Splendor"
        self.player_limit = 1
        self.min_players = 1
        self.turn_limit = 50
        self.board = None
        self.current_player = None
        self.width = 20
        self.length = 20
        self.value_func = get_point(0.1)

    def initialize(self):
        if self.board is None:
            self.board = Rect_Village(self.width, self.length, self.value_func)
        for player in self.players:
            player["position"] = (0, 0)
        self.current_player = np.random.choice(self.players)

    def take_turn(self):
        player = self.current_player
from .game import Game, Player
import numpy as np
import matplotlib.pyplot as plt


class TicTacToe(Game):
    def __init__(self):
        super().__init__()
        self.board = np.zeros((3, 3))
        self.filters = np.zeros((8, 3, 3))
        self.set_filters()
        self.turn = np.random.randint(2)

    def set_filters(self):
        for i in range(3):
            for j in range(3):
                self.filters[j][i][j] = 1
                self.filters[j + 3][j][i] = 1
            self.filters[6][i][i] = 1
            self.filters[7][2 - i][i] = 1

    def initialize(self, player):
        player["status"] = "playing"

    def check(self):
        result = self.board[np.newaxis, :] * self.filters
        print(result)
        result = np.sum(result, (1, 2))
        print(result)
        if 3 in result:
            print("Player 1 wins")
            self.winner = self.players[0]
        elif -3 in result:
            print("Player 2 wins")
            self.winner = self.players[1]

    def take_turn(self):
        player = self.players[self.turn]
        valid_move = False
        while not valid_move:
            response = player["player"].get_response()
            response = response.split(" ")
            response = [int(x) for x in response]
            if len(response) == 1:
                response = response[0]
                pos = (response // 3, response % 3)
            else:
                pos = (response[0], response[1])
            if self.board[pos[0]][pos[1]] == 0:
                valid_move = True
                self.board[pos[0]][pos[1]] = (-1) ** self.turn
            else:
                print("Invalid Move")
        self.turn = (self.turn + 1) % 2

    def display(self, show=False, save=False):
        self.screen = plt.figure()
        ax = self.screen.add_subplot()
        ax.plot([-1, -1], [-3, 3], color="black")
        ax.plot([-3, 3], [-1, -1], color="black")
        ax.plot([1, 1], [-3, 3], color="black")
        ax.plot([-3, 3], [1, 1], color="black")
        for i in range(9):
            pos = self.board[i // 3][i % 3]
            x = 2 * (i % 3 - 1)
            y = 2 * (1 - i // 3)
            if pos == 1:
                ax.scatter(x, y, color='blue', s=10, marker='o')
            elif pos == -1:
                ax.scatter(x, y, color='red', s=10, marker='x')

        if show:
            plt.show()
        if save:
            self.screen.savefig('TicTacToe.png')

    def play(self):
        if len(self.players) == 0:
            print("No player")
            return
        for player in self.players:
            self.initialize(player)
        while self.winner is None:
            self.display(save=True)
            self.take_turn()
            self.check()


from ..game import Game, Player
import numpy as np
import pandas as pd
from PIL import ImageDraw, ImageFont, Image
import pathlib

def generate_permutation():
    permutations = set()
    for i in range(5):
        for j in range(i + 1, 5):
            for k in range(j + 1, 5):
                permutations.add(frozenset({i, j, k}))
    return permutations
class Splendor_Board:
    color_code = {'White': '#FFFFFF', 'Black': '#6E260E', 'Red': '#C41E3A', 'Green': '#008000', 'Blue': '#0047AB',
                  4: '#FFFFFF', 0: '#6E260E', 3: '#C41E3A', 2: '#008000', 1: '#0047AB'}
    colors = {'Black': 0, 'Blue': 1, 'Green': 2, 'Red': 3, 'White': 4,
                   0: 'Black', 1: 'Blue', 2: 'Green', 3: 'Red', 4: 'White',
                   'black': 0, 'blue': 1, 'green': 2, 'red': 3, 'white': 4,
                   "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, }
    action_space = {
        'pick': {frozenset({i}) for i in range(5)}.union(generate_permutation()),
        'buy': {(i,j) for i in range(3) for j in range(4)},
        'reserve': {(i,j) for i in range(3) for j in range(4)},
        'give_back': {(i,) for i in range(6)}.union({(i,j) for i in range(6) for j in range(6)})
        .union({(i,j) for i in range(6) for j in range(6)}).union({(i,j,k) for i in range(6) for j in range(6) for k in range(6)})
    }

    def __init__(self, game):
        self.game = game
        script_path = pathlib.Path(__file__)
        script_dir = script_path.parent
        df = pd.read_csv(f'{script_dir}/Splendor Cards.csv', delimiter=',')
        df1, df2, df3 = df[df['Level'] == 1], df[df['Level'] == 2], df[df['Level'] == 3]
        df1 = [list(df1.iloc[i]) for i in range(len(df1))]
        df2 = [list(df2.iloc[i]) for i in range(len(df2))]
        df3 = [list(df3.iloc[i]) for i in range(len(df3))]

        nobles_df = pd.read_csv(f'{script_dir}/Nobles.csv', delimiter=',')
        self.nobles = list(nobles_df.to_numpy())
        np.random.shuffle(self.nobles)
        self.nobles = self.nobles[:len(self.game.players) + 1]


        for dfi in [df1, df2, df3]:
            for di in dfi:
                di[1] = self.colors[di[1]]

        np.random.shuffle(df1)
        np.random.shuffle(df2)
        np.random.shuffle(df3)
        self.shown = [df1[-4:], df2[-4:], df3[-4:]]
        self.decks = [df1[:-4], df2[:-4], df3[:-4]]

        self.n_gems = {2: 4, 3: 5, 4: 7}[len(self.game.players)]
        self.gems = np.array([self.n_gems for i in range(5)], dtype=np.int32)
        self.gold = 5

    def deal(self):
        for i, row in enumerate(self.shown):
            dealt = 0
            for j, r in enumerate(row):
                if r is None and len(self.decks[i]) > 0:
                    dealt += 1
                    self.shown[i][j] = self.decks[i][-dealt]
            if dealt > 0:
                self.decks[i] = self.decks[i][:-dealt]

    def check_pick3(self, player, index):
        for i in index:
            if self.gems[i] == 0:
                return False
        return True

    def pick3(self, player, index):
        check = self.check_pick3(player, index)
        if check:
            for i in index:
                self.gems[i] -= 1
                player["gems"][i] += 1
        return check

    def check_pick2(self, player, index):
        return self.gems[index] < 4

    def pick2(self, player, index):
        if not self.check_pick2(player, index):
            return False
        else:
            self.gems[index] -= 2
            player["gems"][index] += 2
            return True

    def check_buy(self, player, index):
        if index[0] > 2 or index[1] > 3:
            return False
        gems = np.array([i for i in player["gems"]])
        card = self.shown[index[0]][index[1]]
        if card is None:
            return False
        back = np.zeros(5, dtype=np.int32)
        lack = 0
        for i, (gem, cost) in enumerate(zip(gems, card[3:])):
            lack += max(cost - gem, 0)
            gems[i] = max(gem - cost, 0)
            back[i] += max(gem - cost, 0)
        if lack > player["coins"]:
            return False
        return True

    def buy(self, player, index):
        if index[0] > 2 or index[1] > 3:
            return False
        gems = np.array([i for i in player["gems"]])
        card = self.shown[index[0]][index[1]]
        if card is None:
            return False
        back = np.zeros(5, dtype=np.int32)
        lack = 0
        for i, (gem, cost) in enumerate(zip(gems, card[3:])):
            lack += max(cost - gem, 0)
            gems[i] = max(gem - cost, 0)
            back[i] += max(gem - cost, 0)
        if lack > player["coins"]:
            return False
        player["coins"] -= lack
        player["gems"] = gems
        player["owned"][card[1] - 1].append(card)
        player["score"] += card[2]
        self.gems += back
        self.gold += lack
        self.shown[index[0]][index[1]] = None
        return True

    def check_reserve(self, player, index):
        card = self.shown[index[0]][index[1]]
        if card is None:
            return False
        if len(player["reserved"]) >= 3:
            return False
        return True

    def reserve(self, player, index):
        if not self.check_reserve(player, index):
            return False
        player["reserved"].append(self.shown[index[0]][index[1]])
        self.shown[index[0]][index[1]] = None
        if self.gold > 0:
            self.gold -= 1
            player["coins"] += 1
        return True

    def check_give_back(self, player, index):
        old_gems = np.concatenate([np.copy(player["gems"]), player["coins"]])
        giving = np.zeros(6)
        for i in index:
            giving[i] += 1
        new_gems = old_gems - giving
        for i in new_gems:
            if i < 0:
                return False
        return True

    def give_back(self, player, index):
        old_gems = np.concatenate([np.copy(player["gems"]), player["coins"]])
        giving = np.zeros(6)
        for i in index:
            giving[i] += 1
        new_gems = old_gems - giving
        for i in new_gems:
            if i < 0:
                return False
        self.gems += giving[:-1]
        self.gold += giving[-1]
        player["gems"] = new_gems[:-1]
        player["coins"] -= giving[-1]
        return True

    def check_available(self, player):
        picks = dict()
        for index in Splendor_Board.action_space['pick']:
            index = list(index)
            if len(index) == 1:
                picks[tuple(index)] = self.check_pick2(player, index[0])
            else:
                picks[tuple(index)] = self.check_pick3(player, index)
        picks = [' '.join([f"{j}" for j in i]) for i in picks if picks[i]]
        buys = dict()
        for index in Splendor_Board.action_space['buy']:
            buys[tuple(index)] = self.check_buy(player, index)
        buys = [' '.join([f"{j}" for j in i]) for i in buys if buys[i]]
        reserves = dict()
        for index in Splendor_Board.action_space['reserve']:
            reserves[tuple(index)] = self.check_reserve(player, index)
        reserves = [' '.join([f"{j}" for j in i]) for i in reserves if reserves[i]]
        return {'pick': picks, 'buy': buys, 'reserve': reserves}



    def award(self, player):
        for a, noble in enumerate(self.nobles):
            win = True
            if noble is not None:
                for i, (n, p) in enumerate(zip(noble, player["owned"])):
                    if len(p) < n:
                        win = False
                        break
                if win:
                    player["nobles"].append(noble)
                    self.nobles[a] = None
                    player["score"] += 3

    def draw_card(self, drawer: ImageDraw, pos, card):
        font1 = ImageFont.truetype('assets/arial.ttf', 40)
        font2 = ImageFont.truetype('assets/arial.ttf', 100)
        dx, dy = 200, 200
        sx, sy = 40, 200
        p1, p2, p3, p4 = (pos[0], pos[1]), (pos[0] + dx, pos[1]), (pos[0] + dx, pos[1] + dy), (pos[0], pos[1] + dy)
        s1, s2, s3, s4 = (pos[0], pos[1]), (pos[0] + sx, pos[1]), (pos[0] + sx, pos[1] + sy), (pos[0], pos[1] + sy)
        drawer.polygon([p1, p2, p3, p4], fill=Splendor_Board.color_code[card[1]], outline='#000000')
        drawer.polygon([s1, s2, s3, s4], fill='#FFFFFF', outline='#000000')
        xt, yt = 10, 10
        for i, c in enumerate(card[3:]):
            if c > 0:
                drawer.text((pos[0] + xt, pos[1] + yt), str(c), font=font1, stroke_width=2,
                            fill=Splendor_Board.color_code[i], stroke_fill='#000000')
                yt += 40
        drawer.text((pos[0] + 100, pos[1] + 50), str(card[2]), font=font2, stroke_width=2, fill='#FFFFFF',
                    stroke_fill='#000000')

    def draw_deck(self, drawer, pos):
        font2 = ImageFont.truetype('assets/arial.ttf', 100)
        dx, dy = 200, 200
        p1, p2, p3, p4 = (pos[0], pos[1]), (pos[0] + dx, pos[1]), (pos[0] + dx, pos[1] + dy), (pos[0], pos[1] + dy)
        drawer.polygon([p1, p2, p3, p4], fill=(53, 133, 60), outline='#000000')
        drawer.text((pos[0] + 50, pos[1] + 50), str(len(self.decks[0])), font=font2, stroke_width=2, fill='#FFFFFF',
                    stroke_fill='#000000')
        pos[1] += 300
        p1, p2, p3, p4 = (pos[0], pos[1]), (pos[0] + dx, pos[1]), (pos[0] + dx, pos[1] + dy), (pos[0], pos[1] + dy)
        drawer.polygon([p1, p2, p3, p4], fill=(197, 148, 46), outline='#000000')
        drawer.text((pos[0] + 50, pos[1] + 50), str(len(self.decks[1])), font=font2, stroke_width=2, fill='#FFFFFF',
                    stroke_fill='#000000')
        pos[1] += 300
        p1, p2, p3, p4 = (pos[0], pos[1]), (pos[0] + dx, pos[1]), (pos[0] + dx, pos[1] + dy), (pos[0], pos[1] + dy)
        drawer.polygon([p1, p2, p3, p4], fill=(12, 142, 194), outline='#000000')
        drawer.text((pos[0] + 50, pos[1] + 50), str(len(self.decks[2])), font=font2, stroke_width=2, fill='#FFFFFF',
                    stroke_fill='#000000')

    def draw_coins(self, drawer, pos, color):
        font2 = ImageFont.truetype('assets/arial.ttf', 75)
        s = 150
        drawer.ellipse([pos[0], pos[1], pos[0] + s, pos[1] + s], fill=Splendor_Board.color_code[color],
                       outline='#000000', width=1)
        drawer.text((pos[0] + s / 5, pos[1] + s / 5), str(self.gems[color]), font=font2, stroke_width=2, fill='#FFFFFF',
                    stroke_fill='#000000')
        pass

    def display(self, player):
        font2 = ImageFont.truetype('assets/arial.ttf', 100)
        board = Image.new('RGB', (2000, 2500), '#FFFFFF')
        drawer = ImageDraw.Draw(board)
        cx0, cy0 = 500, 500
        dx, dy = 300, 300
        for i, row in enumerate(self.shown):
            for j, card in enumerate(row):
                if card is not None:
                    self.draw_card(drawer, [cx0 + j * dx, cy0 + i * dy], card)
        self.draw_deck(drawer, [cx0 - dx, cy0])
        for i in range(5):
            self.draw_coins(drawer, [cx0 + (i - 1) * dx, cy0 + 3 * dy], i)
        points = f"Score: {player['score']}"
        py0 = 1600
        drawer.text((100, py0), points, font=font2, stroke_width=2, fill='#FFFFFF', stroke_fill='#000000')

        for i, cards in enumerate(player["owned"]):
            for j, card in enumerate(cards):
                pos = (cx0 + dx * i, py0 + 100 * j)
                self.draw_card(drawer, pos, card)

        # ex_card = self.shown[2][2]
        # self.draw_card(drawer, [100,100], ex_card)
        filepath = f'displays/{self.game.id}_{player["id"]}_{player["Name"]}.png'
        board.save(filepath)
        return filepath


class Main(Game):
    def __init__(self):
        super().__init__()
        self.name = "Splendor"
        self.player_limit = 4
        self.min_players = 2
        self.score_limit = 15
        self.board = None
        self.current_player = None

    def initialize(self):
        self.board = Splendor_Board(self)
        self.status = "Playing"
        for player in self.players:
            player["status"] = "playing"
            player["score"] = 0
            player["reserved"] = []
            player["owned"] = [[] for i in range(5)]
            player["gems"] = np.zeros(5)
            player["coins"] = 0
            player["nobles"] = []
            player["screen"] = None
        np.random.shuffle(self.players)
        self.current_player = 0

    def take_turn(self):
        player = self.players[self.current_player]
        print(f"{player['Name']}'s turn")
        img = self.board.display(player)
        self.send_image(player, img)
        done = False
        while not done:
            action = self.ask_response(player, "Choose your action")
            action = action.split(" ")
            print(action)
            valid = True
            if action[0].lower() == 'check':
                self.send_message(player, self.board.check_available(player))
                continue
            elif action[0].lower() in ["pick"] and len(action) in [2, 4]:
                la = []
                for a in action[1:]:
                    a = a.lower()
                    if a not in ["red", "blue", "green", "white", "black"] + [f"{i}" for i in range(5)]:
                        valid = False
                        break
                    la.append(Splendor_Board.colors[a])
                if valid and len(la) == 1:
                    done = self.board.pick2(player, la[0])
                if valid and len(la) == 3:
                    done = self.board.pick3(player, la)
            elif action[0].lower() in ["buy"] and action[1].isnumeric() and action[2].isnumeric():
                index = [int(action[1]), int(action[2])]
                done = self.board.buy(player, index)
            elif action[0].lower() in ["reserve", "reserved"] and action[1].isnumeric() and action[2].isnumeric():
                index = [int(action[1]), int(action[2])]
                done = self.board.reserve(player, index)

            if not done:
                self.send_message(player, "Invalid action!")
        self.board.deal()
        # Exceeding 10 coins

        if player['coins'] + np.sum(player['gems']) > 10:

            valid = False
            while not valid:
                valid = True
                action = self.ask_response(player, f"Return {player['coins'] + np.sum(player['gems']) - 10} coins").split(" ")
                if len(action) < player['coins'] + np.sum(player['gems']) - 10:
                    valid = False
                for i, a in enumerate(action):
                    a = a.lower()
                    if a not in ["red", "blue", "green", "white", "black", "gold"]:
                        valid = False
                        break
                    if a == "gold":
                        action[i] = 5
                    else:
                        action[i] = Splendor_Board.colors[a]
                if valid:
                    valid = self.board.give_back(player, action)
                self.send_message(player, "Invalid action!")

        self.console(f"{player['Name']} completed his turn")

        if player["score"] >= 15 and self.status == "Playing":
            player["status"] = "won"
            self.console(f"{player['Name']} reached 15 score! This is the last turn.")
            self.winner = player
            self.status = "Last Turn"
        if self.status == "Last Turn" and player["score"] > self.winner["score"]:
            self.console(f"{player['Name']} won over {self.winner['Name']}!")
            self.winner = player
        if self.status == "Last Turn" and self.current_player == len(self.players) - 1:
            self.status = "Game Over"
            self.console(f"{self.winner['Name']} won!")
        self.current_player = (self.current_player + 1) % len(self.players)

    def play(self):
        self.initialize()
        while self.status != "Game Over":
            self.take_turn()

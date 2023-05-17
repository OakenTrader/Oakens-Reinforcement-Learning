import PIL
from PIL import Image
from games.Salesman import *
from games.TicTacToe import TicTacToe
from games.game import HumanPlayer

width = 400
height = 300

# img  = Image.new( mode = "RGB", size = (width, height) )
# img.show()

a = "4"
b = a.split(" ")
print(b)

player = HumanPlayer("Bob")
player2 = HumanPlayer("Mike")
# game = Salesman()
# game.add_player(player)
# game.play()
game = TicTacToe()
game.add_player(player)
game.add_player(player2)
game.play()
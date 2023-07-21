import PIL
from PIL import Image
from games.game import HumanPlayer
from games.Splendor.Splendor import Main as Splendor

width = 400
height = 300

# img  = Image.new( mode = "RGB", size = (width, height) )
# img.show()

player = HumanPlayer("Bob")
player2 = HumanPlayer("Mike")
game = Splendor()
# game.add_player(player)
# game.play()
game.add_player(player)
game.add_player(player2)
game.play()
import PIL
from PIL import Image
from Salesman import *
from game import HumanPlayer

width = 400
height = 300

img  = Image.new( mode = "RGB", size = (width, height) )
# img.show()

a = "4"
b = a.split(" ")
print(b)

player = HumanPlayer("Bob")
game = Salesman(player)
game.play()
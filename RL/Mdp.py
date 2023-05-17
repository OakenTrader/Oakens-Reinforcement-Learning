from ..games.game import Player

class MDP_State:
  def __init__(self, data):
    self.data = data
    pass


class MDP_VI(Player):
  def __init__(self, name):
    super().__init__(name)
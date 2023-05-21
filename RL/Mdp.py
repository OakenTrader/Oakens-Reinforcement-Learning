from ..games.game import Player

class MDP_State:
    def __init__(self, data):
        self.data = data
        pass


class MDP_VI(Player):
    def __init__(self, name):
        super().__init__(name)
        self.environment = None
        self.q_table = None
        self.dq = None
        self.lr = 0.1
        self.dr = 0.9

    def initialize(self):
        self.q_table = self.environment.create_table()
        self.dq = np.zeros(self.q_table.shape)

    def qtsa(self, state, action):
        st, at = self.environment.state_encoding(state, action)
        rt = self.environment.reward(state, action)
        Psa = self.environment.transition(state, action)
        S1P = []
        for st1 in Psa:
            q_next = []
            prob = Psa[st1]["prob"]
            for action1 in self.environment.get_action_space():
                state1 = (Psa[st1]["new_mark"], Psa[st1]["new_pos"])
                q_next.append(qtsa(state1, action1))
            qt1 = max(q_next) * self.dr
            S1P.append(prob * qt1)
        S1P = np.sum(S1P)
            
            
        
            
    

import logging
import random
from hmm import HMM,State
from hmm_utils import load_hmm
from quarry.data import packets

class ActionModel(object):
    def __init__(self, actions, encoder):
        """ 
        Parameters: 
        actions: List of action functions for the associated encoder
        """
        self.encoder = encoder
        self._index = 0  
        self.actions = actions
        self.stored_action = None 
        print(actions, encoder)
        self.enum_actions = dict([(i,k) for i,k in enumerate(actions)])

    def next_action(self):
        self.actions[self.enum_actions[self._index]](self.encoder) #calls action in action list
        self._index += 1 
        self._index %= len(self.actions)

    def next_actions(self, num_actions): 
        """
        Calls num_actions
        """
        for i in range(num_actions): 
            self.next_action()

class RandomActionModel(ActionModel):
    """
    Randomly Picks next action
    """
    def next_action(): 
        self._index = random.randint(0, len(self.actions))
        self.actions[self.enum_actions[self._index]]()


class HMMActionModel(ActionModel):
    def __init__(self, actions, encoder, mapping, hmm_file):
        super().__init__(actions, encoder)
        
        self.hmm = load_hmm(hmm_file)
        self.mapping = mapping
        encoder.logger.warn(mapping)
        
        #need to map sym outputs with quarry calls
    
    def next_action(self):
        if self.stored_action is None:
            raw_action = self.hmm.generate_seq(1)[0]
            #self.encoder.logger.warn(raw_action)
            #count = 0
            while raw_action not in self.mapping:
                #count += 1
                raw_action = self.hmm.generate_seq(1)[0]
                #if count > 100:
                    #self.encoder.logger.warn(f"Looping {raw_action} {self.mapping}") 

            #self.encoder.logger.warn(f"Got Action {hex(int.from_bytes(raw_action,'little'))}") 
            action = self.mapping[raw_action]
            self.stored_action = action
        else:
            action = self.stored_action 
            self.stored_action = None

        if not self.actions[action](self.encoder):
            self.stored_action = action 

class WeightedRandomActionModel(ActionModel):
    def __init__(self, actions, encoder, weights): 
        super().__init__(actions,encoder)
        self.weight_map = []
        for i,k in enumerate(weights): 
            num_occurrences = int(1000.0*weights[k]) 
            for j in range(num_occurrences):
                self.weight_map.append(i)

    def next_action(self): 
        self._index = random.randint(0, len(self.weight_map)-1)
        self._index = self.weight_map[self._index]
        self.actions[self.enum_actions[self._index]](self.encoder)
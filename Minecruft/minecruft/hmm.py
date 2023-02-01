import pickle
import random
from pprint import pprint as pp
from graphviz import Digraph
import numpy as np

class HMM(): 
    def __init__(self): 
        self.states = [] 
        self.state_mapping = {}
        self.start_state = None

    def add_state(self, state):
        for expr in state.expressions: 
            self.state_mapping[expr] = state
        self.states.append(state)
    
    def update_map(self, state, expr):
        self.state_mapping[expr] = state

    def check_unique(self): 
        expressions = {} 
        #print("Checking")
        for state in self.states: 
            #print(state.expressions)
            for expr in state.expressions: 
                if expr in expressions:
                    raise ValueError(f"Found expression {expr} twice in {state.name} and {expressions[expr].name}, {expressions[expr].expressions} \n {state.expressions}")
                expressions[expr] = state

    def save_hmm(self, savefile):
        with open(savefile, 'wb') as f:
            pickle.dump(self,f) 

    def build_transitions(self):
        trans_matrix = []
        self.rename_states()
        for state1 in self.states: 
            row = []
            for state2 in self.states: 
                row.append(0)
            trans_matrix.append(row)
        

        state_map = dict([(state.name[1:], state) for state in self.states])
        tmp_set = []
        for index,sname in enumerate(sorted(state_map.keys())):
            state = state_map[sname]
            for alpha_key in sorted(state.sym_dist.keys()):
                v = state.sym_dist[alpha_key]
                if v > 0:
                    expr = state.expressions[0]+alpha_key
                    #print(state.expressions)
                    num_iter = 0
                    full_expr =expr
                    while expr not in self.state_mapping:
                        expr = expr[1:]
                        num_iter += 1
                        if num_iter > 1: 
                            tmp_set.append(full_expr)
                            #print(state.name, expr)
                    
                    col = int(self.state_mapping[expr].name[1:])
                    trans_matrix[index][col] = 1

                    state.add_transition_state(alpha_key, self.state_mapping[expr])

        #print(set(tmp_set)) 
        trans_matrix = np.array(trans_matrix) 
        #print(trans_matrix)
        return trans_matrix

    #Could optimize search if needed
    def remove_state(self, state_name):
        for state in self.states:
            if state_name == state.name:
                self.states.remove(state)
                for expr in state.expressions: 
                    self.state_mapping.pop(expr)
                
    def remove_transients(self): 
        tmatrix = self.build_transitions()
        #Transpose 
        t_tmatrix = np.transpose(tmatrix) 
        removed = False
        
        for index, row in enumerate(t_tmatrix):  
            #If transposed col has no transitions, it is not a sink state
            if np.count_nonzero(row) == 0: 
                removed = True
                #Remove from mapping and state list
                state_name = "s"+str(index) 
                self.remove_state(state_name)
         
        #Fix state naming 

        if removed:
            self.remove_transients()

    def remove_zero_probs(self):
        for state in self.states:
            zeros_sym = []
            for sym, val in state.sym_dist.items():
                if val == 0:
                    zeros_sym.append(sym) 
            for sym in zeros_sym: 
                state.sym_dist.pop(sym)

    def rename_states(self):
        #This mangles naming, but it is not really an issue
        for index, state in enumerate(self.states):
            state.name = "s"+str(index)

    def print_dot_graph(self,name):
        dot = Digraph(comment='HMM',format='pdf')
        conn_test = []
        for state in self.states:
            #dot.node(state.name +str(state.expressions))
            dot.node(state.name) 
            for a,v in state.sym_dist.items():
                if v > 0:  
                    tmp = state.expressions[0]
                    expr = tmp+a
                    if expr not in self.state_mapping:
                        expr = expr[1:]
                    conn_test.append(expr)
                    dot.edge(state.name , self.state_mapping[expr].name, label=a+" "+f"{v:.4f}")
                    #dot.edge(state.name + str(state.expressions) , self.state_mapping[expr].name + str(self.state_mapping[expr].expressions), label=a+" "+f"{v:.2f}")
        dot.render(name) 
        
        if conn_test.sort() == list(self.state_mapping.keys()).sort():
            print("All Values accounted for") 
        else: 
            print("DANGER WILL ROBINSON")
    #Generate Sequences
    def generate_seq(self, length):
        rval = [] 
        if self.start_state is None: 
            self.start_state = random.choice(self.states)

        for i in range(length):
            sym, nstate = self.start_state.next_state()
            rval.append(sym)
            self.start_state = nstate 
        
        return rval

class State():
    def __init__(self, name, alphabet): 
        self.name = name 
        self.expressions = []  #Expr: Occurence
        self.sym_counts = {} 
        for a in alphabet: 
            self.sym_counts[a] = 0 
        self.sym_dist = {} 
        self.total_occurrences = 0
        self.next_states = {} #Dictionary of tuples
    
    def add_expr(self, expr):
        if expr not in self.expressions: 
            self.expressions.append(expr)
        
    def renormalize(self, sequence, alphabet, expr, count_table):  
        occurrence = count_table[expr]
        self.add_expr(expr)
        for a in alphabet:
            if expr+a in count_table: 
                self.sym_counts[a] += count_table[expr+a] 
                self.total_occurrences += count_table[expr+a]
        self.sym_dist = dict([k, v/self.total_occurrences] for k,v in self.sym_counts.items()) 

    def get_transition_sym(self): 
        val = random.random() 
        new_dict = {}
        for k,v in self.sym_dist.items(): 
            if v != 0: 
                new_dict[k] = v
        self.sym_dist = new_dict

        for k,v in self.sym_dist.items():
            val -= v 
            if val <= 0: 
                break
        return k

    def add_transition_state(self, sym, state): 
        self.next_states[sym] = state 

    def next_state(self):
        val = random.random()
        transition = None 

        for sym,prob in self.sym_dist.items():        
            val -= prob
            #print(sym, prob, val)
            if val <= 0:
                #print("adding ", sym)
                transition = (sym, self.next_states[sym])  
                break

        return transition

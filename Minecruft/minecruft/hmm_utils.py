import pickle
from hmm import HMM, State

def load_hmm(filename):
    with open(filename, 'rb') as f:
        g = pickle.load(f)
    return g

def compare_hmm(hmm1_name, hmm2_name): 
    hmm1 = load_hmm(hmm1_name)   
    hmm2 = load_hmm(hmm2_name)   

    s1_len = len(hmm1.states)  
    s2_len = len(hmm2.states)  

    min_len = min(s1_len, s2_len)

    for i in range(min_len):
        print(hmm1.states[i].expressions)
        print(hmm2.states[i].expressions)

    print("done")
    unmatched = []
    for state1 in hmm1.states:
        in_state = False
        for state2 in hmm2.states:
            if state1.expressions == state2.expressions:
                in_state = True
                break  
        
        if not in_state:
            unmatched.append(state1.expressions) 
        
    for expr in unmatched:
        print(expr) 
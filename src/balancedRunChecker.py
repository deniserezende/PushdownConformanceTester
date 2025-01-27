import logging

class BalancedRunChecker:
    def __init__(self, push, pop, internal, states, transitions, start_state, end_state):
        """
        Initializes vectors and transition matrix based on the automaton definition.
        """
        self.push = push
        self.pop = pop
        self.internal = internal
        self.states = states
        self.transitions = transitions
        self.indice = {state: int(state) for state in states}
       
        self.V = []
        self.In = [[] for _ in range(len(self.indice))]
        self.Out = [[] for _ in range(len(self.indice))]
        self.R = [[[] for _ in range(len(self.indice))] for _ in range(len(self.indice))]
        self.str_global = []  # Store the balanced run string

        self.si = start_state
        self.se = end_state
        
        self._initialize_vectors_()

    def _initialize_vectors_(self):
        """
        Initialize vectors based on push, pop, internal transitions, and states.
        """
        for p in self.states:
            for t in self.transitions:
                if t[0] == p:
                    if (t[1] in self.internal) and (t[3] != p) and not self.R[self.indice[t[0]]][self.indice[t[3]]]:
                        # Record internal transitions
                        self.R[self.indice[t[0]]][self.indice[t[3]]].append(f"{t[0]};{t[1]};{t[3]}")
                        self.V.append([t[0], t[3]])
                    elif t[1] in self.pop:
                        # Record output transitions
                        self.Out[self.indice[p]].append(f"{t[1]};{t[2]};{t[3]}")
                    else:
                        q = t[3]
                        # Record input transitions
                        self.In[self.indice[q]].append(f"{t[0]};{t[1]};{t[2]}")
                        for r in self.transitions:
                            if q == r[0] and (t[2] == r[2]) and (r[1] in self.pop) and (t[0] != r[3]) and not self.R[self.indice[t[0]]][self.indice[r[3]]]:
                                # Handle transitions leading to failure states
                                self.R[self.indice[t[0]]][self.indice[r[3]]].append(f"{t[1]};{r[0]};{r[0]};{r[1]}")
                                self.V.append([t[0], r[3]])

    def _get_balanced_run_string_(self, si, se, R, pu, po, inte, setofstates):
        """
        Recursive function that builds the string corresponding to a balanced run.
        """
        indice = {si: int(si), se: int(se)}  # Map states to indices
        for i in setofstates:
            if i not in (si, se):
                indice[i] = int(i)

        tripla = R[indice[si]][indice[se]]  # Get the first valid transition between si and se
        p = tripla[0].split(";")  # Parse the first valid transition

        if len(p) == 3:
            p1, p2, p3 = p
            if p2 in pu or p2 in po or p2 in inte:
                print(p2)
                self.str_global.append(p2)  # Append to global string
            elif p2 in setofstates:
                # Recursively handle transitions
                self._get_balanced_run_string_(si, p2, R, pu, po, inte, setofstates)
                self._get_balanced_run_string_(p2, se, R, pu, po, inte, setofstates)

        else:  # Handling for 4-part transition
            p1, p2, p3, p4 = p
            if p2 != p3:
                print(p1)
                self.str_global.append(p1)  # Append the first part of the transition
                self._get_balanced_run_string_(p2, p3, R, pu, po, inte, setofstates)  # Recursive call for the middle part
                print(p4)
                self.str_global.append(p4)  # Append the last part of the transition
            else:
                print(p1)
                self.str_global.append(p1)  
                print(p4)
                self.str_global.append(p4)  

        return ','.join(self.str_global)  # Join the list into a single string
    
    def check_balanced_run(self):
        """
        Main function that checks if a balanced run exists from start_state (si) to end_state (se).
        """
        while self.V and not self.R[self.indice[str(self.si)]][self.indice[str(self.se)]]:
            par = self.V.pop(0)
            p = par[0]
            q = par[1]

            for s in self.states:
                if self.R[self.indice[s]][self.indice[p]] and s != q and not self.R[self.indice[s]][self.indice[q]]:
                    # Extend paths from state s to q through p
                    self.R[self.indice[s]][self.indice[q]].append(f"{s};{p};{q}")
                    self.V.append([s, q])

            for t in self.states:
                if self.R[self.indice[q]][self.indice[t]] and p != t and not self.R[self.indice[p]][self.indice[t]]:
                    # Extend paths from p to t through q
                    self.R[self.indice[p]][self.indice[t]].append(f"{p};{q};{t}")
                    self.V.append([p, t])

            for tr1 in self.In[self.indice[p]]:
                s, a, Z = tr1.split(";")
                for tr2 in self.Out[self.indice[q]]:
                    b, W, t = tr2.split(";")
                    if Z == W and s != t and not self.R[self.indice[s]][self.indice[t]]:
                        # Create new transitions based on input-output matching
                        self.R[self.indice[s]][self.indice[t]].append(f"{a};{p};{q};{b}")
                        self.V.append([s, t])

        try:
            if len(self.R[self.indice[str(self.si)]][self.indice[str(self.se)]]) == 0:
                return False, ""
            else:
                mystring = "Um caso de teste que mostra essa condição é: " + \
                           self._get_balanced_run_string_(str(self.si), str(self.se), 
                                                           self.R, 
                                                           self.push,
                                                           self.pop,
                                                           self.internal,
                                                           self.states)
                return True, mystring
        except Exception as e:  # Catch specific exceptions for better debugging
            logging.error(f"Error during balanced run check: {e}")
            return True, "Problema de sincronização dos modelos"

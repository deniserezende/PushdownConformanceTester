from copy import deepcopy
from iovpts import IOVPTS
import logging

class FaultModel:
    def __init__(self, iovpts: IOVPTS):
        self.iovpts = iovpts
        self.setofstates_fail = deepcopy(iovpts.states)
        self.setofstates_fail.append("fail")  # Adiciona o estado de falha ao conjunto de estados
        self.Z = iovpts.stack_symbols[0]
        self.setofstacks = deepcopy(iovpts.stack_symbols)
        self.setofstacks.append("*")  # Adiciona símbolo de pilha vazio
        self.indice = {state: idx for idx, state in enumerate(self.setofstates_fail)}
        self.static_trans = deepcopy(iovpts.transitions)
        self.fault_trans = deepcopy(self.static_trans)  # Inicializa transições de falha

    def generate_fault_model(self):
        setofstates = deepcopy(self.iovpts.states)
        
        for state in setofstates:
            set_lu = deepcopy(self.iovpts.output)  # Conjunto de ações de saída disponíveis
            set_trans = deepcopy(self.static_trans)  # Transições estáticas
            
            for transitions in set_trans:  
                from_state, event, stack_symbol, to_state = transitions

                if from_state == state:
                    set_stack = deepcopy(self.setofstacks)

                    if event in set_lu:
                        if event in self.iovpts.returns:
                            set_lu.remove(event)
                            set_stack.remove(stack_symbol)

                            for W in set_stack:
                                trt = (from_state, event, W, 'fail')  # Cria transição para estado de falha
                                self.fault_trans.append(trt)

                        elif event in self.iovpts.calls or event in self.iovpts.internal:
                            set_lu.remove(event)

            if set_lu:  # Se ainda houver ações de saída disponíveis
                for a in set_lu:
                    if a in self.iovpts.calls:
                        trt = (state, a, self.setofstacks[0], 'fail')
                        self.fault_trans.append(trt)
                    elif a in self.iovpts.returns:
                        for W in self.setofstacks:
                            trt = (state, a, W, 'fail')
                            self.fault_trans.append(trt)
                    elif a in self.iovpts.internal:
                        trt = (state, a, '@', 'fail')
                        self.fault_trans.append(trt)    
                                                
        return [self.setofstates_fail, self.fault_trans]  # Retorna estados e transições de falha

    def save_faultmodel_info_to_list(self, list):
        faultstates = self.setofstates_fail
        faulttrans = self.fault_trans
        list.append("The set of states for the fault model are:")
        list.append(faultstates)
        list.append("The set of transitions for the fault model are:")
        
        trans_list = []
        for transition in faulttrans:  
            trans_list.append(f"t{len(trans_list)}: {transition[0]} --{transition[1]}/{transition[2]}-> {transition[3]}")
        
        for trans in trans_list:
            list.append(trans)
        
        return list

import logging
import pandas as pd
from copy import deepcopy
from iovpts import IOVPTS
from faultModel import FaultModel

class Product:
    def __init__(self, fault_model: FaultModel, implementation: IOVPTS):
        self.fault_model = fault_model  
        self.implementation = implementation  
        self.productComputed = False  
        self.prod_setofstates = None  
        self.prod_setoftrans = None  
        self.prod_setofstacks = None  
        self.prod_pu = None  
        self.prod_po = None  
        self.prod_inte = None  
    
    def _update_states_(self, transition1, transition2, prod_setofstates):
        """Atualiza o conjunto de estados com base nas transições fornecidas."""
        source = [transition1[0], transition2[0]]  
        target = [transition1[3], transition2[3]]  

        if not prod_setofstates:
            prod_setofstates.append(source)  
            if source != target:
                prod_setofstates.append(target)  
        else:
            if source not in prod_setofstates:
                prod_setofstates.append(source)  
            if target not in prod_setofstates:
                prod_setofstates.append(target)  

        return source, target
    
    def _update_transitions_(self, transition1, transition2, pu1, po1, inte1, prod_pu, prod_po, prod_inte, source, target):
        """Atualiza o conjunto de transições com base nas transições e conjuntos de estados."""
        newstack = [transition1[2], transition2[2]]  

        if transition1[1] in pu1 or transition1[1] in inte1:
            if transition1[1] in pu1:
                prod_pu.append(transition1[1])  
            if transition1[1] in inte1:
                prod_inte.append(transition1[1])  
            
            t = [source, transition1[1], newstack, target]  
            self.prod_setoftrans.append(t)  

        elif transition1[1] in po1:
            prod_po.append(transition1[1])  
            
            if transition1[2] != '*' and transition2[2] != '*':
                t = [source, transition1[1], newstack, target]  
                self.prod_setoftrans.append(t)
            elif transition1[2] == '*' and transition2[2] == '*':
                t = [source, transition1[1], newstack, target]  
                self.prod_setoftrans.append(t)
        
    def compute_product(self):
        """Computa o produto entre o modelo de falhas e a implementação."""
        pu1 = self.fault_model.iovpts.calls  
        po1 = self.fault_model.iovpts.returns  
        inte1 = self.fault_model.iovpts.internal  
        setoftrans1 = self.fault_model.fault_trans  

        pu2 = self.implementation.calls  
        po2 = self.implementation.returns  
        inte2 = self.implementation.internal  
        setoftrans2 = self.implementation.transitions  

        prod_pu = []  
        prod_po = []  
        prod_inte = []  
        prod_setofstacks = []  
        prod_setofstates = []  
        self.prod_setoftrans = []  

        logging.info(f"setoftrans1={setoftrans1}")  
        logging.info(f"setoftrans2={setoftrans2}")  
        
        df = pd.DataFrame(setoftrans2, columns=['state', 'event', 'stack_symbol', 'next_state'])  
        
        for transition in setoftrans1:  
            filtered_df = df[df['event'] == transition[1]] 
            filtered_items = list(filtered_df.itertuples(index=False, name=None))  

            for transition2 in filtered_items:  
                newstack = [transition[2], transition2[2]]  

                if newstack not in prod_setofstacks:  
                    prod_setofstacks.append(newstack)  

                source, target = self._update_states_(transition, transition2, prod_setofstates)  
                self._update_transitions_(transition, transition2, pu1, po1, inte1, prod_pu, prod_po, prod_inte, source, target)  

        # Armazenando o resultado no atributo da classe 
        self.productComputed = True  
        self.prod_setofstates = prod_setofstates  
        self.prod_setofstacks = prod_setofstacks  
        self.prod_pu = prod_pu  
        self.prod_po = prod_po  
        self.prod_inte = prod_inte  

    def save_product_info_to_list(self, list):
        """Salva informações sobre estados e transições do produto em uma lista."""
        list.append("\nEstados para FM x IUT:")
        list.append(self.prod_setofstates)  
        list.append("\nTransições para FM x IUT:")
        list.append(self.prod_setoftrans)  

    
def compute_estados(product: Product, specificationIOVPTS: IOVPTS, implementationIOVPTS: IOVPTS):
    """Computa os estados resultantes a partir dos estados do produto e das especificações."""
    newstates = deepcopy(product.prod_setofstates)  
    inicial1 = specificationIOVPTS.initial_state  
    inicial2 = implementationIOVPTS.initial_state  
    estados = {}  
    s = 1  
    savenewstates = deepcopy(newstates)  
    f = len(savenewstates) - 1  
    
    while newstates:  
        par = newstates[0] 
        
        if (par[0] == inicial1 and par[1] == inicial2):  
            estados[par[0], par[1]] = 0  
            newstates.remove(par) 
            
        else: 
            if (par[0] == 'fail'): 
                estados[par[0], par[1]] = f 
                newstates.remove(par) 
                
            elif par[1] == par[0]: 
                estados[par[0], par[1]] = s 
                newstates.remove(par) 
                s += 1 

            else: 
                estados[par[0], par[1]] = s 
                s += 1 
                newstates.remove(par)

    if s < f: 
        for fail in savenewstates: 
            if (fail[0] == 'fail') or (fail[1] == 'fail'): 
                estados[fail[0], fail[1]] = s  

    return estados  

def compute_pilha(product: Product):
    """Computa a pilha resultante a partir das pilhas do produto."""
    newstacks = product.prod_setofstacks
    pilha = {}
    i = 0  
    
    while newstacks: 
        par_pilha = newstacks.pop(0) 
        
        if par_pilha not in newstacks: 
            pilha[par_pilha[0], par_pilha[1]] = i 
            i += 1  
    
    return pilha  

def compute_transicoes(product: Product, estados, pilha):
    """Computa as transições resultantes a partir das transições do produto e dos estados."""
    newtrans = product.prod_setoftrans
    novosestados = []
    transicoes = []  
    
    logging.info(f"newtrans={newtrans}") 
    logging.info(f"estados={estados}") 
    
    for trans in newtrans: 
        sq = trans[0]
        pr = trans[3]
        
        novoestado1 = estados[sq[0], sq[1]]
        novoestado2 = estados[pr[0], pr[1]]
        
        if novoestado1 not in novosestados: 
            novosestados.append(novoestado1)
        
        if novoestado2 not in novosestados: 
            novosestados.append(novoestado2)
        
        novatrans = [str(novoestado1), trans[1], str(pilha[(trans[2][0], trans[2][1])]), str(novoestado2)] 
        transicoes.append(novatrans)

    str_estados = [str(s) for s in novosestados]
    
    return novosestados, transicoes, str_estados  

def save_dictionaries_info_to_list(estados, pilha, str_estados, transicoes, list):
    """Salva informações sobre estados e transições em uma lista formatada."""
    list.append("\nDicionários dos estados do produto:")
    list.append(estados)  
    list.append("\nDicionários dos símbolos de pilha do produto:")
    list.append(pilha)  
    list.append("\nEstados do produto por índices:")
    list.append(str_estados)  
    
    list.append("\nTransições do produto por índices:")
    
    for tr in transicoes:
        list.append("t"+str(transicoes.index(tr))+": "+tr[0]+" --"+tr[1]+"/"+tr[2]+"-> "+tr[3]) 

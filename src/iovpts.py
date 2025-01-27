import logging

class IOVPTS:
    def __init__(self):
        self.calls = []  # Ações CALL (push)
        self.returns = []  # Ações RETURN (pop)
        self.internal = []
        self.input = []
        self.output = []
        self.stack_symbols = []
        self.states = []
        
        self.initial_state = None
        self.transitions = []

    def add_state(self, state):
        """Adiciona um estado ao conjunto de estados."""
        self.states.append(state)

    def set_initial_state(self, state):
        """Define o estado inicial do modelo."""
        self.initial_state = state

    def add_transition(self, from_state, action, stack_symbol, to_state):
        """Adiciona uma transição ao modelo."""
        self.transitions.append((from_state, action, stack_symbol, to_state))

    def save_iovpts_info_to_list(self, list):    
        list.append(f"Push symbols = {self.calls}")
        list.append(f"Pop symbols = {self.returns}")
        list.append(f"Internal symbols = {self.internal}")
        list.append(f"Input symbols = {self.input}")
        list.append(f"Output symbols = {self.output}")
        list.append(f"Stack symbols = {self.stack_symbols}")
        list.append(f"States = {self.states}\n")
        list.append(f"Transitions:")
        
        # Adiciona informações sobre transições à lista
        for transition_count, (from_state, action, stack_symbol, to_state) in enumerate(self.transitions):
            list.append(f"t{transition_count}: {from_state} --{action}/{stack_symbol}-> {to_state}")

def read_iovpts_file(file):
    """Lê um arquivo IOVPTS e retorna um objeto IOVPTS populado com os dados do arquivo."""
    logging.info(f'Began reading iovpts file')
    iovpts = IOVPTS()
    
    content = file.read().decode("utf-8")  # Lê e decodifica o conteúdo do arquivo
    lines = [line.strip() for line in content.splitlines()]
    logging.info(lines)
    
    # Preenche os atributos do objeto IOVPTS com os dados lidos do arquivo
    iovpts.calls = lines[0].split(',') if lines[0] else []
    iovpts.returns = lines[1].split(',') if lines[1] else []
    iovpts.internal = lines[2].split(',') if lines[2] else ['@']
    iovpts.input = lines[3].split(',') if lines[3] else []
    iovpts.output = lines[4].split(',') if lines[4] else []
    iovpts.stack_symbols = lines[5].split(',')
    
    states = lines[6].split(',')
    for state in states:
        iovpts.add_state(state)  # Adiciona cada estado ao objeto IOVPTS
    
    transition_lines = lines[7:]  # Obtém as linhas restantes para as transições
    
    for line in transition_lines:
        if line == "#":  # Encontra o delimitador de fim das transições
            break
        parts = line.split(',')
        iovpts.add_transition(parts[0], parts[1], parts[2], parts[3])  # Adiciona cada transição ao objeto IOVPTS

    # Define o estado inicial após o delimitador
    iovpts.set_initial_state(transition_lines[transition_lines.index("#") + 1])

    return iovpts  # Retorna o objeto IOVPTS populado com os dados do arquivo

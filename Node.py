class NFA_Node():
    def __init__(self, identifier, transitions = []):
        self.id = identifier
        self.transitions = transitions

    def AddTransition(self, symbol, state):
        self.transitions.append((symbol, state))

class DFA_Node():
    def __init__(self, name, nodes, isDirect = False):
        self.name = name
        self.id = None
        self.transitions = []
        self.isMarked = False
        self.isFinal = False
        self.conjunto_nodos = nodes

        if not isDirect:
            self.CreateID(nodes)
        else:
            self.CreateID2(nodes)

    # Metodo para crear un ID unico para el nodo.
    def CreateID(self, nodes):
        a = [n.id for n in nodes]
        a.sort()
        a = [str(i) for i in a]
        self.id = ', '.join(a)

    # Metodo para crear ID unico para hoja de arbol sintactico.
    def CreateID2(self, nodes):
        a = [n for n in nodes]
        a.sort()
        a = [str(i) for i in a]
        self.id = ', '.join(a)

    # Metodo para marcar un estado que ya ha sido visitado.
    def Mark(self):
        self.isMarked = True

    # Metodo para definir un estado como de aceptacion.
    def isAcceptingState(self):
        self.isFinal = True
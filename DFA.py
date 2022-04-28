# References
# Regular expresion to DFA -> https://www.geeksforgeeks.org/regular-expression-to-dfa/
from ctypes import util
from platform import node
from xml.dom.expatbuilder import InternalSubsetExtractor
import utils
import functools
from itertools import count
from Node import DFA_Node
from leaf import Leaf

epsilon = 'ε'
class DFA():
    def __init__(self, regex, complete_symbols, tokens):
        # variable defining
        self.acc_symbols = complete_symbols
        self.count = 0
        self.rounds = 1
        self.states = []
        self.symbols = []
        self.transitions = []
        self.acc_states = []
        self.init_state = None
        self.nodes = [] # Array that contains leaves
        self.root = None
        self.id = 0
        self.final_state = []
        self.follow_pos = {}
        self.tokens = {}
        self.state_names ={}

        #1. If n is a cat-node with left child c1 and right child c2 and i is a position in lastpos(c1), then all positions in firstpos(c2) are in followpos(i).
        # 2. If n is a star-node and i is a position in lastpos(n), then all positions in firstpos(n) are in followpos(i).
        # 3. Now that we have seen the rules for computing firstpos and lastpos, we now proceed to calculate the values of the same for the syntax tree of the given regular expression (a|b)*abb#.
        
        # We start by pre-processing the regular expression given by the user
        print(regex)
        self.build_tree(regex)

        counter = 0
        for i in self.nodes:
            if i.name == '∫':
                self.final_state.append(i.position)
                self.tokens[i.position] = tokens[counter]
                counter = counter + 1

        self.get_follow_pos()
        self.create_dfa()
    
    # Implementacion de la creacion del arbol sintactico
    def build_tree(self, regex):
        my_stack = []
        my_ops = []
        for character in regex:
            if self.is_char_symbol(character):
                my_stack.append(character)
            elif character == '˂':
                my_ops.append(character)
            elif character == '˃':
                last_in = self.peek_stack(my_ops)
                while last_in is not None and last_in != '˂':
                    my_root = self.operate(my_ops, my_stack)
                    my_stack.append(my_root)
                    last_in = self.peek_stack(my_ops)
                my_ops.pop()
            else:
                last_in = self.peek_stack(my_ops)
                while last_in is not None and last_in not in '˂˃' and self.preceding_operator(last_in, character):
                    my_root = self.operate(my_ops, my_stack)
                    my_stack.append(my_root)
                    last_in = self.peek_stack(my_ops)
                my_ops.append(character)

        while self.peek_stack(my_ops) is not None:
            my_root = self.operate(my_ops, my_stack)
            my_stack.append(my_root)
        self.root = my_stack.pop()

    # Verifies if a given character belongs to the valid symbols (letters, numbers and epsilon)
    def is_char_symbol(self, character):
        symbols = 'ε'+'abcdefghijklmnopqrstuvwxyz0123456789'
        return symbols.find(character) != -1

    def peek_stack(self, stack):
        if stack:
            return stack[-1] #Last element
        else:
            return None
        # Implementacion de la creacion del arbol sintactico
    def operate(self, operators, values):
        operator = operators.pop()
        right = values.pop()
        left = '@'

        if right not in self.symbols and right != epsilon and right != '@' and right != '∫':
            self.symbols.append(right)

        if operator != 'Δ' and operator != 'Ʒ':
            left = values.pop()

            if left not in self.symbols and left != epsilon and left != '@' and left != '∫':
                self.symbols.append(left)

        if operator == '∪': 
            return self.or_operation(left, right)
        elif operator == '∩': 
            return self.concatenation(left, right)
        elif operator == 'Δ': 
            return self.kleene_closure(right)

    # Operacion kleen
    def kleene_closure(self, leaf):
        operator = 'Δ'
        if isinstance(leaf, Leaf):
            root = Leaf(operator, None, True, [leaf], True)
            self.nodes += [root]
            return root

        else:
            id_left = None
            if leaf != epsilon:
                id_left = self.get_id()

            left_leaf = Leaf(leaf, id_left, False, [], False)
            root = Leaf(operator, None, True, [left_leaf], True)
            self.nodes += [left_leaf, root]

            return root

    # Operacion OR
    def or_operation(self, left, right):
        operator = '∪'
        if isinstance(left, Leaf) and isinstance(right, Leaf):
            root = Leaf(operator, None, True, [left, right], left.is_nullable or right.is_nullable)
            self.nodes += [root]
            return root

        elif not isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_left = None
            id_right = None
            if left != epsilon:
                id_left = self.get_id()
            if right != epsilon:
                id_right = self.get_id()

            left_leaf = Leaf(left, id_left, False, [], False)
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right_leaf], left_leaf.is_nullable or right_leaf.is_nullable)

            self.nodes += [left_leaf, right_leaf, root]

            return root

        elif isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_right = None
            if right != epsilon:
                id_right = self.get_id()
            
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left, right_leaf], left.is_nullable or right_leaf.is_nullable)

            self.nodes += [right_leaf, root]
            return root

        elif not isinstance(left, Leaf) and isinstance(right, Leaf):
            id_left = None
            if left != epsilon:
                id_left = self.get_id()
            
            left_leaf = Leaf(left, id_left, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right], left_leaf.is_nullable or right.is_nullable)

            self.nodes += [left_leaf, root]
            return root

    # Operacion concatenacion
    def concatenation(self, left, right):
        operator = '∩'
        if isinstance(left, Leaf) and isinstance(right, Leaf):
            root = Leaf(operator, None, True, [left, right], left.is_nullable and right.is_nullable)
            self.nodes += [root]
            return root

        elif not isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_left = None
            id_right = None
            if left != epsilon:
                id_left = self.get_id()
            if right != epsilon:
                id_right = self.get_id()

            left_leaf = Leaf(left, id_left, False, [], False)
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right_leaf], left_leaf.is_nullable and right_leaf.is_nullable)

            self.nodes += [left_leaf, right_leaf, root]
            return root

        elif isinstance(left, Leaf) and not isinstance(right, Leaf):
            id_right = None
            if right != epsilon:
                id_right = self.get_id()
            
            right_leaf = Leaf(right, id_right, False, [], False)
            root = Leaf(operator, None, True, [left, right_leaf], left.is_nullable and right_leaf.is_nullable)

            self.nodes += [right_leaf, root]
            return root
        
        elif not isinstance(left, Leaf) and isinstance(right, Leaf):
            id_left = None
            if left != epsilon:
                id_left = self.get_id()
            
            left_leaf = Leaf(left, id_left, False, [], False)
            root = Leaf(operator, None, True, [left_leaf, right], left_leaf.is_nullable and right.is_nullable)

            self.nodes += [left_leaf, root]
            return root
        
    # Implementacion de Move para la simulacion
    def simulate_move(self, Nodo, symbol):
        move = None
        for i in self.transitions:
            if i[0] == Nodo and i[1] == symbol:
                move = i[2]

        return move
    
    # Crea las transiciones del grafo
    def create_transitions(self):
        f = {}
        for t in self.transitions:
            i, s, fi = [*t]

            if i not in f.keys():
                f[i] = {}
            f[i][s] = fi

        return f

    # Genera los nodos y transiciones para el AFD
    def create_dfa(self):
        startNode0 = self.root.first_pos
        startNode0_automata = DFA_Node(self.get_name(), startNode0, True)
        self.states.append(startNode0_automata)
        self.init_state = startNode0_automata.name
        nodes_temp = []
        for i in startNode0_automata.conjunto_nodos:
            nodes_temp.append(i)

        intersection = utils.intersection(self.final_state, nodes_temp)
        intersection_length = len(intersection)
        if intersection_length > 0:
            self.acc_states.append((startNode0_automata.name, intersection[0]))

        while not self.state_is_marked():
            T = self.state_is_unmarked()
            
            T.Mark()

            for s in self.symbols:
                fp = []
                
                for u in T.conjunto_nodos:
                    if self.get_leaf(u).name == s:
                        fp += self.follow_pos[u]
                fp = {a for a in fp}
                fp = [a for a in fp]
                if len(fp) == 0:
                    continue

                U = DFA_Node(self.get_name(), fp, True)

                if U.id not in [n.id for n in self.states]:
                    nodes_temp = []
                    for i in U.conjunto_nodos:
                        nodes_temp.append(i)
                    intersection = utils.intersection(self.final_state, nodes_temp)
                    intersection_length = len(intersection)
                    if intersection_length > 0:
                        self.acc_states.append((U.name, intersection[0]))
                    
                    self.states.append(U)
                    self.transitions.append((T.name, s, U.name))
                else:
                    self.count -= 1
                    for estado in self.states:
                        if U.id == estado.id:
                            self.transitions.append((T.name, s, estado.name))
        self.state_names = dict(self.acc_states)    

    # Obtiene la hoja a traves de su nombre
    def get_leaf(self, name):
        for n in self.nodes:
            if n.position == name:
                return n

    # Obtiene el estado unmarked
    def state_is_unmarked(self):
        for n in self.states:
            if not n.isMarked:
                return n

    # Obtiene el nombre para asignarlo al nodo
    def get_name(self):
        if self.count == 0:
            self.count += 1
            return 'S' # Starting node!

        available_letters = ' ABCDEFGHIJKLMNOPQRTUVWXYZ'
        name = available_letters[self.count]
        self.count += 1

        if self.count == len(available_letters):
            self.rounds += 1
            self.count = 0

        return name * self.rounds

    # Se realiza el calculo de followpos
    def get_follow_pos(self):
        for n in self.nodes:
            if not n.is_op and not n.is_nullable:
                self.add_followpos(n.position, [])

        for n in self.nodes:
            if n.name == '∩':
                c1, c2 = [*n.leaf_child]

                for i in c1.last_pos:
                    self.add_followpos(i, c2.first_pos)

            elif n.name == 'Δ':
                for i in n.last_pos:
                    self.add_followpos(i, n.first_pos)                

    # Revisa si existe algun estado desmarcado
    def state_is_marked(self):
        marks = [n.isMarked for n in self.states]
        return functools.reduce(lambda a, b: a and b, marks)

    # Agrega un followpos
    def add_followpos(self, pos, val):
        if pos not in self.follow_pos.keys():
            self.follow_pos[pos] = []

        self.follow_pos[pos] += val
        self.follow_pos[pos] = {i for i in self.follow_pos[pos]}
        self.follow_pos[pos] = [i for i in self.follow_pos[pos]]
    
    # Verifies if a given character belongs to the valid symbols (letters, numbers and epsilon)
    def is_char_symbol(self, character):
        valid_symbols = self.acc_symbols + ['ε','∫']
        ans = True if character in valid_symbols else False
        return ans
            

    # Obtiene el ID del nodo
    def get_id(self):
        self.id = self.id + 1
        return self.id

    # Obtiene la precedencia entre dos operadores
    def preceding_operator(self, op1, op2):
        order = ['∪','∩','Δ']
        if order.index(op1) >= order.index(op2):
            return True
        else:
            return False
    
        # Simulacion de AFD
    def simulate_string(self, exp, pos, ignores):
        exp_size = len(exp)
        my_token = ''
        start = self.init_state
        coincidence = True
        lastflag = i = pos
        acc_state = None
        while coincidence and i < exp_size:
            if exp[i] in ignores:
                i = i + 1
                continue
            my_token = my_token + exp[i]
            start = self.simulate_move(start, exp[i])
            if start in [a[0] for a in self.acc_states]:
                 lastflag = i
                 acc_state = dict(self.acc_states)[start]

            if start == None:
                coincidence = False
                break
            i = i+1
        if len(my_token) != 1:
            my_token = my_token[:-1]
        return my_token, lastflag + 1, acc_state
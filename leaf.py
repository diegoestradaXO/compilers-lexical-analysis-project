class Leaf():
    def __init__(self, name, position, is_op, leaf_child, is_nullable):
        self.name = name
        self.position = position
        self.is_op = is_op
        self.leaf_child = leaf_child
        self.is_nullable = is_nullable
        self.first_pos = []
        self.last_pos = []
        self.follow_pos = []
        if self.name == 'ε':
            self.is_nullable = True
        self.add_first_pos()
        self.add_last_pos()


    def GetName(self):
        name = f'{self.name} - {self.position}'
        return name

    def add_first_pos(self):
        if self.is_op:
            if self.name == '∪': # In case is OR
                self.first_pos = self.leaf_child[0].first_pos + self.leaf_child[1].first_pos
            elif self.name == '∩': # In case is CONCAT
                if self.leaf_child[0].is_nullable:
                    self.first_pos = self.leaf_child[0].first_pos + self.leaf_child[1].first_pos
                else:
                    self.first_pos += self.leaf_child[0].first_pos
            elif self.name == 'Δ': # In case is KLEENE
                self.first_pos += self.leaf_child[0].first_pos
        else:
            if self.name != 'ε':
                self.first_pos.append(self.position)

    def add_last_pos(self):
        if self.is_op:
            if self.name == '∪': #In case is OR
                self.last_pos = self.leaf_child[0].last_pos + self.leaf_child[1].last_pos
            elif self.name == '∩':#In case is CONCAT
                if self.leaf_child[1].is_nullable:
                    self.last_pos = self.leaf_child[0].last_pos + self.leaf_child[1].last_pos
                else:
                    self.last_pos += self.leaf_child[1].last_pos
            elif self.name == 'Δ': #In case is Kleene
                self.last_pos += self.leaf_child[0].last_pos
        else:
            if self.name != 'ε':
                self.last_pos.append(self.position)

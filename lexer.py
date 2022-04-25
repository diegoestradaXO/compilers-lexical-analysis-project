class Lexer():
    def __init__(self, atg_file):

        self.parse(atg_file)

    def parse(file):
         syntax = {
             'chars': [],
             'keywords':[],
             'tokens':[],
             'productions':[],
             'ignores':[]
         }

         for line in file: # getting every line in the file
            value = line.split() # separating each word or value in every line in the file
            value_length = len(value)
            if value_length > 0:
                pass



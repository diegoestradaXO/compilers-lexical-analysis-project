

class Lexer():
    def __init__(self, atg_file):
        self.compiler = None
        self.ignores = []
        self.resolve(atg_file)

    def resolve(self, file):
        compilerName = None
        str = ''
        grammar = {
             'chars': [],
             'keywords':[],
             'tokens':[],
             'ignores':[]
         }
        charFlag = False
        keywordFlag = False
        tokensFlag = False

        for line in file: # getting every line in the file
            values = line.split() # separating each word or value in every line in the file
            values_length = len(values)
            if values_length > 0: # If line is not empty
                # verify titles of COCOL file
                # in almost every case the title will be in the very first
                if values[0] == 'COMPILER':
                    compilerName = values[1]
                elif values[0] == 'CHARACTERS':
                    charFlag = True
                elif values[0] == 'KEYWORDS':
                    keywordFlag = True
                    charFlag = False
                elif values[0] == 'TOKENS':
                    tokensFlag = True
                    keywordFlag = False
                elif values[0] == 'IGNORE':
                    grammar['ignores'].append(values[1])
                    tokensFlag = False
                elif values[0] == 'END':
                    break

                if charFlag == True:
                    grammar['chars'].append(line)
                elif keywordFlag == True:
                    grammar['keywords'].append(line)
                elif tokensFlag == True:
                    str = str + line
                    if line[-1] == '.' or str == 'TOKENS':
                        grammar['tokens'].append(str)
                        str = ''
                        
        # removing title
        if len(grammar['chars']) > 0:
            grammar['chars'].pop(0)
        if len(grammar['keywords']) > 0:
            grammar['keywords'].pop(0)
        if len(grammar['tokens']) > 0:
            grammar['tokens'].pop(0)

        # printing the values
        print("chars==========")
        for p in grammar['chars']:
            print(p)
        print("tokens==========")
        for p in grammar['tokens']:
            print(p)
        
        self.compiler = compilerName
        self.buildCharacters(grammar['chars'])

        for i in grammar['ignores']:
            ignore = self.characters[i]
            ignore = ignore.replace(chr(706), '') # <
            ignore = ignore.replace(chr(707), '') # >
            self.ignores += ignore.split(chr(8746)) # ∪

        print(self.ignores)

        # self.buildKeywords(grammar['keywords'])
        # self.buildTokens(grammar['tokens'])

    def buildCharacters(self, grammar):
        pass

config_file = []

archivo = input('Ingrese el nombre del archivo ATG: ')

with open(archivo, 'r') as reader:
    for line in reader:
        if line != '\n':
            config_file.append(line.strip())

analisislexico = Lexer(config_file)
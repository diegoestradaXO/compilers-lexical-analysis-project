from lib2to3.pgen2 import token
import re

# special characters
pipe = chr(8746) # ∪
left = chr(706) # ˂
right = chr(707) # ˃

class Lexer():
    def __init__(self, atg_file):
        self.compiler = None
        self.ignores = []
        self.characters = {}
        self.keywords = {}
        self.tokens = {}
        self.resolve(atg_file)

    def resolve(self, atg_file):
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

        for line in atg_file: # getting every line in the file
            values = line.split() # separating each word or value in every line in the file
            values_size = len(values)
            if values_size > 0: # If line is not empty

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

                # Adding every line after the title in the COCOL file 
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
        
        # Assigning name to the compiler in order to name the scanner file after execution
        self.compiler = compilerName

        # building characters
        self.create_chars(grammar['chars'])
        for i in grammar['ignores']:
            ignore = self.characters[i]
            ignore = ignore.replace(left, '') # <
            ignore = ignore.replace(right, '') # >
            self.ignores += ignore.split(pipe) # ∪

        self.create_keywords(grammar['keywords'])
        self.create_tokens(grammar['tokens'])
    
    def evaluate(self, tokens):
        values = []
        ops = []
        i = 0
        
        last = 0
        for i in range(len(tokens) - 2):
            if tokens[i:i+3] == ' - ' or tokens[i:i+3] == ' + ':
                ops.insert(0, tokens[i+1])
                values.insert(0, tokens[last + 1:i - 1])
                last = i + 3
        values.insert(0, tokens[last + 1:-1])

        while len(ops) != 0:
            val1 = values.pop()
            val2 = values.pop()
            op = ops.pop()
                    
            values.append(self.do_operation(val1, val2, op))

        return values[-1]

 
    def get_explicit_range(self, a, b):
        for c in range(ord(a), ord(b) + 1):
            yield chr(c)
    
    def do_operation(self, a, b, op):
        if op == '+': 
            res = a + pipe + b
            res = pipe.join(list(dict.fromkeys(res.split(pipe))))
            return res
        if op == '-': 
            return pipe.join(list(set(a.split(pipe)) - set(b.split(pipe))))

    def create_chars(self, characters):
        any_char_array = []
        for i in range(9,11):
            any_char_array.append(chr(i))
        for i in range(13,14):
            any_char_array.append(chr(i))
        for i in range(32,127):
            any_char_array.append(chr(i))

        any_char_string = '˂'+ pipe.join(any_char_array) +'˃'
        pattern = '(CHR\([0-9]*\))'
        for i in range(len(characters)):
            similarities = re.findall(pattern, characters[i])
            new_char = characters[i]
            for m in similarities:
                new_char = new_char.replace(m, "'" + eval(m.lower()) + "'" if eval(m.lower()) == '"' else '"' + eval(m.lower()) + '"')

            characters[i] = new_char
        print(characters)
        self.characters['ANY'] = any_char_string

        for char in characters:
            character = char.split('=', 1) # only splitting in the equals sign, just one split

            has_apostrophe = False # ' '
            has_quotation_mark = False # " "
            last = 0
            new = ''

            char_to_evaluate = character[1] # right side of the line

            final = ''
            for i in range(len(char_to_evaluate)):
                text = ''
                if char_to_evaluate[i] == '"' and not has_quotation_mark and not has_apostrophe:
                    has_quotation_mark = True
                    last = i + 1

                elif char_to_evaluate[i] == '"' and has_quotation_mark:
                    has_quotation_mark = False
                    has_apostrophe = False
                    new = char_to_evaluate[last:i]

                    for i in range(len(new)):
                        if i < len(new) - 1:
                            text += new[i] + pipe
                        else:
                            text += new[i] # last element, it doesnt use pipe

                    final += '˂' + text + '˃'

                elif char_to_evaluate[i] == "'" and not has_apostrophe and not has_quotation_mark:
                    has_apostrophe = True
                    last = i + 1

                elif char_to_evaluate[i] == "'" and has_apostrophe:
                    has_quotation_mark = False
                    has_apostrophe = False
                    new = char_to_evaluate[last:i]

                    for i in range(len(new)):
                        if i < len(new) - 1:
                            text += new[i] + pipe
                        else:
                            text += new[i] # last element, it doesnt use pipe

                    final += '˂' + text + '˃'

                elif char_to_evaluate[i] == '+' and not has_apostrophe and not has_quotation_mark:
                    final += ' + '
                
                elif char_to_evaluate[i] == '-' and not has_apostrophe and not has_quotation_mark:
                    final += ' - '

                elif not has_apostrophe and not has_quotation_mark and char_to_evaluate[i] != ' ':
                    final += char_to_evaluate[i]

            self.characters[character[0].replace(' ', '')] = final[:-1] # removing the dot

        for key, value in self.characters.items():
            result = ''
            if '..' in value:
                index = value.find('..')
                a = value[1:index-1].rstrip().lstrip()
                b = value[index+3:-1].rstrip().lstrip()
                resultadoA = chr(int(a[4:-1])) if a.find('CHR(') == 0 else a.replace("'", "")
                resultadoB = chr(int(b[4:-1])) if b.find('CHR(') == 0 else b.replace("'", "")

                for j in self.get_explicit_range(a, b):
                    if j != b:
                        result += j + pipe
                    else:
                        result += j
                self.characters[key] = '˂' + result + '˃'
                # print(self.characters[key])
        
        char_keys = list(self.characters.keys())
        valores = list(self.characters.values())
        for i in range(len(char_keys) - 1):
            for j in range(i + 1, len(char_keys)):
                if char_keys[i] in self.characters[char_keys[j]]:
                    self.characters[char_keys[j]] = self.characters[char_keys[j]].replace(char_keys[i], self.characters[char_keys[i]])

        for key, value in self.characters.items():
            result = self.evaluate(value)
            self.characters[key] = '˂' + result + '˃'

    def create_keywords(self, keywords):
        # result
        # keywords = {
        #   name: value
        # }
        for kw in keywords:
            kw = kw.replace(' ', '')
            keyword, word = kw.split('=')
            word = word[:-1]
            
            self.keywords[word.replace('"', '')] = keyword.replace('"', '')
        # print(self.keywords)

    def create_tokens(self, tokens):
        # result 
        # tokens = {
        #   (tokenName, {expresion, excepts}) 
        # }
        listCharacters = list(self.characters.keys())
        listCharacters.sort(key = len)
        listCharacters.reverse()
        for token in tokens:
            token_ = token.split('=', 1)
            has_quotation_mark = False
            last = 0
            new = ""
            ident = token_[0].replace(' ', '')
            token_to_evaluate = token_[1]
            final = ""
            for i in range(len(token_to_evaluate)):
                text = ""
                if token_to_evaluate[i] == '"' and not has_quotation_mark:
                    has_quotation_mark = True
                    last = i + 1
                elif token_to_evaluate[i] == '"' and has_quotation_mark:
                    has_quotation_mark = False
                    has_apostrophe = False
                    new = token_to_evaluate[last:i]
                    for i in range(len(new)):
                        text += new[i]
                    final += left + text + right
                elif not has_quotation_mark and token_to_evaluate[i] != ' ':
                    final += token_to_evaluate[i]
            final = final.replace('|', pipe)
            # end of string manipulationg

            # print(final[:-1])
            self.tokens[ident] = {}
            self.tokens[ident]['expresion'] = final[:-1]
            self.tokens[ident]['except'] = {}

        for key, value in self.tokens.items():
            if 'EXCEPT' in value['expresion']:
                exceptions = value['expresion'].split('EXCEPT')
                self.tokens[key]['expresion'] = exceptions[0]

                if exceptions[1].replace('.', '') == 'KEYWORDS':
                    self.tokens[key]['except'] = self.keywords

            if '{' in value['expresion'] and '}' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('{', '˂')
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('}', '˃Δ')

            if '[' in value['expresion'] and ']' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('[', '˂')
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace(']', '˃Ʒ')

        # print(self.tokens.items())
        # print(listCharacters)
        for key, value in self.tokens.items():
            newToken = value['expresion']
            for character in listCharacters:
                if character in value['expresion']:
                    newToken = newToken.replace(character, self.characters[character])

            value['expresion'] = newToken
        # print(self.tokens.items())

atg_file = []

file_name = input('Write the name of the ATG file: ')

with open(file_name, 'r') as reader:
    for line in reader:
        if line != '\n':
            atg_file.append(line.strip())

analisislexico = Lexer(atg_file)

tokens_program = ''
exception_program = ''

for key, value in analisislexico.tokens.items():
    tokens_program += '"' + key + '":' + repr(value['expresion']) + ',\n'
    exception_program += '"' + key + '": ' + str(value['except']) + ',\n'

scanner_file = '''
from DFA import DFA
import regex
epsilon = 'ε'
exceptions = {
''' + f'{exception_program}' + '''}
tokens = {
''' + r'{}'.format(tokens_program) + '''}
ignores = ''' + f'{analisislexico.ignores}' + '''
acc_chars = []
for k, v in tokens.items():
    for i in v:
        if i not in '˂˃∪ƷΔ∩' and i not in acc_chars:
            acc_chars.append(i)
expression = '∪'.join(['˂˂' + token + '˃∫˃' for token in tokens.values()])
file_name = input('Write the name of the file: ')
filee = open(file_name, 'r', encoding='utf-8', errors='replace')
w = ''.join(filee.readlines())
regexp = regex.fix_regex_lexer(expression)
automata = DFA(regexp, acc_chars, [t for t in tokens.keys()])
pos = 0
while pos < len(w):
    resultado, pos, aceptacion = automata.simulate_string(w, pos, ignores)
    if aceptacion:
        permitido = True
        for excepcion in exceptions[automata.tokens[aceptacion]].keys():
            if resultado == excepcion:
                permitido = False
                print(repr(excepcion), 'is keyword', exceptions[automata.tokens[aceptacion]][excepcion])
                break
        if permitido:
            if automata.tokens[aceptacion] not in ignores:
                print(repr(resultado), '->', automata.tokens[aceptacion])
    else:
        if resultado != '':
            print(repr(resultado), 'not expected')
'''

f = open(f'scanner{analisislexico.compiler}.py', 'w', encoding='utf-8')
f.write(scanner_file)
f.close()
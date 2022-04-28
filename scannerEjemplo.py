
from DFA import DFA
import regex
epsilon = 'ε'
exceptions = {
"id": {'if': 'if', 'while': 'while'},
"number": {},
"hexnumber": {},
}
tokens = {
"id":'˂a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z∪A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z˃˂˂a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z∪A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z˃˃Δ',
"number":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ',
"hexnumber":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪A∪B∪C∪D∪E∪F˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪A∪B∪C∪D∪E∪F˃˃Δ˂(H)˃',
}
ignores = []
acc_chars = []
for k, v in tokens.items():
    for i in v:
        if i not in '˂˃∪ƷΔ∩' and i not in acc_chars:
            acc_chars.append(i)
expression = '∪'.join(['˂˂' + token + '˃∫˃' for token in tokens.values()])
my_file = input('Write the name of the file: ')
filee = open(my_file, 'r', encoding='utf-8', errors='replace')
w = ''.join(filee.readlines())
regexp = regex.fix_regex_lexer(expression)
syntax = DFA(regexp, acc_chars, [t for t in tokens.keys()])
pos = 0
while pos < len(w):
    resultado, pos, aceptacion = syntax.simulate_string(w, pos, ignores)
    if aceptacion:
        permitido = True
        for excepcion in exceptions[syntax.tokens[aceptacion]].keys():
            if resultado == excepcion:
                permitido = False
                print('-', repr(excepcion), 'is keyword', exceptions[syntax.tokens[aceptacion]][excepcion], '-')
                break
        if permitido:
            if syntax.tokens[aceptacion] not in ignores:
                print('-', repr(resultado), '->', syntax.tokens[aceptacion], '-')
    else:
        if resultado != '':
            print('-', repr(resultado), 'not expected', '-')

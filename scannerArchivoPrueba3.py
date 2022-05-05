
from DFA import DFA
import regex
epsilon = 'ε'
exceptions = {
"identificador": {'if': 'si', 'for': 'para', 'while': 'mientras', 'WHILE': 'MIENTRAS', 'While': 'Mientras'},
"numero": {},
"numeroDecimal": {},
"numeroHex": {},
"espacioEnBlanco": {},
"cadena": {},
}
tokens = {
"identificador":'˂a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z∪A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z˃˂˂a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z∪A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z˃∪˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˃Δ',
"numero":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˃Δ',
"numeroDecimal":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˃Δ˂.˃˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪0˃˃Δ',
"numeroHex":'˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪A∪B∪C∪D∪E∪F˃˂˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪A∪B∪C∪D∪E∪F˃˃Δ˂H˃',
"espacioEnBlanco":'˂\t∪ ˃˂˂\t∪ ˃˃Δ',
"cadena":'˂"˃˂a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z∪A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z∪0∪1∪2∪3∪4∪5∪6∪7∪8∪9∪\t∪ ˃˂"˃',
}
ignores = []
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

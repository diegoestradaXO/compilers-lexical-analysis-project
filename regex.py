from typing import final

from sympy import Add
epsilon = 'ε'

def fix_regex(expresion, isDFA=False):
    first = []
    regex_list = []
    last_index = 0
    i = 0
    special_cases = {
        'positive_closure_group':')+',
        'null_check_group':')?',
        'positive_closure':'+',
        'null_check':'?',
    }
    # Case 01: positive closure (parenthesis)
    if expresion.find(special_cases['positive_closure_group']) != -1:
        while i < len(expresion):
            if expresion[i] == '(':
                first.append(i) # Saves the index            

            if expresion[i] == ')' and i < len(expresion) - 1: # current pos
                regex_list.append(expresion[i])
                if expresion[i + 1] == '+': # is the next pos positive closure?
                    last_index = i + 1
                    regex_list.append('*')
                    regex_list.append(expresion[first.pop() : last_index])
                    i = i + 1
                else:
                    first.pop()

            else:
                regex_list.append(expresion[i])
            i = i + 1

        expresion = ''.join(regex_list)

    #Case 02: null check (parenthesis)
    if expresion.find(special_cases['null_check_group']) != -1:
        while i < len(expresion):
            if expresion[i] == '(':
                first.append(i)                        

            if expresion[i] == ')':
                regex_list.append(expresion[i])  # current pos
                if expresion[i + 1] == '?':     # is the next pos null check?
                    last_index = i + 1
                    regex_list.append('|')
                    regex_list.append('ε')
                    regex_list.append(')')
                    regex_list.insert(first[-1], '(')
                    i = i + 1
                else:
                    first.pop()

            else:
                regex_list.append(expresion[i])
            i += 1

        expresion = ''.join(regex_list)

    final_regex = expresion

    # Case 03: positive closure to an individual symbol
    if expresion.find(special_cases['positive_closure']) != -1:
        while final_regex.find(special_cases['positive_closure']) != -1:
        # while '+' in regex_copy:
            i = final_regex.find('+')
            symbol = final_regex[i - 1]

            final_regex = final_regex.replace(symbol + '+', '(' + symbol + '*' + symbol + ')')

    # Case 04: null check to an individual symbol
    if expresion.find(special_cases['null_check']) != -1:
        while final_regex.find(special_cases['null_check']) != -1:
        # while '?' in regex_copy:
            i = final_regex.find('?')
            symbol = final_regex[i - 1]

            final_regex = final_regex.replace(symbol + '?', '(' + symbol + '|' + 'ε' + ')')

    # Case 05: user did not put the same amount of open parenthesis and close parenthesis
    if final_regex.count('(') > final_regex.count(')'):
        for i in range(final_regex.count('(') - final_regex.count(')')):
            final_regex += ')'

    elif final_regex.count('(') < final_regex.count(')'):
        for i in range(final_regex.count(')') - final_regex.count('(')):
            final_regex = '(' + final_regex
    
    if(isDFA == True):
        final_regex = '(' + final_regex + ')#'

    return add_explicit_concatenation(final_regex)

def add_explicit_concatenation(regex):
    valid_operators = ['Δ','∪','˂']
    enhanced_regex = ''
    i = 0
    regex_size = len(regex)
    
    while i < regex_size:
        if i+1 >= len(regex):
            enhanced_regex += regex[-1]
            break
        if regex[i] == 'Δ' and regex[i+1] != '˃' and not (regex[i+1] in valid_operators):
            enhanced_regex += regex[i]+'∩'
        elif regex[i] == 'Δ' and regex[i+1] == '˂':
            enhanced_regex += regex[i]+'∩'
        elif regex[i] == 'Ʒ' and regex[i+1] != '˃' and not (regex[i+1] in valid_operators):
            enhanced_regex += regex[i]+'∩'
        elif regex[i] == 'Ʒ' and regex[i+1] == '˂':
            enhanced_regex += regex[i]+'∩'
        elif not (regex[i] in valid_operators) and regex[i+1] == '˃':
            enhanced_regex += regex[i]
        elif (not (regex[i] in valid_operators) and not (regex[i+1] in valid_operators)) or (not (regex[i] in valid_operators) and (regex[i+1] == '˂')):
            enhanced_regex += regex[i]+'∩'
        else:
            enhanced_regex += regex[i]
        i += 1
    return enhanced_regex


# Convierte la expresion a una que pueda leer el programa
def fix_regex_lexer(regular):
    exp = []
    hasExpression = False
    hasPlus = False
    final = 0
    
    while '˃Ʒ' in regular:
        real = []
        i = 0
        initial = []
        while i < len(regular) - 1:
            if regular[i] == '˂':
                initial.append(i)                        

            if regular[i] == '˃':
                real.append(regular[i])
                if regular[i + 1] == 'Ʒ':
                    final = i + 1
                    real.append('∪')
                    real.append(epsilon)
                    real.append('˃')
                    real.insert(initial[-1], '˂')
                    i += 1
                    break
                else:
                    initial.pop()

            else:
                real.append(regular[i])
            i += 1

        regular = ''.join(real) + regular[i + 1:]

    regular_copy = regular

    if 'Ʒ' in regular_copy:
        while 'Ʒ' in regular_copy:
            i = regular_copy.find('Ʒ')
            symbol = regular_copy[i - 1]

            regular_copy = regular_copy.replace(symbol + 'Ʒ', '˂' + symbol + '∪' + epsilon + '˃')

    if regular_copy.count('˂') > regular_copy.count('˃'):
        for i in range(regular_copy.count('˂') - regular_copy.count('˃')):
            regular_copy += '˃'

    elif regular_copy.count('˂') < regular_copy.count('˃'):
        for i in range(regular_copy.count('˃') - regular_copy.count('˂')):
            regular_copy = '˂' + regular_copy

    return add_explicit_concatenation(regular_copy)
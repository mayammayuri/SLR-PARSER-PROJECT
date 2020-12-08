from tkinter import Tk
from tkinter import *

from graphviz.dot import Graph
from graph import make_graph
import tkinter as tk
import tkinter
from tabulate import tabulate
from graphviz import dot
from PIL import ImageTk, Image
from graphviz import Digraph
import sys
import os
import shlex
import copy
from prettytable import PrettyTable
import numpy as np

master = Tk()

master.title('SLR Parser')

canvas = Canvas(master, width=master.winfo_screenwidth(),
                height=master.winfo_screenheight())


grammars = open("F:\EBOOKS\Third year\Compiler design\lab\project\grammar.txt")
#grammars = open("grammar.txt")
G = {}
C = {}
start = ""
terminals = []
nonterminals = []
symbols = []
error = 0
master = Tk()

master.title('SLR Parser')

canvas = Canvas(master, width=master.winfo_screenwidth(),
                height=master.winfo_screenheight())


def parse_grammar():
    global G, start, terminals, nonterminals, symbols
    for line in grammars:
        line = " ".join(line.split())
        if line == '\n':
            break
        head = line[:line.index("->")].strip()
        prods = [l.strip().split(' ')
                 for l in ''.join(line[line.index("->") + 2:]).split('|')]
        if not start:
            start = head + "'"
            G[start] = [[head]]
            nonterminals.append(start)
        if head not in G:
            G[head] = []
        if head not in nonterminals:
            nonterminals.append(head)
        for prod in prods:
            G[head].append(prod)
            for char in prod:
                if not char.isupper() and char not in terminals:
                    terminals.append(char)
                elif char.isupper() and char not in nonterminals:
                    nonterminals.append(char)
                    G[char] = []  # non terminals dont produce other symbols
    symbols = nonterminals + terminals


first_seen = []


def FIRST(X):
    global first_seen
    first = []
    first_seen.append(X)
    if X in terminals:  # CASE 1
        first.append(X)
    elif X in nonterminals:
        for prods in G[X]:  # CASE 2
            if prods[0] in terminals and prods[0] not in first:
                first.append(prods[0])
            else:  # CASE 3
                for nonterm in prods:
                    if nonterm not in first_seen:
                        for terms in FIRST(nonterm):
                            if terms not in first:
                                first.append(terms)
    first_seen.remove(X)
    return first


follow_seen = []


def FOLLOW(A):
    global follow_seen
    follow = []
    follow_seen.append(A)
    if A == start:  # CASE 1
        follow.append('$')
    for heads in G.keys():
        for prods in G[heads]:
            follow_head = False
            if A in prods:
                next_symbol_pos = prods.index(A) + 1
                if next_symbol_pos < len(prods):  # CASE 2
                    for terms in FIRST(prods[next_symbol_pos]):
                        if terms not in follow:
                            follow.append(terms)
                else:  # CASE 3
                    follow_head = True
                if follow_head and heads not in follow_seen:
                    for terms in FOLLOW(heads):
                        if terms not in follow:
                            follow.append(terms)
    follow_seen.remove(A)
    return follow


def closure(I):
    J = I
    while True:
        item_len = len(J) + sum(len(v) for v in J.items())
        for heads in list(J):
            for prods in J[heads]:
                dot_pos = prods.index('.')  # checks if final item or not
                if dot_pos + 1 < len(prods):
                    prod_after_dot = prods[dot_pos + 1]
                    if prod_after_dot in nonterminals:
                        for prod in G[prod_after_dot]:
                            item = ["."] + prod
                            if prod_after_dot not in list(J):
                                J[prod_after_dot] = [item]
                            elif item not in J[prod_after_dot]:
                                J[prod_after_dot].append(item)
        if item_len == len(J) + sum(len(v) for v in J.items()):
            return J


def GOTO(I, X):
    goto = {}
    for heads in I.keys():
        for prods in I[heads]:
            for i in range(len(prods) - 1):
                if "." == prods[i] and X == prods[i + 1]:
                    temp_prods = prods[:]
                    temp_prods[i], temp_prods[i +
                                              1] = temp_prods[i + 1], temp_prods[i]
                    prod_closure = closure({heads: [temp_prods]})
                    for keys in prod_closure:
                        if keys not in goto.keys():
                            goto[keys] = prod_closure[keys]
                        elif prod_closure[keys] not in goto[keys]:
                            for prod in prod_closure[keys]:
                                goto[keys].append(prod)
    return goto


def items():
    global C
    i = 1
    C = {'I0': closure({start: [['.'] + G[start][0]]})}
    while True:
        item_len = len(C) + sum(len(v) for v in C.items())
        for I in list(C):
            for X in symbols:
                # print(C[I], ',', X,'-----',GOTO(C[I],X))
                if GOTO(C[I], X) and GOTO(C[I], X) not in C.values():
                    C['I' + str(i)] = GOTO(C[I], X)
                    i += 1
        if item_len == len(C) + sum(len(v) for v in C.items()):
            return


def ACTION(i, a):
    global error
    global terminals

    for heads in C['I' + str(i)]:
        for prods in C['I' + str(i)][heads]:
            for j in range(len(prods) - 1):
                if prods[j] == '.' and prods[j + 1] == a:
                    for k in range(len(C)):
                        if GOTO(C['I' + str(i)], a) == C['I' + str(k)]:
                            if a in terminals:

                                if "r" in parse_table[i][terminals.index(a)]:
                                    if error != 1:
                                        print("ERROR: Shift-Reduce Conflict at State " + str(i) + ", Symbol \'" + str(
                                            terminals.index(a)) + "\'")
                                    error = 1
                                    if "s" + str(k) not in parse_table[i][terminals.index(a)]:
                                        parse_table[i][terminals.index(a)] = parse_table[i][
                                            terminals.index(a)] + "/s" + str(k)
                                    return parse_table[i][terminals.index(a)]
                                else:
                                    parse_table[i][terminals.index(
                                        a)] = "s" + str(k)
                            else:
                                parse_table[i][len(
                                    terminals) + nonterminals.index(a)] = str(k)
                            return "s" + str(k)
    for heads in C['I' + str(i)]:
        if heads != start:
            for prods in C['I' + str(i)][heads]:
                if prods[-1] == '.':  # final item
                    k = 0
                    for head in G.keys():
                        for Gprods in G[head]:
                            if head == heads and (Gprods == prods[:-1]) and (a in terminals or a == '$'):
                                for terms in FOLLOW(heads):
                                    if terms == '$':
                                        index = len(terminals)
                                    else:
                                        index = terminals.index(terms)
                                    
                                    if "s" in parse_table[i][index]:
                                        if error != 1:
                                            print("ERROR: Shift-Reduce Conflict at State " + str(i) + ", Symbol \'" + str(terms) + "\'")
                                        
                                        if "r" + str(k) not in parse_table[i][index]:
                                            parse_table[i][index] = parse_table[i][index] + \
                                                "/r" + str(k)
                                        return parse_table[i][index]
                                        
                                    elif parse_table[i][index] and parse_table[i][index] != "r" + str(k):
                                        if error != 1:
                                            print("ERROR: Reduce-Reduce Conflict at State " + str(i) + ", Symbol \'" + str(terms) + "\'")
                                        
                                        if "r" + str(k) not in parse_table[i][index]:
                                            parse_table[i][index] = parse_table[i][index] + \
                                                "/r" + str(k)
                                        return parse_table[i][index]
                                        
                                    else:
                                        parse_table[i][index] = "r" + str(k)
                                return "r" + str(k)
                                
                            k += 1
    if start in C['I' + str(i)] and G[start][0] + ['.'] in C['I' + str(i)][start]:
        parse_table[i][len(terminals)] = "acc"
        return "acc"
    return "0"


def print_info():
    print("GRAMMAR:")
    for head in G.keys():
        if head == start:
            continue
        print("{:>{width}} ->".format(head,
                                      width=len(max(G.keys(), key=len))), end=' ')
        num_prods = 0
        for prods in G[head]:
            if num_prods > 0:
                print("|", end=' ')
            for prod in prods:
                print(prod, end=' ')
            num_prods += 1
        print()
    output_file = open('closure.txt', 'w+')
    print("\nAUGMENTED GRAMMAR:")
    i = 0
    print('', end=' ')
    for head in G.keys():
        print("{:>{width}} ->".format(head,
                                      width=len(max(G.keys(), key=len))), end='')
        num_prods = 0
        for prods in G[head]:
            if num_prods > 0:
                print("|", end=' ')
            for prod in prods:
                print(prod, end=' ')
            num_prods += 1
        print()
    for head in G.keys():
        for prods in G[head]:
            output_file.write("{:>{width}}:".format(
                str(i), width=len(str(sum(len(v) for v in G.items()) - 1))))
            output_file.write('\n')
            output_file.write("{:>{width}} ->".format(head,
                                                      width=len(max(G.keys(), key=len))))
            output_file.write('\n')
            for prod in prods:
                output_file.write(prod)
                output_file.write('\n')

            output_file.write('\n')
            i += 1
    terminals.append("$")
    print("\nTERMINALS   :", terminals)
    print("NONTERMINALS:", nonterminals)
    print("SYMBOLS     :", symbols)
    print("\nFIRST:")
    print('', end=' ')
    for head in G:
        print("{:>{width}} =".format(
            head, width=len(max(G.keys(), key=len))), end=' ')
        print("{ ", end='')
        num_terms = 0
        for terms in FIRST(head):
            if num_terms > 0:
                print(", ", end='')
            print(terms, end='')
            num_terms += 1
        print(" }")

    print("\nFOLLOW:")
    print('', end=' ')
    for head in G:
        print("{:>{width}} =".format(
            head, width=len(max(G.keys(), key=len))), end='')
        print("{ ", end='')
        num_terms = 0
        for terms in FOLLOW(head):
            if num_terms > 0:
                print(", ", end='')
            print(terms, end='')
            num_terms += 1
        print(" }")
    f = open("F:\EBOOKS\Third year\Compiler design\lab\project\Items.txt", "w+")
    r = open("F:\EBOOKS\Third year\Compiler design\lab\project\Gotofile.txt", "w+")
    e = open("F:\EBOOKS\Third year\Compiler design\lab\project\Edges.txt", "w+")
    f.write(str(len(C)) + "\n")
    for i in range(len(C)):
        f.write('I' + str(i) + ':')
        f.write('\n')
        for keys in C['I' + str(i)]:
            for prods in C['I' + str(i)][keys]:
                f.write("{:>{width}} -> ".format(keys,
                                                 width=len(max(G.keys(), key=len)) - 1))
                for prod in prods:
                    f.write(prod)
                f.write('\n')
        r.write('I' + str(i) + ':')
        r.write('\n')

        for X in symbols:
            ctr = -1
            if GOTO(C['I' + str(i)], X) != {}:
                for si in range(len(C)):
                    if GOTO(C['I' + str(i)], X) == C['I' + str(si)]:
                        ctr = si
                        break

                r.write(str(X))
                r.write(' -> ')
                r.write(str(ctr))
                e.write('I' + str(i))
                e.write('|')
                e.write('I' + str(si))
                e.write('\n')
                r.write('\n')

        f.write('\n')
        r.write('\n')
    print()

    for i in range(len(parse_table)):  # len gives number of states
        for j in symbols:
            ACTION(i, j)
    print_table()
    process_input()
    


class TabulateLabel(tk.Label):
    def __init__(self, data, header, **kwargs):
        super().__init__(font=('Consolas', 10), justify=tk.LEFT, anchor='nw', **kwargs)
        text = tabulate(data, headers=header, tablefmt='psql', showindex=False)
        self.configure(text=text)

    # display.pack()


def print_table():

    rows, cols = (len(C.keys()) + 1, len(terminals) + len(nonterminals[1:]))
    parseing_table = ['States']
    nptable = []
    print("PARSING TABLE:")
    for ele in terminals:
        parseing_table.append(ele)
    for j in nonterminals[1:]:
        parseing_table.append(j)
    header = parseing_table
    for i in range(len(parse_table)):
        for j in range(len(parse_table[i])):
            if parse_table[i][j] == '':
                parse_table[i][j] = '0'
    position = 0
    add = []
    for i in range(len(parse_table)):
        for j in range(len(parse_table[i])):
            if parse_table[i][j] == '0':
                if j not in add:
                    add.append(j)
            elif j in add:
                add.remove(j)
    position = add[0]
    for i in range(len(parse_table)):
        parse_table[i][position] = 'pp'
        parse_table[i].insert(0, 'I'+str(i))
    for i in range(len(parse_table)):
        parse_table[i].remove('pp')
    print(len(header), len(parse_table[0]))
    print(tabulate(parse_table, headers=header, tablefmt="psql"))

def process_input():
    input_string = ""
    inputtt = open('F:\EBOOKS\Third year\Compiler design\lab\project\string.txt')

    for i in inputtt:
        input_string = input_string.join(i)
    get_input = input_string
    list1 = []
    list1[:0] = get_input
    list1.append("$")
    to_parse = list1
    pointer = 0
    stack = []
    stack.append("0")
    string_table = []
    header = ["STEP", "STACK", "INPUT", "ACTION"]

    step = 1
    for ele in to_parse:
        top = int(stack[-1])
        get_action = ACTION(top, ele)
    while True:
        curr_symbol = to_parse[pointer]
        top_stack = int(stack[-1])
        stack_content = ""
        input_content = ""
        string_table.append(step)
        for i in stack:
            stack_content += i
        string_table.append(stack_content)
        i = pointer
        while i < len(to_parse):
            input_content += to_parse[i]
            i += 1
        string_table.append(input_content)
        step += 1
        get_action = ACTION(top_stack, curr_symbol)
        if "/" in get_action:
            string_table.append(get_action + ". So conflict")
            break
        if "s" in get_action:
            string_table.append(get_action)
            stack.append(curr_symbol)
            stack.append(get_action[1:])
            pointer += 1
        elif "r" in get_action:
            string_table.append(get_action)
            i = 0
            for head in G.keys():
                for prods in G[head]:
                    if i == int(get_action[1:]):
                        for j in range(2 * len(prods)):
                            stack.pop()
                        state = stack[-1]   
                        stack.append(head)
                        stack.append(parse_table[int(state)][len(
                            terminals) + nonterminals.index(head)])
                    i += 1
        elif get_action == "acc":
            string_table.append("ACCEPTED")
            break
        else:
            string_table.append("blank")
            print("ERROR: Unrecognized symbol", curr_symbol, "|")
            break
    temp = int(len(string_table)/4)
    result = np.reshape(string_table, (temp, 4))
    print(tabulate(result, header, tablefmt="orgtbl"))


parse_grammar()
items()

global parse_table
parse_table = [["" for c in range(
    len(terminals) + len(nonterminals) + 1)] for r in range(len(C))]
print_info()
make_graph()


# process_input()h

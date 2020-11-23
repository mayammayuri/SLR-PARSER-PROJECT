import pydot
from graphviz import *
import pydotplus
from pydot import Dot, Edge, Node

graph = Digraph(format='png')
#graph = Digraph()
separator = "\n"
file = open("F:\EBOOKS\Third year\Compiler design\lab\project\Items.txt", "r")
doc = file.readlines()
il = int(doc[0][:-1])
for i in range(il):
    ii = ""
    iin = 'I' + str(i) + ':\n'
    ii0 = doc.index(iin)
    if i+1 < il:
        ii1 = 'I' + str(i+1) + ':\n'
        ii1 = doc.index(ii1)
    else:
        ii1 = len(doc)

    for j in range(ii0+1, ii1-1):
        ii = ii + (doc[j].replace("\n", "\\n"))

    iin = iin[:-2]
    print(i,iin,ii)
    graph.node(iin, label=ii)

# print(graph)
edgesfile = open("F:\EBOOKS\Third year\Compiler design\lab\project\Edges.txt", "r")
edg = edgesfile.readlines()
for x in edg:
    txt = x.split("|")
    edge1 = txt[0]
    edge2 = txt[1][:-1]
    graph.edge(edge1, edge2)
    # graph.edge(i)
# graph.view()
#render('dot', 'png', 'fname.dot')

graph.render('Graph', view=False)

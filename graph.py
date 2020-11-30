from graphviz import *

graph = Digraph(format='png')
file = open("Items.txt", "r")
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
    graph.node(iin, label=ii)

gotofile = open("Gotofile.txt", "r")
edgesfile = open("Edges.txt", "r")
edg = edgesfile.readlines()
goto = gotofile.readlines()

for x in edg:
    txt = x.split("|")
    edge1 = txt[0]
    edge2 = txt[1][:-1]
    ed = txt[1][1:]
    e1 = edge1 + ":\n"
    edgelabel = ""
    if int(edge1[1:]) + 1 < il:
        e2 = "I" + str(int(edge1[1:]) + 1) + ":\n"
        i2 = goto.index(e2)
    else:
        i2 = len(goto)
    i1 = goto.index(e1)
    for y in range(i1+1, i2-1):
        n, m = goto[y].split(" -> ")
        if m == ed:
            edgelabel = n
    graph.edge(edge1, edge2, label=edgelabel)

graph.render('Graph', view=True)

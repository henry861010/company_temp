cdb = CDB()
a = 20
edge1 = [[0,0], [0,a]]
edge2 = [] #[[0,a], [a,a]]
edge3 = [[a,0], [a,a]]
edge4 = [[0,0], [a,0]]
for i in range(0, a+1):
    edge2.append([i, a])

build_block(cdb, 5, edge1, edge2, edge3, edge4)
cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")
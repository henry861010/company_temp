edge1_num = 5
edge4_num = 5

cdb = CDB()
for i in range (1, edge1_num+1):
    for j in range(1, edge4_num+1):
        edge1 = [[0,0]]
        edge2 = [[0,10], [10,10]]
        edge3 = [[10,0], [10,10]]
        edge4 = [[0,0]]
        
        ### reset the cdb
        cdb.reset()

        ### build the edge1 and edge4
        edge1_u = 10/i
        for _ in range(i):
            edge1.append([0, edge1[-1][1]+edge1_u])
        edge4_u = 10/j
        for _ in range(j):
            edge4.append([edge4[-1][0]+edge4_u, 0])
        
        print("### now")
        print(f"    edge1: {edge1}")
        print(f"    edge2: {edge2}")
        print(f"    edge3: {edge3}")
        print(f"    edge4: {edge4}")

        ### test
        build_unit_corner(cdb, edge1, edge2, edge3, edge4)
        cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")
### the rectangle
for i in range(50, 200):
    cdb = CDB()
    
    a = i
    edge1 = [[0,0], [0,a]]
    edge2 = [[0,a], [a,a]]
    edge3 = [[a,a], [a,0]]
    edge4 = [[a,0], [0,0]]
    outline_list = [edge1, edge2, edge3, edge4]
    for i, outline in enumerate(outline_list):
        new_outline = []
        num = int(abs(outline[-1][0] - outline[0][0]) + abs(outline[-1][1] - outline[0][1]))
        x = (outline[-1][0] - outline[0][0]) / num
        y = (outline[-1][1] - outline[0][1]) / num
        for j in range(0, num+1): 
            new_outline.append([outline[0][0]+x*j, outline[0][1]+y*j])
        outline_list[i] = new_outline

    cdb.add_pattern_line([edge1])
    cdb.add_pattern_line([edge2])
    cdb.add_pattern_line([edge3])
    cdb.add_pattern_line([edge4])

    element_size = 3
    start_time = time.time()
    build_layer(cdb_obj = cdb, element_size = element_size, pattern_lines_x = [], pattern_lines_y = [], expanding_list = [[-element_size,0], [0,element_size], [element_size,0], [0,-element_size]], outline_list = outline_list)
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"mesh number: {len(cdb.elements)}")
    print(f"Elapsed time: {elapsed:.8f} seconds")

    #cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")
    
    
    
### second example
for i in range(150,200):
    cdb = CDB()
    
    a = i
    element_size = 3
    edge1 = [[0,0], [a,0]]
    edge2 = [[a,0], [a,a]]
    edge3 = [[a,a], [2*a,a]]
    edge4 = [[2*a,a], [2*a,0]]
    edge5 = [[2*a,0], [3*a,0]]
    edge6 = [[3*a,0], [3*a,-a]]
    edge7 = [[3*a,-a], [2*a,-a]]
    edge8 = [[2*a,-a], [2*a,-2*a]]
    edge9 = [[2*a,-2*a], [a,-2*a]]
    edge10 = [[a,-2*a], [a,-a]]
    edge11 = [[a,-a], [0,-a]]
    edge12 = [[0,-a], [0,0]]
    outline_list = [edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, edge9, edge10, edge11, edge12]
    for i, outline in enumerate(outline_list):
        new_outline = []
        num = int(abs(outline[-1][0] - outline[0][0]) + abs(outline[-1][1] - outline[0][1]))
        x = (outline[-1][0] - outline[0][0]) / num
        y = (outline[-1][1] - outline[0][1]) / num
        for j in range(0, num+1): 
            new_outline.append([outline[0][0]+x*j, outline[0][1]+y*j])
        outline_list[i] = new_outline

    expanding1 = [0,element_size]
    expanding2 = [-element_size,0]
    expanding3 = [0,element_size]
    expanding4 = [element_size,0]
    expanding5 = [0,element_size]
    expanding6 = [element_size,0]
    expanding7 = [0,-element_size]
    expanding8 = [element_size,0]
    expanding9 = [0,-element_size]
    expanding10 = [-element_size,0]
    expanding11 = [0,-element_size]
    expanding12 = [-element_size,0]
    expanding_list = [expanding1, expanding2, expanding3, expanding4, expanding5, expanding6, expanding7, expanding8, expanding9, expanding10, expanding11, expanding12]

    cdb.add_pattern_line([edge1])
    cdb.add_pattern_line([edge2])
    cdb.add_pattern_line([edge3])
    cdb.add_pattern_line([edge4])
    cdb.add_pattern_line([edge5])
    cdb.add_pattern_line([edge6])
    cdb.add_pattern_line([edge7])
    cdb.add_pattern_line([edge8])
    cdb.add_pattern_line([edge9])
    cdb.add_pattern_line([edge10])
    cdb.add_pattern_line([edge11])
    cdb.add_pattern_line([edge12])

    start_time = time.time()
    build_layer(cdb_obj = cdb, element_size = element_size, pattern_lines_x = [], pattern_lines_y = [], expanding_list = expanding_list , outline_list = outline_list)
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"mesh number: {len(cdb.elements)}")
    print(f"Elapsed time: {elapsed:.8f} seconds")

    #cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")



### Third example
cdb = CDB()

a = 3
element_size = 3
edge1 = [[0,0], [a,0]]
edge2 = [[a,0], [a,-a]]
edge3 = [[a,-a], [2*a,-a]]
edge4 = [[2*a,-a], [2*a,-2*a]]
edge5 = [[2*a,-2*a], [3*a,-2*a]]
edge6 = [[3*a,-2*a], [3*a,-3*a]]
edge7 = [[3*a,-3*a], [0,-3*a]]
edge8 = [[0,-3*a], [0,0]]
outline_list = [edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8]
for i, outline in enumerate(outline_list):
    new_outline = []
    num = int(abs(outline[-1][0] - outline[0][0]) + abs(outline[-1][1] - outline[0][1]))
    x = (outline[-1][0] - outline[0][0]) / num
    y = (outline[-1][1] - outline[0][1]) / num
    for j in range(0, num+1): 
        new_outline.append([outline[0][0]+x*j, outline[0][1]+y*j])
    outline_list[i] = new_outline

expanding1 = [0,element_size]
expanding2 = [element_size,0]
expanding3 = [0,element_size]
expanding4 = [element_size,0]
expanding5 = [0,element_size]
expanding6 = [element_size,0]
expanding7 = [0,-element_size]
expanding8 = [-element_size,0]
expanding_list = [expanding1, expanding2, expanding3, expanding4, expanding5, expanding6, expanding7, expanding8]

cdb.add_pattern_line([edge1])
cdb.add_pattern_line([edge2])
cdb.add_pattern_line([edge3])
cdb.add_pattern_line([edge4])
cdb.add_pattern_line([edge5])
cdb.add_pattern_line([edge6])
cdb.add_pattern_line([edge7])
cdb.add_pattern_line([edge8])

start_time = time.time()
build_layer(cdb_obj = cdb, element_size = element_size, pattern_lines_x = [], pattern_lines_y = [], expanding_list = expanding_list , outline_list = outline_list)
end_time = time.time()
elapsed = end_time - start_time
print(f"mesh number: {len(cdb.elements)}")
print(f"Elapsed time: {elapsed:.8f} seconds")

cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")
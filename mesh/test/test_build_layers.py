cdb = CDB()
    
a = 100
element_size = 1
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

cdb.add_pattern_line([edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8])

pattern_lines_y = [[[-100, 50], [100, 50]]]
pattern_lines_x = [[[50, -100], [50, 100]]]
cdb.add_pattern_line(pattern_lines_x)
cdb.add_pattern_line(pattern_lines_y)

start_time = time.time()
build_layers(cdb_obj = cdb, element_sizes = [3,9,27], pattern_lines_x = pattern_lines_x, pattern_lines_y = pattern_lines_y, outline_list = outline_list)
end_time = time.time()
elapsed = end_time - start_time
print(f"mesh number: {len(cdb.elements)}")
print(f"Elapsed time: {elapsed:.8f} seconds")

cdb.show_graph(f"edge1: {len(edge1)-1}, edge4: {len(edge4)-1}")

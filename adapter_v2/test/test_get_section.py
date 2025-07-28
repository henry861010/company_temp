from adapter_wrap import get_section

a = 100
element_size = 2
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

section_list = get_section(outline_list, expanding_list, [], [])

for section in section_list:
    print(section["type"])
    if section["type"] == "LINE":
        print(f"    sub section len: {len(section["sub_section"])}")
        for sub_section in section["sub_section"]:
            edge1 = sub_section["edge1"]
            edge2 = sub_section["edge2"]
            edge3 = sub_section["edge3"]
            edge4 = sub_section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
            print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
    elif section["type"] == "INNER":
        edge1 = section["edge1"]
        edge2 = section["edge2"]
        edge3 = section["edge3"]
        edge4 = section["edge4"]
        print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
        print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
        print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
        print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
    elif section["type"] == "OUTER":
        edge1 = section["edge1"]
        edge2 = section["edge2"]
        edge3 = section["edge3"]
        edge4 = section["edge4"]
        print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
        print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
        print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
        print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
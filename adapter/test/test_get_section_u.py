import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from adapter_get_section import *

a = 100
element_size = 10
edge1 = [[0,0], [0,2*a]]
edge2 = [[0,2*a], [a, 2*a]]
edge3 = [[a, 2*a], [a, a]]
edge4 = [[a, a], [3*a, a]]
edge5 = [[3*a, a], [3*a, 2*a]]
edge6 = [[3*a, 2*a], [4*a, 2*a]]
edge7 = [[4*a, 2*a], [4*a, 0]]
edge8 = [[4*a, 0], [0,0]]
outline_list = [edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8]
for i, outline in enumerate(outline_list):
    new_outline = []
    num = int(abs(outline[-1][0] - outline[0][0]) + abs(outline[-1][1] - outline[0][1]))
    x = (outline[-1][0] - outline[0][0]) / num
    y = (outline[-1][1] - outline[0][1]) / num
    for j in range(0, num+1, element_size): 
        new_outline.append([outline[0][0]+x*j, outline[0][1]+y*j])
    outline_list[i] = new_outline

expanding_unit = 4
expanding1 = [-expanding_unit, 0]
expanding2 = [0, expanding_unit]
expanding3 = [expanding_unit, 0]
expanding4 = [0, expanding_unit]
expanding5 = [-expanding_unit, 0]
expanding6 = [0, expanding_unit]
expanding7 = [expanding_unit, 0]
expanding8 = [0, -expanding_unit]
expanding_list = [expanding1, expanding2, expanding3, expanding4, expanding5, expanding6, expanding7, expanding8]

pattern_lines_vertical = []

#line1 = [[108, -50], [108, 300]]
#pattern_lines_vertical = [line1]

#line1 = [[120, -50], [120, 300]]
#pattern_lines_vertical = [line1]

#line1 = [[119, 104], [119, 300]]
#line2 = [[120, -50], [120, 300]]
#pattern_lines_vertical = [line1, line2]

#line1 = [[110, -50], [110, 300]]
#pattern_lines_vertical = [line1]


pattern_lines_vertical_list = []
for i in range(5):
    random.seed(i)
    pattern_lines_vertical = []
    line_num = random.randint(1, 10)
    for _ in range(line_num):
        x = (random.randint(a+expanding_unit, 3*a-expanding_unit)//element_size) * element_size
        y1 = random.randint(-a, 3*a)
        y2 = random.randint(-a, 3*a)
        pattern_lines_vertical.append([[x, min(y1,y2)], [x, max(y1,y2)]])
    pattern_lines_vertical_list.append(pattern_lines_vertical)
'''
line1 = [[150, 104], [150, 300]]
line2 = [[150, 104], [150, 300]]
pattern_lines_vertical = [line1, line2]
pattern_lines_vertical_list = [pattern_lines_vertical]
'''  
for pattern_lines_vertical in pattern_lines_vertical_list:
    pattern_lines_vertical = sorted(pattern_lines_vertical, key=lambda pair: pair[0][0])
    section_list = adapter_get_section(outline_list, expanding_list, pattern_lines_vertical, [])

    result_lines = []
    for section in section_list:
        print(section["type"])
        if section["type"] == "LINE":
            edge1 = section["edge1"]
            edge2 = section["edge2"]
            edge3 = section["edge3"]
            edge4 = section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
            print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
            result_lines.append([edge1[0], edge1[-1]])
            result_lines.append([edge2[0], edge2[-1]])
            result_lines.append([edge3[0], edge3[-1]])
            result_lines.append([edge4[0], edge4[-1]])
        elif section["type"] == "OUTER":
            edge1 = section["edge1"]
            edge2 = section["edge2"]
            edge3 = section["edge3"]
            edge4 = section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
            print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
            result_lines.append([edge1[0], edge1[-1]])
            result_lines.append([edge2[0], edge2[-1]])
            result_lines.append([edge3[0], edge3[-1]])
            result_lines.append([edge4[0], edge4[-1]])
        elif section["type"] == "INNER":
            edge1 = section["edge1"]
            edge2 = section["edge2"]
            edge3 = section["edge3"]
            edge4 = section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
            print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
            result_lines.append([edge1[0], edge1[-1]])
            result_lines.append([edge2[0], edge2[-1]])
            result_lines.append([edge3[0], edge3[-1]])
            result_lines.append([edge4[0], edge4[-1]])
        elif section["type"] == "INNER_LEFT":
            edge1 = section["edge1"]
            edge2 = section["edge2"]
            edge3 = section["edge3"]
            edge4 = section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
            print(f"    edge2({len(edge2)}) - {edge2}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
            result_lines.append([edge1[0], edge1[-1]])
            result_lines.append([edge2[0], edge2[1]])
            result_lines.append([edge2[1], edge2[2]])
            result_lines.append([edge3[0], edge3[-1]])
            result_lines.append([edge4[0], edge4[-1]])
        elif section["type"] == "INNER_RIGHT":
            edge1 = section["edge1"]
            edge2 = section["edge2"]
            edge3 = section["edge3"]
            edge4 = section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1}")
            print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
            result_lines.append([edge1[0], edge1[1]])
            result_lines.append([edge1[1], edge1[2]])
            result_lines.append([edge2[0], edge2[-1]])
            result_lines.append([edge3[0], edge3[-1]])
            result_lines.append([edge4[0], edge4[-1]])
        elif section["type"] == "INNER_BOTH":
            edge1 = section["edge1"]
            edge2 = section["edge2"]
            edge3 = section["edge3"]
            edge4 = section["edge4"]
            print(f"    edge1({len(edge1)}) - {edge1[0]}~{edge1[-1]}")
            print(f"    edge2({len(edge2)}) - {edge2[0]}~{edge2[-1]}")
            print(f"    edge3({len(edge3)}) - {edge3[0]}~{edge3[-1]}")
            print(f"    edge4({len(edge4)}) - {edge4[0]}~{edge4[-1]}")
            print(f"    outer: {section["outer"]}")
            
    for line in pattern_lines_vertical:
        x_vals = [line[0][0], line[-1][0]]
        y_vals = [line[0][1], line[-1][1]]
        plt.plot(x_vals, y_vals, color='black', linewidth=1)
    for line in result_lines:
        x_vals = [line[0][0], line[-1][0]]
        y_vals = [line[0][1], line[-1][1]]
        plt.plot(x_vals, y_vals, color='blue', linewidth=1.5)
    plt.gca().set_aspect('equal')
    plt.grid(True)
    plt.show()
    plt.close()
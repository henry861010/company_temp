def cal_expanding(element_size, pattern_lines_x, pattern_lines_y, outline):
    node1_x = outline[0][0]
    node1_y = outline[0][1]
    node2_x = outline[1][0]
    node2_y = outline[1][1]

    dir = get_direction(outline)

    normal_direction = rotate(dir, 270)
    if normal_direction[1] == 1:
        index = 0
        while True:
            ### out of the boundary
            if index == len(pattern_lines_x):
                expand = [0, element_size]
                break

            temp = pattern_lines_x[index]
            temp_node1_x = temp[0][0]
            temp_node1_y = temp[0][1]
            temp_node2_x = temp[1][0]
            temp_node2_y = temp[1][1]

            if temp_node1_y == temp_node2_y and  temp_node1_x <= node1_x and node1_x <= temp_node2_x and node1_y < temp_node1_y:
                expand_y = min(abs(temp_node1_y - node1_y), element_size)
                expand = [0, expand_y]
                break

            index += 1
    elif normal_direction[1] == -1:
        index = len(pattern_lines_x) - 1
        while True:
            ### out of the boundary
            if index < 0:
                expand = [0, -element_size]
                break

            temp = pattern_lines_x[index]
            temp_node1_x = temp[0][0]
            temp_node1_y = temp[0][1]
            temp_node2_x = temp[1][0]
            temp_node2_y = temp[1][1]

            if temp_node1_y == temp_node2_y and temp_node1_x <= node1_x and node1_x <= temp_node2_x and temp_node1_y < node1_y:
                expand_y = -min(abs(temp_node1_y - node1_y), element_size)
                expand = [0, expand_y]
                break

            index += -1
    elif normal_direction[0] == 1:
        index = 0
        while True:
            ### out of the boundary
            if index == len(pattern_lines_y):
                expand = [element_size, 0]
                break

            temp = pattern_lines_y[index]
            temp_node1_x = temp[0][0]
            temp_node1_y = temp[0][1]
            temp_node2_x = temp[1][0]
            temp_node2_y = temp[1][1]

            if temp_node1_x == temp_node2_x and temp_node1_y <= node1_y and node1_y <= temp_node2_y and node1_x < temp_node1_x:
                expand_x = min(abs(temp_node1_x - node1_x), element_size)
                expand = [expand_x, 0]
                break

            index += 1
    elif normal_direction[0] == -1:
        index = len(pattern_lines_y) - 1
        while True:
            ### out of the boundary
            if index < 0:
                expand = [-element_size, 0]
                break
            temp = pattern_lines_y[index]
            temp_node1_x = temp[0][0]
            temp_node1_y = temp[0][1]
            temp_node2_x = temp[1][0]
            temp_node2_y = temp[1][1]

            if temp_node1_x == temp_node2_x and temp_node1_y <= node1_y and node1_y <= temp_node2_y and temp_node1_x < node1_x:
                expand_x = -min(abs(temp_node1_x - node1_x), element_size)
                expand = [expand_x, 0]
                break

            index += -1
    return expand

def det_section(outline):
import math

def get_direction(edge, tolerance = 0.001):
    x = edge[-1][0] - edge[0][0]
    y = edge[-1][1] - edge[0][1]
    
    if abs(x) < tolerance:
        x = 0
    if abs(y) < tolerance:
        y = 0
        
    if x != 0:
        x = x / abs(x)
    if y != 0:
        y = y / abs(y)
        
    if x !=0 and y != 0:
        print("not the edge in x or y")
    return [x, y]

def intersection(edge1, edge2, limit: bool = True, tolerance=0.0001):
    x1, y1 = edge1[0]
    x2, y2 = edge1[-1]
    x3, y3 = edge2[0]
    x4, y4 = edge2[-1]

    denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    if denom == 0:
        return None  # Lines are parallel

    # Compute intersection point (infinite line)
    px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

    # Check if the intersection is within both segments
    def in_range(p, a, b):
        return min(a, b) - tolerance <= p <= max(a, b) + tolerance  # allow small tolerance

    if not limit or (in_range(px, x1, x2) and in_range(py, y1, y2) and in_range(px, x3, x4) and in_range(py, y3, y4)):
        return [px, py]
    else:
        return None  # intersection is outside the segment bounds

def rotate(v, degree, tolerance = 0.0001):
    x = v[0]
    y = v[1]
    theta_rad = math.radians(-degree)  # Convert to radians
    x_new = x * math.cos(theta_rad) - y * math.sin(theta_rad)
    y_new = x * math.sin(theta_rad) + y * math.cos(theta_rad)
    if abs(x_new) < tolerance:
        x_new = 0
    if abs(y_new) < tolerance:
        y_new = 0
    return [x_new, y_new]

def distance(node1, node2):
    len = math.sqrt((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)
    return len

def nearby(node, edge):
    index = 0
    max_d = 1000000000
    for i, temp_node in enumerate(edge):
        temp_d = distance(temp_node, node)
        if temp_d < max_d:
            max_d = temp_d
            index = i
        else:
            break
    return index

def equal_node(node1, node2):
    tolerance = 0.001
    if node1[0] < node2[0] - tolerance or  node2[0] + tolerance < node1[0]:
        return False
    if node1[1] < node2[1] - tolerance or  node2[1] + tolerance < node1[1]:
        return False
    return True

def adapter_get_outline2(outline_list, ref_nodes_list, expaneding_list, pattern_horizon_liness, pattern_vertical_lines):
    inner_node_count = 0
    for outline in outline_list:
        inner_node_count += (len(outline) - 1)

def adapter_get_section(outline1_list, outline2_list, pattern_horizon_liness, pattern_vertical_lines):
    def _get_pattern_lines(dir, pattern_horizon_lines, pattern_vertical_lines):
        if dir[0] > 0 and dir[1] == 0:
            return pattern_horizon_lines
        elif dir[0] < 0 and dir[1] == 0:
            return pattern_horizon_lines[::-1]
        if dir[0] == 0 and dir[1] > 0:
            return pattern_vertical_lines
        elif dir[0] == 0 and dir[1] < 0:
            return pattern_vertical_lines[::-1]
    
    def _adapter_get_corner(short_line, long_line, pattern_lines, isRight=True):
        if isRight:
            ### (0 ~ -1) short_line -> node
            ### (0 ~ -1) long_line -> node
            index_l = min(len(long_line)-2, nearby(node, long_line))
            node_s = short_line[-1]
            node_l = long_line[index_l]
            
            ### check if the pattern line intersect at the long_line[index_l]
            isExtend = False
            for pattern_line in pattern_lines:
                node_i_l = intersection(pattern_line, long_line)
                node_i_s = intersection(pattern_line, short_line)
                if node_i_l is not None and node_i_s is not None and equal_node(node_l, node_i_l):
                    node_s = intersection(pattern_line, short_line)
                    isExtend = True
                    break
            return isExtend, node_s, node_l, index_l
        else:
            ### (0 ~ -1) short_line -> node
            ### (0 ~ -1) long_line -> node
            index_l = max(1, nearby(node, long_line))
            node_s = short_line[0]
            node_l = long_line[index_l]
            
            ### check if the pattern line intersect at the long_line[index_l]
            isExtend = False
            for pattern_line in pattern_lines:
                node_i_l = intersection(pattern_line, long_line)
                node_i_s = intersection(pattern_line, short_line)
                if node_i_l is not None and node_i_s is not None and equal_node(node_l, node_i_l):
                    node_s = intersection(pattern_line, short_line)
                    isExtend = True
                    break
            return isExtend, node_s, node_l, index_l
    
    for index, (outline1, outline2) in enumerate(zip(outline1_list, outline2_list)): 
        ### now
        now_index = index
        outline1_now = outline1_list[now_index]
        outline2_now = outline2_list[now_index]
        dirction1_now = get_direction(outline1_now)
        pattern_lines_now = _get_pattern_lines(dirction_now, pattern_horizon_lines, pattern_vertical_lines)
        
        ### next
        post_index = index
        outline1_post = outline1_list[post_index]
        outline2_post = outline2_list[post_index]
        dirction1_post = get_direction(outline1_post)
        pattern_lines_post = _get_pattern_lines(dirction_post, pattern_horizon_lines, pattern_vertical_lines)
        
        outline1_left = 0
        outline1_right = len(outline1) - 1
        outline2_left = 0
        outline2_right = len(outline2) - 1
        
        ### left corner
        if isLeftInner:
            _, section_node2, section_node1, outline1_left = _adapter_get_corner(outline2_now, outline1_now, pattern_lines_now, isRight=False)
        else:
            _, section_node1, section_node2, outline2_left = _adapter_get_corner(outline1_now, outline2_now, pattern_lines_now, isRight=False)
            
        ### right corner
        if isRightInner:
            isExtend_now, section_node3, section_node4, outline1_right = _adapter_get_corner(outline2_now, outline1_now, pattern_lines_now, isRight=True)
            isExtend_next, _, _, index_r_next = _adapter_get_corner(outline2_post, outline1_post, pattern_lines_post, isRight=False)
            
            right_corner_info = {
                "edge1": [],
                "edge2": [],
                "edge3": [],
                "edge4": []
            }
        else:
            isExtend_now, section_node4, section_node3, outline2_right = _adapter_get_corner(outline1_now, outline2_now, pattern_lines_now, isRight=True)
            isExtend_next, _, _, index_r_next = _adapter_get_corner(outline1_post, outline2_post, pattern_lines_post, isRight=False)
            
            right_corner_info = {
                "edge1": [],
                "edge2": [],
                "edge3": [],
                "edge4": []
            }
            
        ### line
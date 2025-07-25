import numpy as np
import math
import matplotlib.pyplot as plt
import time
import resource
from my_math import *

tolerance = 0.001

def equal_node(node1, node2):
    tolerance = 0.001
    if node1[0] < node2[0] - tolerance or  node2[0] + tolerance < node1[0]:
        return False
    if node1[1] < node2[1] - tolerance or  node2[1] + tolerance < node1[1]:
        return False
    return True
        
def edge_len(edge):
    return distance(edge[0], edge[-1])

def distance(node1, node2):
    len = math.sqrt((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)
    return len

def get_direction(edge):
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

def intersection(edge1, edge2, limit: bool = True):
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

def rotate(v, degree):
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

def next_index(node, edge, edge_index, section_node_num, direction: int = 1):
    ### direction: 
    ###     1 go right
    ###     -1 go left
    
    ### if node at last of its edge, the user should manually handle
    ### outer_index == last -> use "last" as next index
    ### outer_index == 0 -> use "0" as next index
    
    def line_project(line, node):
        v_x = line[-1][0] - line[0][0]
        v_y = line[-1][1] - line[0][1]
        w_x = node[0] - line[0][0]
        w_y = node[1] - line[0][1]
        t = (w_x * v_x + w_y * v_y) / ((v_x * v_x + v_y * v_y))
        project_x = line[0][0] + t * v_x
        project_y = line[0][1] + t * v_y
        return [project_x, project_y]
        
    project = line_project(edge, node)
    vector_x = f_zero(direction * (edge [-1][0] - edge [0][0]))
    vector_y = f_zero(direction * (edge [-1][1] - edge [0][1]))
    node_pre = edge[edge_index]
    index_pre = edge_index

    if section_node_num % 2:
        edge_index = edge_index + 1 * direction
    else:
        edge_index = edge_index + 2 * direction
    
    while 1:
        ### if at the last node, return the last element
        if edge_index == len(edge) or edge_index < 0:
            return index_pre

        node_now = edge[edge_index]
        temp_vector_x = f_zero(project[0] - node_now[0])
        temp_vector_y = f_zero(project[1] - node_now[1])
        if (vector_x < 0 and temp_vector_x < 0) or (vector_x > 0 and temp_vector_x > 0) or (vector_y < 0 and temp_vector_y < 0) or (vector_y > 0 and temp_vector_y > 0):
            node_pre = node_now
            index_pre = edge_index
            edge_index += 2 * direction
        else:
            dis_now = distance(node_now, project)
            dis_pre = distance(node_pre, project)
            if edge_index == (len(edge) - 1) or edge_index == 0:
                ### the first/last inner_node must belong to the first/last outer node, and these situation must be deal at the begin of the function
                return index_pre
            elif dis_now < dis_pre:
                return edge_index
            else:
                return index_pre

def build_unit_normal(cdb_obj: 'Mesh2D', edge1: list, edge2: list, edge3: list, edge4: list):
    if len(edge1)==2 and len(edge2)==2 and len(edge3)==2 and len(edge4)==2:
        cdb_obj.add_element(edge1[0], edge2[0], edge3[-1], edge4[-1])
        return
    
    origin_edge1 = edge1
    origin_edge2 = edge2
    origin_edge3 = edge3
    origin_edge4 = edge4
    if len(edge1) > 2:
        edge1 = origin_edge4
        edge2 = origin_edge3
        edge3 = origin_edge2
        edge4 = origin_edge1
    elif len(edge2) > 2:
        edge1 = origin_edge3[::-1]
        edge2 = origin_edge4[::-1]
        edge3 = origin_edge1[::-1]
        edge4 = origin_edge2[::-1]
    elif len(edge3) > 2:
        edge1 = origin_edge4[::-1]
        edge2 = origin_edge1
        edge3 = origin_edge2[::-1]
        edge4 = origin_edge3
    elif len(edge4) > 2:
        edge1 = origin_edge1
        edge2 = origin_edge2
        edge3 = origin_edge3
        edge4 = origin_edge4  
    else:
        print("????")
        
    node1 = edge1[0]
    node2 = edge2[0]
    node3 = edge3[-1]
    node4 = edge4[-1]
    
    section_num = len(edge4) - 1
    half_num = section_num // 2
    
    if section_num % 2 == 0:
        raise Exception("[build_unit_normal] the number of nodes at edge4 should be even")
    
    ### vector1
    vector1 = edge4[0 : half_num+1]
    vector1.reverse()
    
    ### vector4
    vector4 = edge4[half_num+1:]
    
    ### vector2
    mid1_x = node1[0] + (node4[0] - node1[0]) * half_num / section_num
    mid1_y = node1[1] + (node4[1] - node1[1]) * half_num / section_num
    mid2_x = node2[0] + (node3[0] - node2[0]) * half_num / section_num
    mid2_y = node2[1] + (node3[1] - node2[1]) * half_num / section_num
    mid_x = (mid1_x + mid2_x) / 2
    mid_y = (mid1_y + mid2_y) / 2
    temp_x = mid_x
    temp_y = mid_y
    v_x = (node2[0] - mid_x) / half_num
    v_y = (node2[1] - mid_y) / half_num
    vector2 = []
    for _ in range(half_num+1):
        vector2.append([temp_x, temp_y])
        temp_x += v_x
        temp_y += v_y

    ### vector3
    mid1_x = node1[0] + (node4[0] - node1[0]) * (half_num + 1) / section_num
    mid1_y = node1[1] + (node4[1] - node1[1]) * (half_num + 1) / section_num
    mid2_x = node2[0] + (node3[0] - node2[0]) * (half_num + 1) / section_num
    mid2_y = node2[1] + (node3[1] - node2[1]) * (half_num + 1) / section_num
    mid_x = (mid1_x + mid2_x) / 2
    mid_y = (mid1_y + mid2_y) / 2
    temp_x = mid_x
    temp_y = mid_y
    v_x = (node3[0] - mid_x) / half_num
    v_y = (node3[1] - mid_y) / half_num
    vector3 = []
    for _ in range(half_num+1):
        vector3.append([temp_x, temp_y])
        temp_x += v_x
        temp_y += v_y
    
    ### build the element
    ### center_node
    cdb_obj.add_element(vector1[0], vector2[0], vector3[0], vector4[0])
    for i in range(1, half_num+1):
        ### left
        cdb_obj.add_element(vector1[i-1], vector1[i], vector2[i], vector2[i-1])
        
        ### center
        cdb_obj.add_element(vector2[i-1], vector2[i], vector3[i], vector3[i-1])
        
        ### right
        cdb_obj.add_element(vector3[i-1], vector3[i], vector4[i], vector4[i-1])
        
    return [origin_edge1, origin_edge2, origin_edge3, origin_edge4]

def build_unit_corner(cdb_obj: 'Mesh2D', edge1: list, edge2: list, edge3: list, edge4: list):
    origin_edge1 = edge1
    origin_edge2 = edge2
    origin_edge3 = edge3
    origin_edge4 = edge4
    if len(edge1) > 2 and len(edge2) > 2:
        edge1 = origin_edge2
        edge2 = origin_edge3[::-1]
        edge3 = origin_edge4
        edge4 = origin_edge1[::-1]
    elif len(edge2) > 2 and len(edge3) > 2:
        edge1 = origin_edge3[::-1]
        edge2 = origin_edge4[::-1]
        edge3 = origin_edge1[::-1]
        edge4 = origin_edge2[::-1]
    elif len(edge3) > 2 and len(edge4) > 2:
        edge1 = origin_edge4[::-1]
        edge2 = origin_edge1
        edge3 = origin_edge2[::-1]
        edge4 = origin_edge3
    else:
        edge1 = origin_edge1
        edge2 = origin_edge2
        edge3 = origin_edge3
        edge4 = origin_edge4    
        
    node1 = edge1[0]
    node2 = edge2[0]
    node3 = edge3[-1]
    node4 = edge4[-1]
    
    #if len(edge1) == 2 and len(edge2) == 2 and len(edge3) == 2 and len(edge4) == 2:
    #    cdb_obj.add_element(edge1[0], edge1[1], edge3[1], edge3[0])
    #    return [origin_edge1, origin_edge2, origin_edge3, origin_edge4]
    if (len(edge1) + len(edge2) + len(edge3) + len(edge4)) % 2 == 0:
        if len(edge1) > len(edge4):
            l_edge = edge1
            s_edge = edge4
            lr_edge = edge3
            sr_edge = edge2
        else:
            l_edge = edge4
            s_edge = edge1
            lr_edge = edge2
            sr_edge = edge3
        
        l_begin = 1 + len(l_edge) - len(s_edge)
        s_begin = 1
        outer_section_num = len(s_edge) - 2
        
        ### mid point
        if len(s_edge) == 1:
            mid = lr_edge[-1]
        else:
            temp1 = l_edge[l_begin]
            temp3_x = lr_edge[0][0] + (distance(l_edge[l_begin], l_edge[0])/distance(l_edge[-1], l_edge[0])) * (lr_edge[-1][0] - lr_edge[0][0])
            temp3_y = lr_edge[0][1] + (distance(l_edge[l_begin], l_edge[0])/distance(l_edge[-1], l_edge[0])) * (lr_edge[-1][1] - lr_edge[0][1])
            temp3 = [temp3_x, temp3_y] 
            temp2_x = sr_edge[0][0] + (distance(s_edge[s_begin], s_edge[0])/distance(s_edge[-1], s_edge[0])) * (sr_edge[-1][0] - sr_edge[0][0])
            temp2_y = sr_edge[0][1] + (distance(s_edge[s_begin], s_edge[0])/distance(s_edge[-1], s_edge[0])) * (sr_edge[-1][1] - sr_edge[0][1])
            temp2 = [temp2_x, temp2_y] 
            temp4 = s_edge[s_begin]
            temp_edge1 = [[temp1[0], temp1[1]], [temp3[0], temp3[1]]]
            temp_edge2 = [[temp4[0], temp4[1]], [temp2[0], temp2[1]]]
            mid = intersection(temp_edge1, temp_edge2)
        
        ### build the inner part
        temp_edge1 = l_edge[0:l_begin+1]
        temp_edge2 = [l_edge[l_begin], mid]
        temp_edge3 = [s_edge[s_begin], mid]
        temp_edge4 = s_edge[0:s_begin+1]
        build_unit_normal(cdb_obj, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
        
        ### build the other layer - build vector
        if outer_section_num > 0:
            vector1 = l_edge[l_begin:]
            vector3 = s_edge[s_begin:]
            temp_x = mid[0]
            temp_y = mid[1]
            v_x = (node3[0] - mid[0]) / outer_section_num
            v_y = (node3[1] - mid[1]) / outer_section_num
            vector2 = []
            for _ in range(outer_section_num+1):
                vector2.append([temp_x, temp_y])
                temp_x += v_x
                temp_y += v_y
                
            ### build the other layer - build element
            for i in range(len(vector1)):
                ### right
                cdb_obj.add_element(vector1[i-1], vector1[i], vector2[i], vector2[i-1])
                
                ### left
                cdb_obj.add_element(vector2[i-1], vector2[i], vector3[i], vector3[i-1])    
        return [origin_edge1, origin_edge2, origin_edge3, origin_edge4]    
    else:
        if len(edge1) > len(edge4):
            l_edge = edge1
            s_edge = edge4
            lr_edge = edge3
            sr_edge = edge2
        else:
            l_edge = edge4
            s_edge = edge1
            lr_edge = edge2
            sr_edge = edge3
        print(f"        ~l_edge: {len(l_edge)}, s_edge: {len(s_edge)}, lr_edge: {len(lr_edge)}, sr_edge: {len(sr_edge)}")

        l_begin = 1 + len(l_edge) - len(s_edge)
        l_mid_index =  l_begin // 2 | 1 
        s_begin = 1
        outer_section_num = len(s_edge) - 2
        
        ### mid1 point
        if len(s_edge) == 1:
            mid2 = lr_edge[-1]
        else:
            ### calculate the mid2
            temp1 = l_edge[l_begin]
            temp3_x = lr_edge[0][0] + (distance(l_edge[l_begin], l_edge[0])/distance(l_edge[-1], l_edge[0])) * (lr_edge[-1][0] - lr_edge[0][0])
            temp3_y = lr_edge[0][1] + (distance(l_edge[l_begin], l_edge[0])/distance(l_edge[-1], l_edge[0])) * (lr_edge[-1][1] - lr_edge[0][1])
            temp3 = [temp3_x, temp3_y] 
            temp2_x = sr_edge[0][0] + (distance(s_edge[s_begin], s_edge[0])/distance(s_edge[-1], s_edge[0])) * (sr_edge[-1][0] - sr_edge[0][0])
            temp2_y = sr_edge[0][1] + (distance(s_edge[s_begin], s_edge[0])/distance(s_edge[-1], s_edge[0])) * (sr_edge[-1][1] - sr_edge[0][1])
            temp2 = [temp2_x, temp2_y] 
            temp4 = s_edge[s_begin]
            temp_edge1 = [[temp1[0], temp1[1]], [temp3[0], temp3[1]]]
            temp_edge2 = [[temp4[0], temp4[1]], [temp2[0], temp2[1]]]
            mid2 = intersection(temp_edge1, temp_edge2)
            
        ### calculate the mid1
        mid1_x = s_edge[1][0] + (mid2[0] - s_edge[1][0]) * (distance(l_edge[l_mid_index], l_edge[0])/distance(l_edge[l_begin], l_edge[0]))
        mid1_y = s_edge[1][1] + (mid2[1] - s_edge[1][1]) * (distance(l_edge[l_mid_index], l_edge[0])/distance(l_edge[l_begin], l_edge[0]))
        mid1 = [mid1_x, mid1_y]
        
        ### calculate the mid1_o
        mid1_o_x = s_edge[-1][0] + (lr_edge[-1][0] - s_edge[-1][0]) * (distance(l_edge[l_mid_index], l_edge[0])/distance(l_edge[l_begin], l_edge[0]))
        mid1_o_y = s_edge[-1][1] + (lr_edge[-1][1] - s_edge[-1][1]) * (distance(l_edge[l_mid_index], l_edge[0])/distance(l_edge[l_begin], l_edge[0]))
        mid1_o = [mid1_o_x, mid1_o_y]
            
        ### build the inner part (low)
        temp_edge1 = l_edge[0 : l_mid_index+1]
        temp_edge2 = [l_edge[l_mid_index], mid1]
        temp_edge3 = [s_edge[1], mid1]
        temp_edge4 = [l_edge[0],s_edge[1]]
        build_unit_normal(cdb_obj,temp_edge1, temp_edge2, temp_edge3, temp_edge4)

        ### build the inner part (top)
        temp_edge1 = l_edge[l_mid_index : l_begin+1]
        temp_edge2 = [l_edge[l_begin], mid2]
        temp_edge3 = [mid1, mid2]
        temp_edge4 = [l_edge[l_mid_index],mid1]
        build_unit_normal(cdb_obj,temp_edge1, temp_edge2, temp_edge3, temp_edge4)
        
        ### vector1
        if outer_section_num > 0:
            vector1 = l_edge[l_begin:]
            vector4 = s_edge[s_begin:]
            temp_x = mid2[0]
            temp_y = mid2[1]
            v_x = (node3[0] - mid2[0]) / outer_section_num
            v_y = (node3[1] - mid2[1]) / outer_section_num
            vector2 = []
            for _ in range(outer_section_num+1):
                vector2.append([temp_x, temp_y])
                temp_x += v_x
                temp_y += v_y
            temp_x = mid1[0]
            temp_y = mid1[1]
            v_x = (mid1_o[0] - mid1[0]) / outer_section_num
            v_y = (mid1_o[1] - mid1[1]) / outer_section_num
            vector3 = []
            for _ in range(outer_section_num+1):
                vector3.append([temp_x, temp_y])
                temp_x += v_x
                temp_y += v_y

            ### build the other layer - build element
            for i in range(len(vector1)):
                ### right
                cdb_obj.add_element(vector1[i-1], vector1[i], vector2[i], vector2[i-1])
                
                ### top
                cdb_obj.add_element(vector2[i-1], vector2[i], vector3[i], vector3[i-1])
                
                ### low
                cdb_obj.add_element(vector3[i-1], vector3[i], vector4[i], vector4[i-1])
                
        ### build the new edge1/2/3/4 (would add new node at the lr_edge)
        if len(origin_edge1) > 2 and len(origin_edge2) > 2:
            if len(origin_edge1) > len(origin_edge2):
                origin_edge3.insert(1, mid1_o)
            else:
                origin_edge4.insert(1, mid1_o)
        elif len(origin_edge2) > 2 and len(origin_edge3) > 2:
            if len(origin_edge2) > len(origin_edge3):
                origin_edge4.insert(1, mid1_o)
            else:
                origin_edge1.insert(1, mid1_o)
        elif len(origin_edge3) > 2 and len(origin_edge4) > 2:
            if len(origin_edge3) > len(origin_edge4):
                origin_edge1.insert(1, mid1_o)
            else:
                origin_edge2.insert(1, mid1_o)
        elif len(origin_edge4) > 2 and len(origin_edge1) > 2:
            if len(origin_edge4) > len(origin_edge1):
                origin_edge2.insert(1, mid1_o)
            else:
                origin_edge3.insert(1, mid1_o)
        return [origin_edge1, origin_edge2, origin_edge3, origin_edge4]

def build_unit_spe1(cdb_obj: 'Mesh2D', edge1: list, edge2: list, edge3: list, edge4: list):
    ### 2-1-2-O
    print("build  2-1-2-O")

def build_block(cdb_obj: 'Mesh2D', element_size: int ,edge1: list, edge2: list, edge3: list, edge4: list):
    origin_edge1 = edge1
    origin_edge2 = edge2
    origin_edge3 = edge3
    origin_edge4 = edge4
    
    max_len_edge = max(len(edge1), len(edge2), len(edge3), len(edge4))
    if max_len_edge == len(origin_edge4):
        edge1 = origin_edge1
        edge2 = origin_edge2
        edge3 = origin_edge3
        edge4 = origin_edge4
    elif max_len_edge == len(origin_edge1):
        edge1 = origin_edge2
        edge2 = origin_edge3[::-1]
        edge3 = origin_edge4
        edge4 = origin_edge1[::-1]
    elif max_len_edge == len(origin_edge2):
        edge1 = origin_edge3[::-1]
        edge2 = origin_edge4[::-1]
        edge3 = origin_edge1[::-1]
        edge4 = origin_edge2[::-1]
    elif max_len_edge == len(origin_edge3):
        edge1 = origin_edge4[::-1]
        edge2 = origin_edge1
        edge3 = origin_edge2[::-1]
        edge4 = origin_edge3
        
    ### calculate how many section at edge4 would be split
    target_section_num = max(round(edge_len(edge2) / element_size), 1)
    if (target_section_num + (len(edge1) + len(edge3) + len(edge4) - 3)) % 2 == 1:
        if target_section_num == 1:
            target_section_num += 1
        else:
            target_section_num -= 1
    
    ### determine the outer node
    ### there are several reference node at the edge, we should consider it while we mesh.
    ### we call the distance between the reference node are "bucket"
    ###     * bucket_num: the number of the section in it
    ###     * bucket_dis: the distance of the bucket
    bucket_num = []
    bucket_dis = []
    for i in range(1, len(edge2)):
        bucket_num.append(1)
        bucket_dis.append(distance(edge2[i-1], edge2[i]))
    
    for i in range(len(edge2)-1, target_section_num):
        ### find the bucket where each section in it have maximum len
        max_len = -1
        max_index = -1
        for j in range(len(bucket_dis)):
            temp_len = bucket_dis[j] / (bucket_num[j] + 1)
            if temp_len > max_len:
                max_len = temp_len
                max_index = j

        ### find it and add the section to this found bucket
        bucket_num[max_index] = bucket_num[max_index] + 1
    
    new_edge2 = []
    for i in range(0, len(bucket_num)):
        v_x = (edge2[i+1][0] - edge2[i][0]) / bucket_num[i]
        v_y = (edge2[i+1][1] - edge2[i][1]) / bucket_num[i]
        temp = [edge2[i]]
        for _ in range(bucket_num[i]):
            temp.append([temp[-1][0]+v_x, temp[-1][1]+v_y])

        new_edge2 = new_edge2[:-1] + temp

    ### build the unit 
    left_index = 0
    left_outer_index = 0
    left_edge = edge1
    
    right_index = len(edge4) - 1
    right_outer_index = len(new_edge2) - 1
    right_edge = edge3
    
    count = 0
    while True:
        ### if finish get out from the while loop
        count += 1
        if count == len(new_edge2): 
            break
        
        ### build the left unit
        now_node = new_edge2[left_outer_index]
        next_node = new_edge2[left_outer_index + 1]
        if count == len(new_edge2)-1:
            next_left_index = right_index
        else:
            next_left_index = next_index(next_node, edge4, left_index, len(left_edge)-1, 1)
        
        temp_edge1 = left_edge
        temp_edge2 = [now_node, next_node]
        temp_edge3 = [edge4[next_left_index], next_node]
        temp_edge4 = edge4[left_index : next_left_index+1]
        
        ### build
        build_unit_corner(cdb_obj, temp_edge1, temp_edge2, temp_edge3, temp_edge4)

        ### update the temp var
        left_index = next_left_index
        left_outer_index = left_outer_index + 1
        left_edge = temp_edge3
        
        ### if finish get out from the while loop
        count += 1
        if count == len(new_edge2): 
            break
        
        ### build the right unit
        now_node = new_edge2[right_outer_index]
        next_node = new_edge2[right_outer_index - 1]
        if count == len(new_edge2)-1:
            next_right_index = left_index
        else:
            next_right_index = next_index(next_node, edge4, right_index, len(right_edge)-1, -1)
        
        temp_edge3 = right_edge
        temp_edge2 = [next_node, now_node]
        temp_edge1 = [edge4[next_right_index], next_node]
        temp_edge4 = edge4[next_right_index : right_index+1]
                
        ### build
        build_unit_corner(cdb_obj, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
        
        ### update the temp var
        right_index = next_right_index
        right_outer_index = right_outer_index - 1
        right_edge = temp_edge3

    if max_len_edge == len(origin_edge4):
        origin_edge2 = new_edge2
    elif max_len_edge == len(origin_edge1):
        origin_edge3 = new_edge2[::-1]
    elif max_len_edge == len(origin_edge2):
        origin_edge4 = new_edge2[::-1]
    elif max_len_edge == len(origin_edge3):
        origin_edge1 = new_edge2
        
    return [origin_edge1, origin_edge2, origin_edge3, origin_edge4]

def build_block_pattern(cdb_obj: 'Mesh2D', element_size: int, pattern_lines_x: list, pattern_lines_y: list ,edge1: list, edge2: list, edge3: list, edge4: list):
    origin_edge1 = edge1
    origin_edge2 = edge2
    origin_edge3 = edge3
    origin_edge4 = edge4
    max_len = max(len(edge1), len(edge2), len(edge3), len(edge4))
    if max_len == len(origin_edge4):
        edge1 = origin_edge1
        edge2 = origin_edge2
        edge3 = origin_edge3
        edge4 = origin_edge4
    elif max_len == len(origin_edge1):
        edge1 = origin_edge2
        edge2 = origin_edge3[::-1]
        edge3 = origin_edge4
        edge4 = origin_edge1[::-1]
    elif max_len == len(origin_edge2):
        edge1 = origin_edge3[::-1]
        edge2 = origin_edge4[::-1]
        edge3 = origin_edge1[::-1]
        edge4 = origin_edge2[::-1]
    elif max_len == len(origin_edge3):
        edge1 = origin_edge4[::-1]
        edge2 = origin_edge1
        edge3 = origin_edge2[::-1]
        edge4 = origin_edge3
    else:
        print("~~~~~")
    
    dir = get_direction(edge2)
    if dir[0] != 0:
        pattern_lines = pattern_lines_x
    else:
        pattern_lines = pattern_lines_y
    
    post_index = 0
    begin_index = 0
    new_edge2 = [edge2[0]]
    section_list = [edge2[0]]
    left_edge = edge1
    ### OPTIMIZE: now, each time the function called, all the pattern_line would be looped once(there is no early break or quick search(binary search))
    for pattern_line in pattern_lines:
        inner_intersection = intersection(pattern_line, edge4)
        outer_intersection = intersection(pattern_line, edge2)
        
        if outer_intersection is not None:
            ### append the outer intersection node to section_lis if it is not exist in section_list
            if not equal_node(outer_intersection, section_list[-1]):
                section_list.append(outer_intersection)
                
            ### if there is intersection between the edge4 and patttern line, the section end and builld the block
            if inner_intersection is not None:
                ### find the correspond index of inner intersection at edge4
                begin_index = post_index
                post_index += 1
                while not equal_node(inner_intersection, edge4[post_index]):
                    post_index += 1
                    
                if post_index == len(edge4)-1:
                    break
        
                ### build the block        
                temp_edge1 = left_edge
                temp_edge2 = section_list
                temp_edge3 = [inner_intersection, outer_intersection]
                temp_edge4 = edge4[begin_index : post_index+1]

                res = build_block(cdb_obj, element_size, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
                
                ### update new_edge2
                new_edge2 = new_edge2 + res[1][1:]
                
                ### reset
                section_list = [section_list[-1]]
                left_edge = res[2]

    ### [last block] build the last block which use the edge3 as its edge3
    begin_index = post_index
    if not equal_node(section_list[-1], edge2[-1]):
        section_list.append(edge2[-1])
    temp_edge1 = left_edge
    temp_edge2 = section_list
    temp_edge3 = edge3
    temp_edge4 = edge4[begin_index:]
    res = build_block(cdb_obj, element_size, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
    new_edge2 = new_edge2 + res[1][1:]
    
    if max_len == len(origin_edge4):
        origin_edge2 = new_edge2
    elif max_len == len(origin_edge1):
        origin_edge1 = new_edge2
    elif max_len == len(origin_edge2):
        origin_edge4 = new_edge2[::-1]
    elif max_len == len(origin_edge3):
        origin_edge3 = new_edge2[::-1]
    
    return [origin_edge1, origin_edge2, origin_edge3, origin_edge4]

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

def build_layer(cdb_obj: 'Mesh2D', element_size: int, pattern_lines_x: list, pattern_lines_y: list, expanding_list: list, outline_list: list):
    new_outline_list = []
    
    ### outer ncorner
    direction_pre_90 = rotate(get_direction(outline_list[-1]), 90)
    direction_now = get_direction(outline_list[0])
    if direction_pre_90 == direction_now:
        node1_x = outline_list[0][0][0] + expanding_list[-1][0]
        node1_y = outline_list[0][0][1] + expanding_list[-1][1]
        node2_x = outline_list[0][0][0] + expanding_list[-1][0] + expanding_list[0][0]
        node2_y = outline_list[0][0][1] + expanding_list[-1][1] + expanding_list[0][1]
        node3_x = outline_list[0][0][0] + expanding_list[0][0]
        node3_y = outline_list[0][0][1] + expanding_list[0][1]
        node4_x = outline_list[0][0][0]
        node4_y = outline_list[0][0][1]
        
        temp_edge1 = [[node1_x, node1_y], [node2_x, node2_y]]
        temp_edge2 = [[node2_x, node2_y], [node3_x, node3_y]]
        temp_edge3 = [[node4_x, node4_y], [node3_x, node3_y]]
        temp_edge4 = [[node1_x, node1_y], [node4_x, node4_y]]
        
        res_corner = build_block(cdb_obj, element_size, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
        next_edge1 = res_corner[2]
        next_left_outer_node_list = res_corner[1]
        last_edge3 = res_corner[3][::-1]
        last_right_outer_node_list = res_corner[0]
    else:
        node1_x = outline_list[0][0][0]
        node1_y = outline_list[0][0][1]
        node3_x = outline_list[0][0][0] + expanding_list[-1][0] + expanding_list[0][0]
        node3_y = outline_list[0][0][1] + expanding_list[-1][1] + expanding_list[0][1]
        node2_index = nearby([node3_x, node3_y], outline_list[-1])
        node4_index = nearby([node3_x, node3_y], outline_list[0])

        temp_edge1 = outline_list[-1][node2_index:][::-1]
        temp_edge2 = [outline_list[-1][node2_index], [node3_x, node3_y]]
        temp_edge3 = [outline_list[0][node4_index], [node3_x, node3_y]]
        temp_edge4 = outline_list[0][0:node2_index+1]
        
        res_corner = build_unit_corner(cdb_obj, element_size, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
        next_edge1 = res_corner[2]
        next_left_outer_node_list = []
        last_edge3 = res_corner[1]
        last_right_outer_node_list = []
        
    for i, outline in enumerate(outline_list):
        post = (i + 1) % len(outline_list)
        direction_post_270 = rotate(get_direction(outline_list[post]), 270)
        direction_now = get_direction(outline_list[i])
        
        center_edge1 = next_edge1
        center_left_outer_node_list = next_left_outer_node_list
        
        ### build the right corner
        if i == len(outline_list)-1:
            center_edge3 = last_edge3
            center_right_outer_node_list = last_right_outer_node_list
        elif direction_pre_270 == direction_now:
            ### outer corner
            node1_x = outline_list[i][-1][0]
            node1_y = outline_list[i][-1][1]
            node2_x = outline_list[i][-1][0] + expanding_list[i][0]
            node2_y = outline_list[i][-1][1] + expanding_list[i][1]
            node3_x = outline_list[i][-1][0] + expanding_list[i][0] + expanding_list[post][0]
            node3_y = outline_list[i][-1][1] + expanding_list[i][1] + expanding_list[post][1]
            node4_x = outline_list[i][-1][0] + expanding_list[post][0]
            node4_y = outline_list[i][-1][1] + expanding_list[post][1]
            
            temp_edge1 = [[node1_x, node1_y], [node2_x, node2_y]]
            temp_edge2 = [[node2_x, node2_y], [node3_x, node3_y]]
            temp_edge3 = [[node4_x, node4_y], [node3_x, node3_y]]
            temp_edge4 = [[node1_x, node1_y], [node4_x, node4_y]]
            
            res_corner = build_block(cdb_obj, element_size, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
            next_edge1 = res_corner[3]
            next_left_outer_node_list = res_corner[2][::-1]
            center_edge3 = res_corner[0]
            center_right_outer_node_list = res_corner[1]
        else:
            ### inner corner
            node2_x = outline_list[i][-1][0] + expanding_list[i][0] + expanding_list[post][0]
            node2_y = outline_list[i][-1][1] + expanding_list[i][1] + expanding_list[post][1]
            node4_x = outline_list[i][-1][0]
            node4_y = outline_list[i][-1][1]
            node1_index = nearby([node2_x, node2_y], outline_list[i])
            node3_index = nearby([node2_x, node2_y], outline_list[post])
            
            temp_edge1 = [[node1_x, node1_y], [node2_x, node2_y]]
            temp_edge2 = [[node2_x, node2_y], [node3_x, node3_y]]
            temp_edge3 = outline_list[post][0:node3_index+1]
            temp_edge4 = outline_list[i][node1_index:]
            
            res_corner = build_unit_corner(cdb_obj, element_size, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
            next_edge1 = res_corner[1][::-1]
            next_left_outer_node_list = []
            center_edge3 = res_corner[0]
            center_right_outer_node_list = []
            
        ### build the center part
        center_node2_index = nearby(center_edge1[-1], outline_list[i])
        center_node3_index = nearby(center_edge3[-1], outline_list[i])
        
        if not equal_node(center_edge1[-1], center_edge3[-1]):
            temp_edge1 = center_edge1
            temp_edge2 = [center_edge1[-1], center_edge3[-1]]
            temp_edge3 = center_edge3
            temp_edge4 = outline_list[center_node2_index:center_node3_index+1]
            res_block = build_block_pattern(cdb_obj, element_size, pattern_lines_x, pattern_lines_y, temp_edge1, temp_edge2, temp_edge3, temp_edge4)
            center_node_list = res_block[1]
        else:
            center_node_list = []
        
        new_outline_list.appned(center_left_outer_node_list + center_node_list + center_right_outer_node_list)
    return new_outline_list

def build_layers(cdb_obj: 'Mesh2D', element_sizes: list, pattern_lines_x: list, pattern_lines_y: list, outline_list: list):
    for element_size in element_sizes:
        ### calculate the expanding
        expanding_list = []
        for outline in outline_list:
            expanding_list.append(cal_expanding(element_size, pattern_lines_x, pattern_lines_y, outline))
    
        ### build the expanding
        outline_list = build_layer(cdb_obj = cdb_obj, element_size = element_size, pattern_lines_x = pattern_lines_x, pattern_lines_y = pattern_lines_y, expanding_list = expanding_list , outline_list = outline_list)

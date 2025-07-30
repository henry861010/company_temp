def adapter_get_section(outline_list, expanding_list, pattern_lines_vertical: list, pattern_lines_horizon: list):   
    section_list = []
    right_corner_section = None
    
    for index, outline in enumerate(outline_list):
        if len(outline_list[index]) < 2:
            raise ValueError(f"[adapter_get_section] the len of outline {len(outline_list[index])} is small than 2")
            
        outline = outline_list[index]
        expanding = expanding_list[index]
        direction = get_direction(outline)
        
        outline_pre = outline_list[index-1]
        expanding_pre = expanding_list[index-1]
        direction_pre = get_direction(outline_pre)
        
        outline_post = outline_list[int(index+1)%len(outline_list)]
        expanding_post = expanding_list[int(index+1)%len(outline_list)]
        direction_post = get_direction(outline_post)
        
        outer_line = [[outline[0][0]+expanding[0], outline[0][1]+expanding[1]], [outline[-1][0]+expanding[0], outline[-1][1]+expanding[1]]]
        outer_line_post = [[outline_post[0][0]+expanding_post[0], outline_post[0][1]+expanding_post[1]], [outline_post[-1][0]+expanding_post[0], outline_post[-1][1]+expanding_post[1]]]
        
        if direction[0] != 0:
            if direction[0] < 0:
                pattern_line_list = list(reversed(pattern_lines_vertical))
            else:
                pattern_line_list = pattern_lines_vertical
        else:
            if direction[1] < 0:
                pattern_line_list = list(reversed(pattern_lines_horizon))
            else:
                pattern_line_list = pattern_lines_horizon

        if direction_post[0] != 0:
            if direction_post[0] < 0:
                pattern_line_post_list = list(reversed(pattern_lines_vertical))
            else:
                pattern_line_post_list = pattern_lines_vertical
        else:
            if direction_post[1] < 0:
                pattern_line_post_list = list(reversed(pattern_lines_horizon))
            else:
                pattern_line_post_list = pattern_lines_horizon
        
        ### [section_node1 & section_node2]
        if direction == rotate(direction_pre, 90):
            ### left - outer corner
            section_node1 = outline[0]
            section_node2 = [outline[0][0]+expanding[0], outline[0][1]+expanding[1]]
            begin_index = 0
        else:
            ### left - inner corner
            section_node2 = [outline[0][0]+expanding[0]+expanding_pre[0], outline[0][1]+expanding[1]+expanding_pre[1]]
            for pattern_line in pattern_line_list:
                inner_intersection = intersection(pattern_line, outline)
                if inner_intersection is not None:
                    section_node2 = intersection(pattern_line, outer_line, limit=False)
                    break
            begin_index = max(1, nearby(section_node2, outline))
            section_node1 = outline[begin_index]
            
        ### [section_node3 & section_node4]
        if direction == rotate(direction_post, 270):
            ### right outer corner
            section_node4 = outline[-1]
            section_node3 = [outline[-1][0]+expanding[0], outline[-1][1]+expanding[1]]
            end_index = len(outline)-1
            
            ### add right corner section
            corner_node1 = section_node4
            corner_node2 = section_node3
            corner_node3 = [outline[-1][0]+expanding[0]+expanding_post[0], outline[-1][1]+expanding[1]+expanding_post[1]]
            corner_node4 = [outline[-1][0]+expanding_post[0], outline[-1][1]+expanding_post[1]]
            right_corner_section = {
                "type": "OUTER",
                "edge1": [corner_node1, corner_node2],
                "edge2": [corner_node2, corner_node3],
                "edge3": [corner_node4, corner_node3],
                "edge4": [corner_node1, corner_node4]
            }
        else:
            ### right inner corner
            right_outer = [outline[-1][0]+expanding[0]+expanding_post[0], outline[-1][1]+expanding[1]+expanding_post[1]]
            
            ### right inner corner - left side            
            section_node3 = right_outer
            for pattern_line in list(reversed(pattern_line_list)):
                inner_intersection = intersection(pattern_line, outline)
                if inner_intersection is not None:
                    section_node3 = intersection(pattern_line, outer_line, limit=False)
                    break
            end_index = min(len(outline)-2, nearby(section_node3, outer_line))
            section_node4 = outline[end_index]
            
            ### right inner corner - right side (next_section_node1 & next_section_node2)
            next_section_node2 = right_outer
            for pattern_line_post in pattern_line_post_list:
                inner_intersection = intersection(pattern_line_post, outline_post)
                if inner_intersection is not None:
                    next_section_node2 = intersection(pattern_line_post, outer_line, limit=False)
                    break
            next_begin_index = max(1, nearby(next_section_node2, outline_post))
            next_section_node1 = outline_post[next_begin_index]
            
            ### add right corner section
            if not equal_node(right_outer, section_node3) and not equal_node(right_outer, next_section_node2):
                right_corner_section = {
                    "type": "INNER_BOTH",
                    "edge1": [section_node4, right_outer],
                    "edge2": [right_outer, next_section_node1],
                    "edge3": outline[end_index:],
                    "edge4": outline_post[:next_begin_index+1],
                    "outer": right_outer
                }
            elif equal_node(right_outer, section_node3) and not equal_node(right_outer, next_section_node2):
                right_corner_section = {
                    "type": "INNER_RIGHT",
                    "edge1": [section_node4, right_outer, next_section_node2],
                    "edge2": [right_outer, next_section_node1],
                    "edge3": outline[end_index:],
                    "edge4": outline_post[:next_begin_index+1]
                }
            elif not equal_node(right_outer, section_node3) and equal_node(right_outer, next_section_node2):
                right_corner_section = {
                    "type": "INNER_LEFT",
                    "edge1": [section_node4, right_outer],
                    "edge2": [section_node3, right_outer, next_section_node1],
                    "edge3": outline[end_index:],
                    "edge4": outline_post[:next_begin_index+1]
                }
            else:
                right_corner_section = {
                    "type": "INNER",
                    "edge1": [section_node4, right_outer],
                    "edge2": [right_outer, next_section_node1],
                    "edge3": outline[end_index:],
                    "edge4": outline_post[:next_begin_index+1]
                }

        ### [center line ]if section_node2 != section_node2
        if not equal_node(section_node1, section_node4):
            raise ValueError(f"[adapter_get_section] section_node1 and section_node4 are overlap, out of consideration. {section_node1} & {section_node4}")
        if not equal_node(section_node2, section_node3):
            raise ValueError(f"[adapter_get_section] section_node2 and section_node3 are overlap, out of consideration. {section_node2} & {section_node3}")
        
        inner_line = outline[begin_index:end_index+1]
        
        left_edge = [section_node1, section_node2]
        new_edge2 = [section_node2]
        pre_index = 0
        post_index = 0
        
        ### begin
        for pattern_line in pattern_line_list:
            inner_intersection = intersection(pattern_line, outline)
            outer_intersection = intersection(pattern_line, outer_line)
            if outer_intersection is not None:
                if not equal_node(new_edge2[-1], outer_intersection):
                    new_edge2.append(outer_intersection)
            if inner_intersection is not None:
                if not equal_node(inner_intersection, left_edge[0]):
                    ### append the outer node
                    outer_intersection = intersection(pattern_line, outer_line, limit=False)
                    if not equal_node(new_edge2[-1], outer_intersection):
                        new_edge2.append(outer_intersection)
                    
                    post_index = nearby(inner_intersection, inner_line)
                    
                    ### append the section
                    section_list.append({
                        "type": "LINE",
                        "edge1": left_edge,
                        "edge2": new_edge2,
                        "edge3": [inner_intersection, outer_intersection],
                        "edge4": inner_line[pre_index:post_index+1]
                    })
                    
                    pre_index = post_index
                    left_edge = [inner_intersection, outer_intersection]
                    new_edge2 = [new_edge2[-1]]
                
        ### last
        if pre_index != len(inner_line)-1:
            if not equal_node(new_edge2[-1], section_node3):
                new_edge2.append(section_node3)
            section_list.append({
                "type": "LINE",
                "edge1": left_edge,
                "edge2": new_edge2,
                "edge3": [section_node4, section_node3],
                "edge4": inner_line[pre_index:]
            })
        
        ### add the right corner section
        section_list.append(right_corner_section)
    return section_list
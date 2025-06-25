def get_neighbor_status(x, y, section_type):
    section_x_len = len(section_type)
    section_y_len = len(section_type[0])

    ### [list ???]
    neighbor_status = []

    ### bottom
    if 0 <= y-1 and section_type[x][y-1] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### left
    if 0 <= x-1 and section_type[x-1][y] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### top
    if y+1 < section_y_len and section_type[x][y+1] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### right
    if x+1 < section_x_len and section_type[x+1][y] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### bottom-left
    if 0 <= x-1 and 0 <= y-1 and section_type[x-1][y-1] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### top-left
    if 0 <= x-1 and y+1 < section_y_len and section_type[x-1][y+1] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### top-right
    if x+1 < section_x_len and y+1 < section_y_len and section_type[x+1][y+1] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    ### bottom-right
    if x+1 < section_x_len and 0 <= y+1 and section_type[x+1][y-1] & 2:
        neighbor_status.append(1)
    else:
        neighbor_status.append(0)

    return neighbor_status

def get_corner_dim(x, y, direction_pre, direction_next, table_x_dim, table_y_dim):
    res = []
    
    dir_old_x = direction_pre[0]
    dir_old_y = direction_pre[1]
    dir_new_x = direction_next[0]
    dir_new_y = direction_next[1]

    ### go down then x add 1
    if dir_old_y == -1 or dir_new_y == -1:
        x = x + 1
    else:
        x = x

    ### do right then y add 1
    if dir_old_x == 1 or dir_new_x == 1:
        y = y + 1
    else:
        y = y

    return [table_x_dim[x], table_y_dim[y]]

def find_block_outline(x, y, section_type, table_x_dim, table_y_dim):
    outline_list = []

    index_x = x
    index_y = y

    first_x = x
    first_y = y
    direction_pre = [0, 1]
    pre_node = [table_x_dim[first_x], table_y_dim[first_y]]

    while True:
        neighbor_status = get_neighbor_status(x, y, section_type)

        if direction_pre[1] == 1:
            a = 0
        elif direction_pre[0] == 1:
            a = 1
        elif direction_pre[1] == -1:
            a = 2
        elif direction_pre[0] == -1:
            a = 3
        
        neighbor0 = neighbor_status = (0 + a) % 4
        neighbor1 = neighbor_status = (1 + a) % 4
        neighbor2 = neighbor_status = (2 + a) % 4
        neighbor3 = neighbor_status = (3 + a) % 4

        if not neighbor2 and neighbor3:
            direction_next = rotate_direction(direction_pre, 0)

        elseif {not neighbor1 and not neighbor2 and neighbor3} {
            ### 90 degree
            direction_next rotate_direction(direction_pre, 90)

            ### outer corner
            corner_dim = get_corner_dim(index_x, index_y, direction_pre, direction_next)
            post_node = [corner_dim[0], corner_dim[1]]
            outline_list = outline_list.append([pre_node, post_node, direction_pre])
            pre_node = post_node
            
        } elseif {!$neighbor1 && !$neighbor2 && !$neighbor3} {
            ### 90 degree ~ outer corner
            set direction_next [rotate_direction $direction_pre 90]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
            set direction_pre $direction_next

            ### 90 degree ~ outer corner
            set direction_next [rotate_direction $direction_pre 90]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node

        } elseif {$neighbor2} {
            ### 270 degree ~ inner corner
            set direction_next [rotate_direction $direction_pre 270]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
        } if {!$neighbor0 && !$neighbor1 && !$neighbor2 && !$neighbor3} {
            ### 90 degree ~ outer corner
            set direction_next [rotate_direction $direction_pre 90]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
            set direction_pre $direction_next

            ### 90 degree ~ outer corner
            set direction_next [rotate_direction $direction_pre 90]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
            set direction_pre $direction_next

            ### 90 degree ~ outer corner
            set direction_next [rotate_direction $direction_pre 90]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
            set direction_pre $direction_next

            ### 90 degree ~ outer corner
            set direction_next [rotate_direction $direction_pre 90]
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
            set direction_pre $direction_next

            set direction_pre [list 0 0]
        }

        ### move to the next section
        set index_x [expr $index_x + [lindex $direction_next 0]]
        set index_y [expr $index_y + [lindex $direction_next 1]]

        set direction_pre $direction_next

        if {$first_x == $index_x && $first_y == $index_y} {
            break
        }
### get the maximum allowed expand length of the line with given direction
### param:
###     1. patternLine_list_x: sorted patternLine with x-axis
###     2. patternLine_list_y: sorted patternLine with y-axis
###     3. outline: the target expanding outline
###         * [list NODE1 NODE2 Direction]
###     4. target_size: the target element size for this expanding
### return:
###     * expand: maximum allowed expanding
###         * [list EXPAND_X EXPAND_Y]
proc get_outline_prediect_expand {
    patternLine_list_x
    patternLine_list_y
    outline
    target_size
} {
    set node1_x [lindex [lindex $outline 0] 0]
    set node1_y [lindex [lindex $outline 0] 1]
    set node2_x [lindex [lindex $outline 1] 0]
    set node2_y [lindex [lindex $outline 1] 1]
    set direction [lindex $outline 2] 

    set normal_direction [list [expr -[lindex $direction 1]] [expr [lindex $direction 0]]]
    if {[lindex $normal_direction 1] == 1} {
        set index 0
        while { 1 } {
            ### out of the boundary
            if {$index == [llength $patternLine_list_y]} {
                set expand -1
                break
            }
            set temp [lindex $patternLine_list_y $index]
            set temp_node1_x [lindex [lindex $temp 0] 0]
            set temp_node1_y [lindex [lindex $temp 0] 1]
            set temp_node2_x [lindex [lindex $temp 1] 0]
            set temp_node2_y [lindex [lindex $temp 1] 1]

            if {
                $temp_node1_y == $temp_node2_y && 
                $temp_node1_x <= $node1_x && $node1_x <= $temp_node2_x &&
                $node1_y < $temp_node1_y
            } {
                set expand_y [expr min(($temp_node1_y - $node1_y), $target_size)]
                set expand [list 0 $expand_y]
                break
            }

            incr index 1
        }
    } elseif {[lindex $normal_direction 1] == -1} {
        set index [expr [llength $patternLine_list_y] - 1]
        while { 1 } {
            ### out of the boundary
            if {0 < $index} {
                set expand -1
                break
            }
            set temp [lindex $patternLine_list_y $index]
            set temp_node1_x [lindex [lindex $temp 0] 0]
            set temp_node1_y [lindex [lindex $temp 0] 1]
            set temp_node2_x [lindex [lindex $temp 1] 0]
            set temp_node2_y [lindex [lindex $temp 1] 1]

            if {
                $temp_node1_y == $temp_node2_y && 
                $temp_node1_x <= $node1_x && $node1_x <= $temp_node2_x &&
                $temp_node1_y < $node1_y
            } {
                set expand_y [expr -min(abs($temp_node1_y - $node1_y), $target_size)]
                set expand [list 0 $expand_y]
                break
            }

            incr index -1
        }
    } elseif {[lindex $normal_direction 0] == 1} {
        set index 0
        while { 1 } {
            ### out of the boundary
            if {$index == [llength $patternLine_list_x]} {
                set expand -1
                break
            }
            set temp [lindex $patternLine_list_x $index]
            set temp_node1_x [lindex [lindex $temp 0] 0]
            set temp_node1_y [lindex [lindex $temp 0] 1]
            set temp_node2_x [lindex [lindex $temp 1] 0]
            set temp_node2_y [lindex [lindex $temp 1] 1]

            if {
                $temp_node1_x == $temp_node2_x && 
                $temp_node1_y <= $node1_y && $node1_y <= $temp_node2_y &&
                $node1_x < $temp_node1_x
            } {
                set expand_x [expr min(($temp_node1_x - $node1_x), $target_size)]
                set expand [list $expand_x 0]
                break
            }

            incr index 1
        }
    } elseif {[lindex $normal_direction 0] == -1} {
        set index [expr [llength $patternLine_list_x] - 1]
        while { 1 } {
            ### out of the boundary
            if {0 < $index} {
                set expand -1
                break
            }
            set temp [lindex $patternLine_list_x $index]
            set temp_node1_x [lindex [lindex $temp 0] 0]
            set temp_node1_y [lindex [lindex $temp 0] 1]
            set temp_node2_x [lindex [lindex $temp 1] 0]
            set temp_node2_y [lindex [lindex $temp 1] 1]

            if {
                $temp_node1_x == $temp_node2_x && 
                $temp_node1_y <= $node1_y && $node1_y <= $temp_node2_y &&
                $temp_node1_x < $node1_x
            } {
                set expand_x [expr -min(($temp_node1_x - $node1_x), $target_size)]
                set expand [list $expand_x 0]
                break
            }

            incr index -1
        }
    }

    return $expand
}

proc build_inner_corner {
    node_list_left
    node_list_right
    expanding_right
    expanding_left
} {
    set inner_x [lindex [lindex $node_list_right 0] 0]
    set inner_y [lindex [lindex $node_list_right 0] 1]
    set outer_x [expr $inner_x + [lindex $expanding_right 0] + [lindex $expanding_left 0]]
    set outer_x [expr $inner_y + [lindex $expanding_right 1] + [lindex $expanding_left 1]]

    set right 0
    set left [expr [llength $node_list_left] - 1]
    set dis_right 0
    set dis_left 0
    set first_x [lindex [lindex $node_list_left $left] 0]
    set first_y [lindex [lindex $node_list_left $left] 1]
    set target_right [expr abs([lindex $expanding_left 0] + [lindex $expanding_left 1])]
    set target_left [expr abs([lindex $expanding_right 0] + [lindex $expanding_right 1])]

    ### determine the corner_node_list_left & corner_node_list_right
    set corner_node_list_left [list]
    set corner_node_list_right [list]
    while {$target_right < $target_right && $target_left < $target_left} {
        lappend corner_node_list_left [lindex $node_list_left $left]
        lappend corner_node_list_right [lindex $node_list_right $right]

        incr right 1
        incr left 1

        set temp_l_x [lindex [lindex $node_list_left $left] 0]
        set temp_l_y [lindex [lindex $node_list_left $left] 1]
        set temp_r_x [lindex [lindex $node_list_right $right] 0]
        set temp_r_y [lindex [lindex $node_list_right $right] 1]
        set dis_left [expr abs($temp_l_x - $first_x) + abs($temp_l_y - $first_y)] 
        set dis_right [expr abs($temp_r_x - $first_x) + abs($temp_r_y - $first_y)] 
    }

    ### determine the center
    set center_x [expr $first_x + [lindex $expanding_left 0] + [lindex $expanding_right 0]]
    set center_y [expr $first_y + [lindex $expanding_left 1] + [lindex $expanding_right 1]]

    ###buile the element
    set num [expr [llength $corner_node_list_left] - 1]
    set vector_left_x [expr double([lindex [lindex $corner_node_list_left end] 0] - [lindex [lindex $corner_node_list_left 0] 0]) / num]
    set vector_left_y [expr double([lindex [lindex $corner_node_list_left end] 1] - [lindex [lindex $corner_node_list_left 0] 1]) / num]
    set vector_right_x [expr double([lindex [lindex $corner_node_list_right end] 0] - [lindex [lindex $corner_node_list_right 0] 0]) / num]
    set vector_right_y [expr double([lindex [lindex $corner_node_list_right end] 1] - [lindex [lindex $corner_node_list_right 0] 1]) / num]

    ??????
}

proc build_outer_corner {
    node_list_left
    node_list_right
    expanding_right
    expanding_left
} {
    ### outer corner
    set inner_x [lindex [lindex $node_list_right 0] 0]
    set inner_y [lindex [lindex $node_list_right 0] 1]
    set outer_x [expr $inner_x + [lindex $expanding_right 0] + [lindex $expanding_left 0]]
    set outer_y [expr $inner_y + [lindex $expanding_right 1] + [lindex $expanding_left 1]]

    ### build the corner
    *straightline $outer_x $inner_y 0 $outer_x $outer_y 0
    *straightline $inner_x $outer_y 0 $outer_x $outer_y 0

}

proc build_first_corner {
    index
    outline_list
    expanding_list
} {
    set expanding_pre [lindex $expanding_list [expr ($index + [llength $expanding_list] - 1) % [llength $expanding_list]]]
    set outline_pre [lindex $outline_list [expr ($index + [llength $outline_list] - 1) % [llength $outline_list]]]
    set direction_pre [lindex $outline_pre 1] 
    set node_list_pre [lindex $outline_pre 0] 

    set expanding_now [lindex $expanding_list $index]
    set outline_now [lindex $outline_list $index]
    set direction_now [lindex $outline_now 1] 
    set node_list_now [lindex $outline_now 0] 

    set expanding_post [lindex $expanding_list [expr ($index + [llength $expanding_list] - 1) % [llength $expanding_list]]]
    set outline_post [lindex $outline_list [expr ($index + [llength $outline_list] - 1) % [llength $outline_list]]]
    set direction_post [lindex $outline_post 1] 
    set node_list_post [lindex $outline_post 0] 

    set direction_270degree [list [expr -[lindex $direction_now 1]] [expr [lindex $direction_now 0]]]
    set direction_90degree [list [expr [lindex $direction_now 1]] [expr -[lindex $direction_now 0]]]

    set normal_direction_now [list [expr [lindex $direction_now 1]] [expr -[lindex $direction_now 0]]]
    set normal_direction_pre [list [expr [lindex $direction_pre 1]] [expr -[lindex $direction_pre 0]]]
    set normal_direction_post [list [expr [lindex $direction_post 1]] [expr -[lindex $direction_post 0]]]

    ### first corner: idnetity the left corner (270 degree -> outer corner ; 90 degree -> inner corner)
    if {[lindex $direction_pre 0] == [lindex $direction_90degree 0] && [lindex $direction_pre 1] == [lindex $direction_90degree 1]} {
        build_inner_corner $node_list_pre $node_list_now $expanding_pre $expanding_now
    } elseif {[lindex $direction_pre 0] == [lindex $direction_270degree 0] && [lindex $direction_pre 1] == [lindex $direction_270degree 1]} {
        build_outer_corner $node_list_pre $node_list_now $expanding_pre $expanding_now
    }    

    ### second corner: idnetity the left corner (270 degree -> inner corner ; 90 degree -> outer corner)
    if {[lindex $direction_pre 0] == [lindex $direction_270degree 0] && [lindex $direction_pre 1] == [lindex $direction_270degree 1]} {
        build_inner_corner $node_list_pre $node_list_now $expanding_pre $expanding_now
    } elseif {[lindex $direction_pre 0] == [lindex $direction_270degree 0] && [lindex $direction_pre 1] == [lindex $direction_270degree 1]} {
        build_outer_corner $node_list_pre $node_list_now $expanding_pre $expanding_now
    }   
}

### ---------------------------------------------------------------

proc distance {
    node1
    node2
} {
    set x [expr [lindex $node2 0] - [lindex $node1 0]]
    set y [expr [lindex $node2 1] - [lindex $node1 1]]
    set distance [expr sqr($x * $x + $y * $y)]
    return $distance
}

proc draw_line {
    node1
    node2
} {
    *straightline [lindex $node1 0] [lindex $node1 1] 0 [lindex $node2 0] [lindex $node2 1] 0
}

proc line_project {
    line
    node
} {
    set v_x [expr double([lindex [lindex $line end] 0]) - double([lindex [lindex $line 0] 0])]
    set v_y [expr double([lindex [lindex $line end] 1]) - double([lindex [lindex $line 0] 1])]
    set w_x [expr double([lindex $node 0]) - double([lindex [lindex $line 0] 0])]
    set w_y [expr double([lindex $node 1]) - double([lindex [lindex $line 0] 1])]

    set t [expr ($w_x * $v_x + $w_y * $v_y) / (($v_x * $v_x + $v_y * $v_y))]

    set project_x [expr double([lindex [lindex $line 0] 0]) + $t * $v_x]
    set project_y [expr double([lindex [lindex $line 0] 1]) + $t * $v_y]

    return [list $project_x $project_y]
}

### edge1: 3 nodes (or 2 sections)
### edge2: 2 nodes (or 1 sections)
### edge3: 3 nodes (or 2 sections)
### edge4: >=2 && %2, the number of nodex should be even
proc build_2_1_2_x {
    edge1
    edge2
    edge3
    edge4
} {
    ### check if the x is odd or it is impossible to be mesh
    if {[llength $edge4] % 2} {
        the node number of the edge4 should be even !!!
    }

    set section_num [expr [llength $edge4] - 1]
    set mid_begin_x [expr double([lindex [lindex $edge1 1] 0])]
    set mid_begin_y [expr double([lindex [lindex $edge1 1] 1])]
    set mid_end_x [expr double([lindex [lindex $edge3 1] 0])]
    set mid_end_y [expr double([lindex [lindex $edge3 1] 1])]
    set vector_x [expr ($mid_end_x - $mid_begin_x) / double($section_num)]
    set vector_y [expr ($mid_end_y - $mid_begin_y) / double($section_num)]

    set now_x [expr double([lindex [lindex $edge4 0] 0])]
    set now_y [expr double([lindex [lindex $edge4 0] 1])]

    set mid_node_list  [list [list $now_x $now_y]]
    set mid_now_x $mid_begin_x
    set mid_now_y $mid_begin_y
    for {set i 1} {$i <= [llength $edge4]} {incr i 1} {
        set now_x [expr double([lindex [lindex $edge4 $i] 0])]
        set now_y [expr double([lindex [lindex $edge4 $i] 1])]
        set temp_x [expr $mid_now_x + $vector_x]
        set temp_y [expr $mid_now_y + $vector_y]

        draw_line [list $mid_now_x $mid_now_y] [list $temp_x $temp_y]
        draw_line [list $temp_x $temp_y] [list $now_x $now_y]

        set mid_now_x $temp_x
        set mid_now_y $temp_y
        lappend mid_node_list [list $mid_now_x $mid_now_y]
    }

    ### draw the unit 1_1_1_x
    set edge1 [lrange $edge1 1 2]
    set edge3 [lrange $edge3 0 1]
    set edge4 $mid_node_list
    build_1_1_1_x  $edge1 $edge2 $edge3 $edge4
}

### edge1: 3 nodes (or 2 sections)
### edge2: 3 nodes (or 2 sections)
### edge3: 3 nodes (or 2 sections)
### edge3: 3 nodes (or 2 sections)
proc build_2_2_2_2 {
    edge1
    edge2
    edge3
    edge4
} {
    set mid1_x [expr double([lindex [lindex $edge1 1] 0])]
    set mid1_y [expr double([lindex [lindex $edge1 1] 1])]
    set mid2_x [expr double([lindex [lindex $edge2 1] 0])]
    set mid2_y [expr double([lindex [lindex $edge2 1] 1])]
    set mid3_x [expr double([lindex [lindex $edge3 1] 0])]
    set mid3_y [expr double([lindex [lindex $edge3 1] 1])]
    set mid4_x [expr double([lindex [lindex $edge4 1] 0])]
    set mid4_y [expr double([lindex [lindex $edge4 1] 1])]

    set mid_x [expr ($mid1_x + $mid2_x + $mid3_x + $mid4_x) /4]
    set mid_y [expr ($mid1_y + $mid2_y + $mid3_y + $mid4_y) /4]

    draw_line [list $mid_x $mid_y] [list $mid1_x $mid1_y]
    draw_line [list $mid_x $mid_y] [list $mid2_x $mid2_y]
    draw_line [list $mid_x $mid_y] [list $mid3_x $mid3_y]
    draw_line [list $mid_x $mid_y] [list $mid4_x $mid4_y]
}

### edge1: 2/3 nodes (or 1/2 sections)
### edge2: >=2
### edge3: 2/3 nodes (or 1/2 sections)
### edge4: >=2
### algorithm would add nodes on edge2 to ensure that target_size and mesh could be satisfied
proc build_line {
    target_size
    edge1
    edge2
    edge3
    edge4
} {
    set section_outer_num [expr [llength $edge2] - 1]
    set section_inner_num [expr [llength $edge1] + [llength $edge3] + [llength $edge4] - 3]

    set last_inner_index [expr [llength $$edge4] - 1]
    set last_outer_index [expr [llength $$edge2] - 1]

    ### determine the target outer section number
    set edge2_len [distance [lindex $edge2 0] [lindex $edge2 end]]
    set target_section_num [expr ceil($edge2_len / $target_size)]
    if {($section_inner_num + $target_section_num) % 2} {
        ### to guarante the number of total edge is even, if it is odd add 1 to $target_section_num
        incr target_section_num 1
    }

    ### determine the outer node
    ### there are several reference node at the edge, we should consider it while we mesh.
    ### we call the distance between the reference node are "bucket"
    ###     * bucket_num: the number of the section in it
    ###     * bucket_dis: the distance of the bucket
    set bucket_num [list ]
    set bucket_dis [list ]
    for {set i 1} {$i < [llength $edge2]} {incr i -1} {
        lappend bucket_num 1
        lappend bucket_dis [distance [lindex $edge2 [expr $i - 1]] [lindex $edge2 $i]]
    }
    while {$section_outer_num < $target_section_num} {
        ### find the bucket where each section in it have maximum len
        set max_len -1
        set max_index -1
        for {set i 0} {$i < [llength $bucket_dis]} {incr i 1} {
            set temp_len [expr [lindex $bucket_dis $i] / [lindex $bucket_num $i]]
            if {$temp_len > $max_len} {
                set max_len $temp_len
                set max_index $i
            }
        }

        ### find it and add the section to this found bucket
        set new_num [expr [lindex $bucket_num $max_index] + 1]
        set bucket_num [lreplace $bucket_num $max_index $max_index $new_num]
        
        incr section_outer_num 1
    }

    ### determine the ouetr node list
    set outer_node_list [list ]

    set now_x [lindex [lindex $edge2 0] 0]
    set now_y [lindex [lindex $edge2 0] 1]
    for {set i 0} {$i < [llength $bucket_num]} {incr i 1} {
        set section_num [lindex $bucket_num $i]
        set begin_x [lindex [lindex $edge2 $i] 0]
        set begin_y [lindex [lindex $edge2 $i] 1]
        set end_x [lindex [lindex $edge2 [expr $i + 1]] 0]
        set end_y [lindex [lindex $edge2 [expr $i + 1]] 1]

        set vector_x [expr double($end_x - $begin_x) / double($section_num)]
        set vector_x [expr double($end_y - $begin_y) / double($section_num)]

        for {set j 0} {$j < $section_num} {incr j 1} {
            set new_x [expr $now_x + $vector_x]
            set new_y [expr $now_x + $vector_y ]

            lappend outer_node_list [list [list $now_x $now_y] [list $new_x $new_y]]

            set now_x $new_x
            set now_y $new_y
        }
    }

    ### mesh
    if {[llength $edge1] == 3 && [llength $outer_node_list] == 3 && [llength $edge3] == 3 && [llength $edge4] == 3} {
        build_2_2_2_2 $edge1 $outer_node_list $edge3 $edge4
    } elseif {[llength $edge1] == 3 && [llength $outer_node_list] == 3 && [llength $edge3] == 3 && [llength $edge4] == 3} {
        build_2_1_2_x $edge1 $outer_node_list $edge3 $edge4
    } else {
        set inner_pre  0
        set inner_post 0
        set outer_pre 0
        set outer_post 1
        while {$outer_post != [llength $outer_node_list]} {
            if {$outer_pre == 0 && [llength $edge1] == 3} {
                set inner_post [next_index 1 $edge2 $inner_pre $edge4 $outer_post 4]

                set temp1 [list [lindex $edge4 $inner_pre] [lindex $outer_node_list $outer_pre]]
                set temp2 [lrange $outer_node_list $outer_pre $outer_post]
                set temp3 [list [lindex $edge4 $inner_post] [lindex $outer_node_list $outer_post]]
                set temp4 [lrange $edge4 $inner_pre $inner_post] 

                build_x_1_1_y $temp1 $temp2 $temp3 $temp4
            } elseif {$outer_pre == [expr [llength $outer_node_list] - 1] && [llength $edge3] == 3} {
                set inner_post [next_index 1 $edge2 $inner_pre $edge4 $outer_post 4]

                set temp1 [list [lindex $edge4 $inner_pre] [lindex $outer_node_list $outer_pre]]
                set temp2 [lrange $outer_node_list $outer_pre $outer_post]
                set temp3 [list [lindex $edge4 $inner_ost] [lindex $outer_node_list $outer_post]]
                set temp4 [lrange $edge4 $inner_pre $inner_post] 

                build_x_1_1_y $temp4 $temp1 $temp2 $temp3
            } else {
                set inner_post [next_index 1 $edge2 $inner_pre $edge4 $outer_post 3]

                set temp1 [list [lindex $edge4 $inner_pre] [lindex $outer_node_list $outer_pre]]
                set temp2 [lrange $outer_node_list $outer_pre $outer_post]
                set temp3 [list [lindex $edge4 $inner_ost] [lindex $outer_node_list $outer_post]]
                set temp4 [lrange $edge4 $inner_pre $inner_post] 

                build_1_1_1_x $temp1 $temp2 $temp3 $temp4
            }
            
            set inner_pre $inner_post
            incr outer_pre 1
            incr outer_post 1
        }
    }

    return [list $edge1 $outer_node_list $edge3 $edge4]
}

### return index in edge which is the next node
### direction: 
###     1 go right
###     -1 go left
### edge_num: the edge of the section now
###     INT
proc next_index {
    direction
    outer_node_list
    outer_index
    inner_node_list
    inner_index
    edge_num
} {
    if {$outer_index == [expr [llength $outer_node_list] - 1]} {
        return [expr [llength $inner_node_list] - 1]
    }
    if {$outer_index == 0} {
        return 0
    }

    set node [lindex $outer_node_list $outer_index]
    set project [line_project $inner_node_list $node]
    set vector_x [expr $direction * ([lindex [lindex $inner_node_list end] 0] - [lindex [lindex $inner_node_list 0] 0])]
    set vector_y [expr $direction * ([lindex [lindex $inner_node_list end] 1] - [lindex [lindex $inner_node_list 0] 1])]

    set node_pre [lindex $inner_node_list $inner_index]
    set index_pre $inner_index

    if {edge_num % 2} {
        set inner_index [expr $inner_index + 1]
    } else {
        set inner_index [expr $inner_index + 2]
    }
    
    while {1} {
        ### if at the last node, return the last element
        if {$inner_index == [llength $inner_node_list] || $inner_index < 0} {
            return $index_pre
        }

        set node_now [lindex $inner_node_list $inner_index]
        set temp_vector_x [expr [lindex $project 0] - [lindex $node_now 0]]
        set temp_vector_x [expr [lindex $project 1] - [lindex $node_now 1]]

        if {
            $vector_x < 0 && $temp_vector_x < 0 ||
            $vector_x > 0 && $temp_vector_x > 0 ||
            $vector_y < 0 && $temp_vector_y < 0 ||
            $vector_y > 0 && $temp_vector_y > 0 ||
        } {
            set node_pre $node_now
            set index_pre $inner_index

            incr inner_index [expr 2 * $direction]
        } else {
            set dis_now [distance $node_now $project]
            set dis_pre [distance $node_pre $project]
            if {$inner_index == [expr [llength $inner_node_list] - 1] || $inner_index == 0} {
                ### the first/last inner_node must belong to the first/last outer node, and these situation must be deal at the begin of the function
                return $index_pre
            } elseif{$dis_now < $dis_pre} {
                return $inner_index
            } else {
                return $index_pre
            }
        }
    }
}


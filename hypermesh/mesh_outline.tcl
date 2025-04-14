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
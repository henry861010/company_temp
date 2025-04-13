### get the maximum allowed expand length of the line with given direction
### param:
###     1. patternLine_list_x: sorted patternLine with x-axis
###     2. patternLine_list_y: sorted patternLine with y-axis
###     3. outline: the target expanding outline
###         * [list NODE1 NODE2 Direction]
###     4. target_size: the target element size for this expanding
### return:
###     * expand: maximum allowed expanding
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
                set expand [expr min(($temp_node1_y - $node1_y), $target_size)]
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
                set expand [expr min(($node1_y - $temp_node1_y), $target_size)]
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
                set expand [expr min(($temp_node1_x - $node1_x), $target_size)]
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
                set expand [expr min(($node1_x - $temp_node1_x), $target_size)]
                break
            }

            incr index -1
        }
    }

    return $expand
}

proc build_left_corner {
    index
    outline_list
    expanding_list
} {
    set outline_pre [lindex $outline_list [expr ($index + [llength $outline_list] - 1) % [llength $outline_list]]]
    set expanding_pre [lindex $expanding_list [expr ($index + [llength $expanding_list] - 1) % [llength $expanding_list]]]
    set direction_pre [lindex $outline_pre 2] 

    set outline [lindex $outline_list $index]
    set expanding [lindex $expanding_list $index]
    set direction [lindex $outline 2] 
    set node1 [lindex $outline 0] 
    set node2 [lindex $outline 1] 

    set direction_90degree [list [expr -[lindex $direction 1]] [expr [lindex $direction 0]]]
    set direction_270degree [list [expr [lindex $direction 1]] [expr -[lindex $direction 0]]]

    set normal_direction [list [expr -[lindex $direction 1]] [expr [lindex $direction 0]]]
    set normal_direction_pre [list [expr -[lindex $direction_pre 1]] [expr [lindex $direction_pre 0]]]

    ### idnetity the left corner (270 degree -> outer corner ; 90 degree -> inner corner)
    if {[lindex $direction_pre 0] == [lindex $direction_90degree 0] && [lindex $direction_pre 1] == [lindex $direction_90degree 1]} {
        ### inner corner
        set pre_node_list ???
        set now_node_list ???

        

    } elseif {[lindex $direction_pre 0] == [lindex $direction_270degree 0] && [lindex $direction_pre 1] == [lindex $direction_270degree 1]} {
        ### outer corner
        if {[lindex $normal_direction 0]} {
            set inner_x [lindex $node1 0]
            set outer_x [expr $inner_x + $expanding * [lindex $normal_direction 0]]

            set inner_y [lindex $node1 1]
            set inner_y [expr $inner_y + $expanding_pre * [lindex $normal_direction_pre 1]]
        } else {
            set inner_x [lindex $node1 0]
            set outer_x [expr $inner_x + $expanding_pre * [lindex $normal_direction_pre 0]]

            set inner_y [lindex $node1 1]
            set inner_y [expr $inner_y + $expanding * [lindex $normal_direction 1]]
        }

        ### build the corner
        *straightline $outer_x $inner_y 0 $outer_x $outer_y 0
        *straightline $inner_x $outer_y 0 $outer_x $outer_y 0
    }    
}
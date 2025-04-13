### change the 2d list value
proc set_2dList_item {
    target_list
    i
    j
    value
} {
    set subList [lindex $target_list $i]
    set subList [lreplace $subList $j $j $value]
    set target_list [lreplace $target_list $i $i $subList]
    return $target_list
}

### get the 2d list value
proc get_2dList_item {
    target_list
    i
    j
} {
    return [lindex [lindex $target_list $i] $j]
}

proc get_table {
    potential_dim_list
    constrained_dim_list
    gap_dim_list
} {
    ### build the "table_x/y_dim" which elements are unique and in the increasing
    set table_x_dim [list ]
    set table_y_dim [list ]
    foreach dim $potential_dim_list {
        lappend table_x_dim [lindex $dim 0]
        lappend table_x_dim [lindex $dim 2]
        lappend table_y_dim [lindex $dim 1]
        lappend table_y_dim [lindex $dim 3]
    }
        foreach dim $constrained_dim_list {
        lappend table_x_dim [lindex $dim 0]
        lappend table_x_dim [lindex $dim 2]
        lappend table_y_dim [lindex $dim 1]
        lappend table_y_dim [lindex $dim 3]
    }
        foreach dim $gap_dim_list {
        lappend table_x_dim [lindex $dim 0]
        lappend table_x_dim [lindex $dim 2]
        lappend table_y_dim [lindex $dim 1]
        lappend table_y_dim [lindex $dim 3]
    }
    set table_x_dim [lsort -unique -increasing $table_x_dim]
    set table_y_dim [lsort -unique -increasing $table_y_dim]

    ### build the table_x/y_id
    set table_x_id [dict create]
    set table_y_id [dict create]
    for {set i 0} {$i < [llength $table_x_dim]} {incr i 1} {
        dict lappend table_x_id [lindex $table_x_dim $i] $i
    }
    for {set i 0} {$i < [llength $table_y_dim]} {incr i 1} {
        dict lappend table_y_id [lindex $table_y_dim $i] $i
    }

    ### build the section block & initialize it to zero, value:
    ###     * -1 -> out of consideration
    ###     * 0 -> empty
    ###     * 1 -> die
    ###     * 2 -> gap
    set section_type [list ]
    set section_x_len [expr [llength $table_x_dim]-1]
    set section_y_len [expr [llength $table_y_dim]-1]
    for {set i 0} {$i < $section_x_len} {incr i 1} {
        set section_type_sub [list ]
        for {set j 0} {$j < $section_y_len} {incr j 1} {
            lappend section_type_sub -1
        }
        lappend section_type $section_type_sub
    }
    foreach dim $potential_dim_list {
        set first_x_id [dict get $table_x_id [lindex $dim 0]]
        set first_y_id [dict get $table_y_id [lindex $dim 1]]
        set last_x_id [dict get $table_x_id [lindex $dim 2]]
        set last_y_id [dict get $table_y_id [lindex $dim 3]]
        for {set i $first_x_id} {$i < $last_x_id} {incr i 1} {
            for {set j $first_y_id} {$j < $last_y_id} {incr j 1} {
                set section_type [set_2dList_item $section_type $i $j 0]
            }
        }
    }
    foreach dim $constrained_dim_list {
        set first_x_id [dict get $table_x_id [lindex $dim 0]]
        set first_y_id [dict get $table_y_id [lindex $dim 1]]
        set last_x_id [dict get $table_x_id [lindex $dim 2]]
        set last_y_id [dict get $table_y_id [lindex $dim 3]]
        for {set i $first_x_id} {$i < $last_x_id} {incr i 1} {
            for {set j $first_y_id} {$j < $last_y_id} {incr j 1} {
                set section_type [set_2dList_item $section_type $i $j 1]
            }
        }
    }
    foreach dim $gap_dim_list {
        set first_x_id [dict get $table_x_id [lindex $dim 0]]
        set first_y_id [dict get $table_y_id [lindex $dim 1]]
        set last_x_id [dict get $table_x_id [lindex $dim 2]]
        set last_y_id [dict get $table_y_id [lindex $dim 3]]
        for {set i $first_x_id} {$i < $last_x_id} {incr i 1} {
            for {set j $first_y_id} {$j < $last_y_id} {incr j 1} {
                set section_type [set_2dList_item $section_type $i $j 2]
            }
        }
    }

    return [list $table_x_dim $table_y_dim $table_x_id $table_y_id $section_type]
}

proc get_neighbor_status {
    x
    y
    section_type
} {
    set section_x_len [llength $section_type]
    set section_y_len [llength [lindex $section_type 0]]

    ### [list ???]
    set neighbor_status [list ]

    ### bottom
    if {0 <= [expr $y - 1] && [set_2dList_item $section_type $x [expr $y - 1]] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### left
    if {0 <= [expr $x - 1] && [set_2dList_item $section_type [expr $x - 1] $y] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### top
    if {[expr $y + 1] < $section_y_len && [set_2dList_item $section_type $x [expr $y + 1]] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### right
    if {[expr $x + 1] < $section_x_len && [set_2dList_item $section_type [expr $x + 1] $y] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### bottom-left
    if {0 <= [expr $x - 1] && 0 <= [expr $y - 1] && [set_2dList_item $section_type [expr $x - 1] [expr $y - 1]] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### top-left
    if {0 <= [expr $x - 1] && [expr $y + 1] < $section_y_len && [set_2dList_item $section_type [expr $x - 1] [expr $y + 1]] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### top-right
    if {[expr $x + 1] < $section_x_len && [expr $y + 1] < $section_y_len && [set_2dList_item $section_type [expr $x + 1] [expr $y +1]] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    ### bottom-right
    if {[expr $x + 1] < $section_x_len && 0 <= [expr $y - 1] && [set_2dList_item $section_type [expr $x + 1] [expr $y - 1]] == 2} {
        set neighbor_status [lappend neighbor_status 1]
    } else {
        set neighbor_status [lappend neighbor_status 0]
    }

    return $neighbor_status
}

proc rotate_direction {
    direction
    degree
} {
    set dir_x [lindex $direction 0]
    set dir_y [lindex $direction 1]

    ### rotate matrix
    ### a b
    ### c d
    ### [ax+by, cx+dy]

    if {$degree == 0} {
        ### rotate matrix of 0 degree
        ### 1 0
        ### 0 1
        set a 1
        set b 0
        set c 0
        set d 1
    } elseif {$degree == 90} {
        ### rotate matrix of 90 degree
        ### 0 -1
        ### 1  0
        set a 0
        set b -1
        set c 1
        set d 0
    } elseif {$degree == 180} {
        ### rotate matrix of 0 degree
        ### -1  0
        ###  0 -1
        set a -1
        set b 0
        set c 0
        set d -1
    } elseif {$degree == 270} {
        ### rotate matrix of 0 degree
        ###  0 1
        ### -1 0
        set a 0
        set b 1
        set c -1
        set d 0
    }
    set new_x [expr $a * $dir_x + $b * $dir_y]
    set new_y [expr $c * $dir_x + $d * $dir_y]

    return [list $new_x $new_y]
}

proc get_corner_dim {
    x
    y
    direction_pre
    direction_next
    table_x_dim
    table_y_dim
} {
    set res [list ]
    
    set dir_old_x [lindex $direction_pre 0]
    set dir_old_y [lindex $direction_pre 1]
    set dir_new_x [lindex $direction_next 0]
    set dir_new_y [lindex $direction_next 1]

    ### go down then x add 1
    if {$dir_old_y == -1 || $dir_new_y == -1} {
        set x [expr $x + 1]
    } else {
        set x $x
    }

    ### do right then y add 1
    if {$dir_old_x == 1 || $dir_new_x == 1} {
        set y [expr $y + 1]
    } else {
        set y $y
    }

    return [list [lindex $table_x_dim $x] [lindex $table_y_dim $y]]
}

### find the outline of the block
proc find_block_outline {
    x
    y
    section_type
    table_x_dim
    table_y_dim
} {
    set outline_list [list ]

    set index_x $x
    set index_y $y

    set first_x $x
    set first_y $y
    set direction_pre [list 0 1]
    set pre_node [list [lindex $table_x_dim $first_x] [lindex $table_y_dim $first_y]]

    while {1} {
        set neighbor_status [get_neighbor_status $x $y $section_type]

        if {[lindex $direction_pre 1] == 1} {
            ### upward
            set a 0
        } elseif {[lindex $direction_pre 0] == 1} {
            ### rightward
            set a 1
        } elseif {[lindex $direction_pre 1] == -1} {
            ### downward 
            set a 2
        } elseif {[lindex $direction_pre 0] == -1} {
            ### lefward
            set a 3
        }
        set neighbor0 [lindex $neighbor_status [expr (0 + $a) % 4]]
        set neighbor1 [lindex $neighbor_status [expr (1 + $a) % 4]]
        set neighbor2 [lindex $neighbor_status [expr (2 + $a) % 4]]
        set neighbor3 [lindex $neighbor_status [expr (3 + $a) % 4]]

        if {!$neighbor2 && $neighbor3} {
            ### 0 degree
            set direction_next [rotate_direction $direction_pre 0]

        } elseif {!$neighbor1 && !$neighbor2 && $neighbor3} {
            ### 90 degree
            set direction_next [rotate_direction $direction_pre 90]

            ### outer corner
            set corner_dim [get_corner_dim $index_x $index_y $direction_pre $direction_next]
            set post_node [list [lindex $corner_dim 0] [lindex $corner_dim 1]]
            set outline_list [lappend outline_list [list $pre_node $post_node $direction_pre]]
            set pre_node $post_node
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
    }
}

###
proc set_blockToFound {
    x
    y
    section_type
} {
    set section_x_len [llength $section_type]
    set section_y_len [llength [lindex $section_type 0]]

    if {$x < 0 || $y < 0 || $x == $section_x_len || $y == $section_y_len}  {
        return $section_type
    }
    if {[get_2dList_item $section_type $x $y] != 2} {
        return $section_type
    }

    set section_type [set_2dList_item $section_type $x $y 3]
    set section_type [set_blockToFound [expr $x + 1] $y $section_x_len $section_y_len $section_type]
    set section_type [set_blockToFound [expr $x - 1] $y $section_x_len $section_y_len $section_type]
    set section_type [set_blockToFound $y [expr $y + 1] $section_x_len $section_y_len $section_type]
    set section_type [set_blockToFound $y [expr $y - 1] $section_x_len $section_y_len $section_type]

    return section_type
}

proc outline_getor {
    gap_dim_list
} {
    set block_outline_list [list ]

    ### build the section dim-id table & section_type table
    set temp [get_table [list ] [list ] $gap_dim_list]
    set table_x_dim [lindex $temp 0]
    set table_y_dim [lindex $temp 1]
    set table_x_id [lindex $temp 2]
    set table_y_id [lindex $temp 3]
    set section_type [lindex $temp 4]

    set section_x_len [expr [llength $table_x_dim]-1]
    set section_y_len [expr [llength $table_y_dim]-1]

    for {set i 0} {$i < $section_x_len} {incr i 1} {
        for {set j 0} {$j < $section_y_len} {incr j 1} {
            if {[get_2dList_item $section_type $i $j] == 2} {
                ### find the outline list of the block
                set outline_list [find_block_outline $i $j $section_type $table_x_dim $table_y_dim]
                set block_outline_list [lappend block_outline_list $outline_list]
                
                ### clear the found block to prevent the duplicate finding
                set section_type [set_blockToFound $i $j $section_type]
            }
        }
    }

    return $block_outline_list
}

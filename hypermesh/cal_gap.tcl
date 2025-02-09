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

### calculate the gap area between the object. when the gap between object is smaller than the target gap the area would be account
### 1. parameter:
###     (1) gap: float
###     (2) dim_list: [list [list node1_x node1_y node3_x node3_y] ... ]
### 2.return
###     (1) gap_list: [list [list node1_x node1_y node3_x node3_y] ... ]
###             * the area with smaller than target gap
### 3. design ???
proc cal_gap {
    gap
    dim_list
} {
    ### build the "table_x/y_dim" which elements are unique and in the increasing
    set table_x_dim [list ]
    set table_y_dim [list ]
    foreach dim $dim_list {
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
    ###     1. 0 -> empty
    ###     2. 1 -> die
    ###     3. 2 -> gap
    set section_type [list ]
    set section_x_len [expr [llength $table_x_dim]-1]
    set section_y_len [expr [llength $table_y_dim]-1]
    for {set i 0} {$i < $section_x_len} {incr i 1} {
        set section_type_sub [list ]
        for {set j 0} {$j < $section_y_len} {incr j 1} {
            lappend section_type_sub 0
        }
        lappend section_type $section_type_sub
    }
    foreach dim $dim_list {
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

    ### determine the "gap" section
    for {set i 0} {$i < $section_x_len} {incr i 1} {
        for {set j 0} {$j < $section_y_len} {incr j 1} {
            if {[get_2dList_item $section_type $i $j] == 0} {
                ### x - axis
                if {$i > 0 && [get_2dList_item $section_type [expr $i-1] $j]} {
                    set right [expr $i + 1]
                    while {1} {
                        if {$right >= $section_x_len} {
                            set right -1
                            break
                        } elseif {[get_2dList_item $section_type $right $j]} {
                            break
                        } else {
                            incr right 1
                        }
                    }
                    if {$right != -1 && [expr [lindex $table_x_dim $right] - [lindex $table_x_dim $i]] <= $gap} {
                        for {set k $i} {$k < $right} {incr k 1} {
                            set section_type [set_2dList_item $section_type $k $j 2]
                        }
                    }
                }

                ### y-axis
                if {$j > 0 && [get_2dList_item $section_type $i [expr $j-1]]} {
                    set upper [expr $j + 1]
                    while {1} {
                        if {$upper >= $section_y_len} {
                            set upper -1
                            break
                        } elseif {[get_2dList_item $section_type $i $upper]} {
                            break
                        } else {
                            incr upper 1
                        }
                    }
                    if {$upper != -1 && [expr [lindex $table_y_dim $upper] - [lindex $table_y_dim $j]] <= $gap} {
                        for {set k $j} {$k < $upper} {incr k 1} {
                            set section_type [set_2dList_item $section_type $i $k 2]
                        }
                    }
                }
            }

            ### add the lose one (only in x-axis ???)
            if {[get_2dList_item $section_type $i $j] == 2} {
                set left [expr $i-1]
                while {1} {
                    if {$left < 0} {
                        set left -1
                        break
                    } elseif {[get_2dList_item $section_type $left $j]} {
                        incr left 1
                        break
                    } else {
                        incr left -1
                    }
                }
                if {$left != -1 && [expr [lindex $table_x_dim $i] - [lindex $table_x_dim $left]] <= $gap} {
                    for {set k $left} {$k < $i} {incr k 1} {
                        set section_type [set_2dList_item $section_type $k $j 2]
                    }
                }
            }
        }
    }

    ### merge the gap section and regenerate the list
    set gap_list [list ]
    for {set i 0} {$i < $section_x_len} {incr i 1} {
        for {set j 0} {$j < $section_y_len} {incr j 1} {
            if {[get_2dList_item $section_type $i $j] == 2} {
                set node1_x [lindex $table_x_dim $i]
                set node1_y [lindex $table_y_dim $j]
                set node3_x [lindex $table_x_dim [expr $i+1]]
                set node3_y [lindex $table_y_dim [expr $j+1]]
                lappend gap_list [list $node1_x $node1_y $node3_x $node3_y]
            }
        }
    }
    return $gap_list
}

set dim_list [list [list 0 0 1 2] [list 0 3 2 9] [list 5 0 7 1] [list 5 7 7 9]]
set gap 6
set gap_list [cal_gap $gap $dim_list]
puts "gap_list: $gap_list"
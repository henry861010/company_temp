set total_dummy %total_dummy%


### y-axis
set record_line [dict create]
foreach dim $total_dummy {
    set node1_x [lindex $dim 0]
    set node1_y [lindex $dim 1]
    set node3_x [lindex $dim 2]
    set node3_y [lindex $dim 3]
    if {$node3_x > 0 && $node3_y > 0 && ![dict exists record_line $node3_x]} {
        set min_y $node3_y
        foreach dim_ref $total_dummy {
            set node1_x_ref [lindex $dim_ref 0]
            set node1_y_ref [lindex $dim_ref 1]
            set node3_x_ref [lindex $dim_ref 2]
            set node3_y_ref [lindex $dim_ref 3]
            if {$node3_x_ref == $node3_x && $node3_y_ref > 0} {
                set min_y [expr min($min_y, $node3_y_ref)]
            }
        }

        dict set record_line $node3_x 1
        *linexxxx $node1_x $min_y 0 $node1_x 1e30 0
        *linexxxx $node3_x $min_y 0 $node3_x 1e30 0
    }
}

if {$modelType == "Full Model" || $modelType=="X-Half Model"} {
    set record_line [dict create]
    foreach dim $total_dummy {
        set node1_x [lindex $dim 0]
        set node1_y [lindex $dim 1]
        set node3_x [lindex $dim 2]
        set node3_y [lindex $dim 3]
        if {$node3_x > 0 && $node1_y < 0 && ![dict exists record_line $node3_x]} {
            set max_y $node1_y
            foreach dim_ref $total_dummy {
                set node1_x_ref [lindex $dim_ref 0]
                set node1_y_ref [lindex $dim_ref 1]
                set node3_x_ref [lindex $dim_ref 2]
                set node3_y_ref [lindex $dim_ref 3]
                if {$node3_x_ref == $node3_x && $node1_y_ref < 0} {
                    set max_y [expr max($max_y, $node1_y_ref)]
                }
            }

            dict set record_line $node3_x 1
            *linexxxx $node1_x $max_y 0 $node1_x -1e30 0
            *linexxxx $node3_x $max_y 0 $node3_x -1e30 0
        }
    }
}

### x-axis
### arg:
###  1. element_size
###  2. now_z
###  3. distance
###  4. default_comp_name
###  5. comp_list: [list ]
###  6. dim_list: [list [list ] [list ] ...]
###         * element: [comp node1_x node1_x node1_y node1_y]
###         * ensure the previous one's range is larger than later (the later component overcome the previous one if covered)

proc smart_drag {
    element_size
    now_z
    distance
    default_comp_name
    comp_list
    dim_list
} {
    *clearmark 1
    *clearmark 2

    set on_drag [expr floor($distance / $element_size)]
    set element_size [expr $distance / $on_drag]

    ### build the first layer
    if {[hm_entityexists comps name=$default_comp_name]} {
        *setcurrentcomponent $default_comp_name  ###???
    } else {
        *createentity comps name=$default_comp_name
    }
    *createvector 1 0 0 0 1
    *createmark nodes 1 "by box" -1e30 -1e30 [expr $now-0.1] 1e30 1e30 [expr $now+0.1] 0 inside 1 1 0
    *meshdragelements2 1 1 $element_size 1 0 0 1 ###???
    for {set i 0} {$i < [llength $comp_list]} {incr i 1} {
        set comp_name [lindex $comp_list $i]
        set node1_x [lindex [lindex $dim_list $i] 0]
        set node1_y [lindex [lindex $dim_list $i] 1]
        set node3_x [lindex [lindex $dim_list $i] 2]
        set node3_y [lindex [lindex $dim_list $i] 3]

        *createmark elems 1 "by box" [expr $node1_x-0.1] [expr $node1_y-0.1] [expr $now-0.1] [expr $node3_x+0.1] [expr $node3_y+0.1] [expr $now+$element_size+0.1] 0 inside 1 1 0
        if {![hm_entityexists comps name=$comp_name]} {
            *createentity comps name=$comp_name
        }  
        *movemark elems 1 comp_name
    }

    ### build the others layer
    if { $on_drag > 1} {
        *clearmark 1 ###??? necessary
        *clearmark 2 ###??? necessary
        *createmark nodes 1 "by box" -1e30 -1e30 [expr $now+$element_size-0.1] 1e30 1e30 [expr $now+$element_size+0.1] 0 inside 1 1 0
        *meshdragelements2 1 1 [expr $distance - $element_size] [expr $on_drag-1] 0 0 0 ###???
    }

    return [$distance + $now_z]
}
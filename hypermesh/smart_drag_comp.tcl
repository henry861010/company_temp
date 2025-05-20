### param:
###     * layer_info_list: [list layer_info ...]
###            * layer_info: [list z [list [material node1_x node1_y node3_x node3_y] ...]]
###                 * z: the begin of the material
###                 * [material node1_x node1_y node3_x node3_y]
###                     * material
###                         * END
###                     * node1_x/node1_y/node3_x/node3_y
###                 * NOTE: 
###                     * must add the end of the material

proc smart_drag_comp {
    element_size
    now_z
    layer_info_list
    default_material
} {
    proc smart_drag_comp_compare { a b } { return [expr [lindex $a 0] > [lindex $b 0]]}

    ### sort the list base on the z
    set temp_layer_info_list [lsort -command smart_drag_comp_compare $layer_info_list]
    set layer_info_list [list ]

    puts "$temp_layer_info_list"
    puts ""

    set pre_z [lindex [lindex $temp_layer_info_list 0] 0]
    set pre_dim [lindex [lindex $temp_layer_info_list 0] 1]
    for {set i 1} {$i < [llength $temp_layer_info_list]} {incr i 1} {
        set temp_z [lindex [lindex $temp_layer_info_list $i] 0]
        set temp_dim [lindex [lindex $temp_layer_info_list $i] 1]

        ### replace the DEFAULT material to default_material
        for {set j 0} {$j < [llength $temp_dim]} {incr j 1} {
            set temp [lindex $temp_dim $j]
            if {[lindex $temp 0] == "END"} {
                lset temp 0 $default_material
                lset temp_dim $j $temp
            }
        }

        ### merge the layer_infos into one layer if they are at the same height
        if {$pre_z == $temp_z} {
            set pre_dim [concat $pre_dim $temp_dim]
        } else {
            lappend layer_info_list [list [expr $pre_z + $now_z] $pre_dim]
            set pre_z $temp_z
            set pre_dim $temp_dim
        }
    }
    if {$pre_z != [lindex [lindex $layer_info_list end] 0] } {
        lappend layer_info_list [list [expr $pre_z + $now_z] $pre_dim]
    }

    puts "$layer_info_list"

    ### drag the element
    set section_z_list [list]
    for {set i 0} {$i < [expr [llength $layer_info_list] - 1]} {incr i 1} {
        set layer_info [lindex $layer_info_list $i]
        set layer_info_next [lindex $layer_info_list [expr $i + 1]]

        set node1_z [lindex $layer_info 0]
        set node3_z [lindex $layer_info_next 0]

        if {$i == 0} {
            set section_z [smart_drag2 $element_size $node1_z $node3_z $default_material $layer_info]
            set section_z_list [concat $section_z_list $section_z]
        } else {
            set section_z [smart_drag2 $element_size $node1_z $node3_z "" $layer_info]
            set section_z_list [concat $section_z_list $section_z]
        }
    }

    return $section_z_list
}

proc smart_drag2 {
    element_size
    node1_z
    node3_z
    default_material
    layer_info
} {
    return [list]
}

proc test1 {} {
    set element_size 0
    set now_z 0
    set default_material "aaaa"

    set comp1 [list [list 0 [list [list "comp1_1" 0 0 10 10]]] [list 10 [list [list "comp1_2" 0 0 10 10]]] [list 20 [list [list "comp1_3" 0 0 10 10]]] [list 30 [list [list "comp1_4" 0 0 10 10]]]]
    set comp2 [list [list 5 [list [list "comp2_1" 0 0 10 10]]] [list 15 [list [list "comp2_2" 0 0 10 10]]] [list 35 [list [list "comp2_3" 0 0 10 10]]] [list 40 [list [list "comp2_4" 0 0 10 10]]]]
    set layer_info_list [concat $comp1 $comp2]

    smart_drag_comp $element_size $now_z $layer_info_list $default_material
}
#puts "test1 begin"
#test1

proc test2 {} {
    set element_size 0
    set now_z 0
    set default_material "aaaa"

    set comp1 [list [list 0 [list [list "comp1_1" 0 0 10 10]]] [list 10 [list [list "comp1_2" 0 0 10 10]]] [list 20 [list [list "comp1_3" 0 0 10 10]]] [list 30 [list [list "comp1_4" 0 0 10 10]]]]
    set comp2 [list [list 5 [list [list "comp2_1" 0 0 10 10]]] [list 10 [list [list "comp2_2" 0 0 10 10]]] [list 10 [list [list "comp2_3" 0 0 10 10]]] [list 40 [list [list "comp2_4" 0 0 10 10]]]]
    set layer_info_list [concat $comp1 $comp2]

    smart_drag_comp $element_size $now_z $layer_info_list $default_material
}
#puts "test2 begin"
#test2

proc test3 {} {
    set element_size 0
    set now_z 0
    set default_material "aaaa"

    set comp1 [list [list 0 [list [list "comp1_1" 0 0 10 10]]] [list 10 [list [list "comp1_2" 0 0 10 10]]] [list 20 [list [list "comp1_3" 0 0 10 10]]] [list 30 [list [list "END" 0 0 10 10]]]]
    set comp2 [list [list 5 [list [list "comp2_1" 0 0 10 10]]] [list 10 [list [list "comp2_2" 0 0 10 10]]] [list 10 [list [list "comp2_3" 0 0 10 10]]] [list 40 [list [list "END" 0 0 10 10]]]]
    set layer_info_list [concat $comp1 $comp2]

    smart_drag_comp $element_size $now_z $layer_info_list $default_material
}
puts "test3 begin"
test3
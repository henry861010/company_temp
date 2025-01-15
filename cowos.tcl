### comp_list: [list [list compName bottom top]]
### -> write the function to convert it

set dummy_cord_list %dummy_cord_list%

###set dis_list -> get from the previous model
set moldingArea_comp_list %molding_comp_list%
set dieArea_comp_list0 %dieArea_comp_list0%
set dieArea_comp_list1 %dieArea_comp_list1%
set dieArea_comp_list2 %dieArea_comp_list2%
set dieArea_comp_list3 %dieArea_comp_list3%

set moldingArea_compMesh_list [convert_compMeshList $dis_list $moldingArea_comp_list]
set dieArea_compMesh_list0 [convert_compMeshList $dis_list $dieArea_comp_list0]
set dieArea_compMesh_list1 [convert_compMeshList $dis_list $dieArea_comp_list1]
set dieArea_compMesh_list2 [convert_compMeshList $dis_list $dieArea_comp_list2]
set dieArea_compMesh_list3 [convert_compMeshList $dis_list $dieArea_comp_list3]

set spaceSizeB %spaceSizeB%
set spaceSizeA %spaceSizeA%

set dummySizeX %dummySizeX%
set dummySizeY %dummySizeY%

for {set i 0} {$i < [llength $dummy_cord_list]} {incr i 1} {
    set dummy_cord_list_i [lindex $dummy_cord_list $i]

    for {set j 0} {$j < [llength $dummy_cord_list_i]} {incr j 1} {
        set dummy_cord_list_i_j [lindex $dummy_cord_list_i $j]

        set baseX -1e30
        set baseY -1e30

        ### set the inner/outer position
        set spaceLeft $spaceSizeB
        set spaceRight $spaceSizeB
        set spaceTop $spaceSizeB
        set spaceBottop $spaceSizeB
        if {$i == 1} {
            set spaceBottop $spaceSizeA
        } else if{$i == 2} {
            set spaceBottop $spaceSizeA
            set spaceLeft $spaceSizeA
        }

        ### set the dummy die at each layer
        switch $j {
            0 { set dieArea_compMesh_list $dieArea_compMesh_list0 }
            1 { set dieArea_compMesh_list $dieArea_compMesh_list1 }
            2 { set dieArea_compMesh_list $dieArea_compMesh_list2 }
            3 { set dieArea_compMesh_list $dieArea_compMesh_list3 }
        }

        set coordinate [lindex $dummy_cord_list_i_j $0]
        set inner1X [lindex $coordinate 0]
        set inner1X [lindex $coordinate 1]
        set inner3X [lindex $coordinate 2]
        set inner3X [lindex $coordinate 3]
        set outer1X [lindex $coordinate 4]
        set outer1X [lindex $coordinate 5]
        set outer3X [lindex $coordinate 6]
        set outer3X [lindex $coordinate 7]
        set bias_angle [lindex $coordinate 8]
        build_DW $dis_list $moldingArea_compMesh_list $dieArea_compMesh_list $inner1X $inner1Y $inner3X $inner3Y $outer1X $outer1Y $outer3X $outer3Y

        for {set k 1} {$k < [llength $dummy_cord_list_i_j]} {incr k 1} {
            set coordinate [lindex $dummy_cord_list_i_j $k]
            set outer1X_copy [lindex $coordinate 0]
            set outer1X_copy [lindex $coordinate 1]
            set outer3X_copy [lindex $coordinate 2]
            set outer3X_copy [lindex $coordinate 3]
            set bias_angle [lindex $coordinate 8]
            set angle [lindex $coordinate 4]
            copy_aaa  $outer1X $outer1Y $outer3X $outer3Y $outer1X_copy $outer1Y_copy $outer3X_copy $outer3Y_copy [expr $angle - bias_angle]
        }
    }
}

#################################

proc convert_compMeshList { dis_list com_list} {
    set comp_mesh_list [list ]
    set dis_index 0
    set now_y 0

    for {set i 0} {$i < [llength $com_list]} {
        set comp_layer [lindex $com_list $i]
        set compName [lindex $comp_layer 0]
        set compTop [lindex $comp_layer 1]

        while {$now_y < [llength $dis_list] && [expr $now_y + [lindex $dis_list $dis_index]] <= $compTop} {
            set comp_mesh_list [lappend comp_mesh_list $compName]
            set dis_index [expr $dis_index + 1]
            set now_y [expr $now_y + [lindex $dis_list $dis_index]]
        }
    }
    return comp_mesh_list
}


proc _createmark_by_2d {
    entity_type
    mark
    type
    dim
    node1_z
    node3_z
} {
    if {$type == "BOX"} {
        set node1_x [lindex $dim 0]
        set node1_y [lindex $dim 1]
        set node1_z $node1_z
        set node3_x [lindex $dim 2]
        set node3_y [lindex $dim 3]
        set node3_z $node3_z
        *createmark $entity_type $mark "by box" [expr $node1_x - 0.1] [expr $node1_y - 0.1] [expr $node1_z - 0.1] [expr $node3_x + 0.1] [expr $node3_y + 0.1] [expr $node3_z + 0.1] 0 inside 1 0 0
    } elseif {$type == "CONE"} {
        NOT IMPLEMENT NOW !!!
        *createmark $entity_type $mark "by cone" x y z i j k rb rt h inside 1 0 0
    }
}

proc drag {
    element_size
    distance
    layer_info
} {
    set faces [dict get $layer_info faces]
    set z [dict get $layer_info z]

    ### detemine the drag number & drag distance
    set drag_num [expr floor(double($element_size) / $element_size)]
    if {[expr double($element_size) % $element_size] != 0} {
        set drag_num [expr $drag_num + 1]
        set element_size [expr double($distance) / double(drag_num)]
    }

    ### drag one layer
    *createmark nodes 1 "by box" -1e30 -1e30 [expr $z - 0.1] 1e30 1e30 [expr $z +0.1]  0 inside 1 0 0
    if {[hm_marklength nodes 1] == 0} {
        *createmark elems 1 "by box" -1e30 -1e30 [expr $z - 0.1] 1e30 1e30 [expr $z +0.1]  0 inside 1 0 0
    }
    *createvector 1 0 0 1
    *meshdragelements2 1 1 $element_size 1 1 0 1

    foreach face $faces {
        set face_type [dict get $face type]
        set face_dim [dict get $face dim]
        set face_material [dict get $face material]
        set face_holes [dict get $face holes]
        set face_metals [dict get $face metals]

        ### get the target face and assign to "mark 1"
        _createmark_by_2d elems 1 $face_type $face_dim $z [expr $z + $element_size]
        foreach hole $face_holes {
            set hole_type [dict get $hole hole]
            set hole_dim [dict get $hole dim]
            _createmark_by_2d elems 2 $hole_type $hole_dim $z [expr $z + $element_size]

            *markdifference elems 1 elems 2
        }

        ### exclude the parts of metal where are the "CONTINUE" type
        foreach metal $face_metals {
            set metal_type [dict get $metal type]
            set metal_material [dict get $metal material]
            if {$metal_type == "CONTINUE"} {
                *createmark elems 2 "by comp" $metal_material
                *markdifference elems 1 $entity_type 2
            }
        }

        ### assign the metal
        foreach metal $face_metals {
            set metal_type [dict get $metal type]
            set metal_material [dict get $metal material]
            set metal_density [dict get $metal density]
            if {$metal_type == "NORMAL"} {
                assign_metal_density_mark1 $metal_material $metal_density
                *createmark elems 2 "by comp" $metal_material
                *markdifference elems 1 elems 2
            }
        }

        ### move the element to the target
        *movemark elems 1 $face_material

        ### drag the others layer
        *meshdragelements2 1 1 [expr $distance - $element_size] [expr $drag_num - 1] 1 0 1
    }
}
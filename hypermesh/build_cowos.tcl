source "/smart_drag.tcl"

### -------------------------------- build 2d mesh ----------------------------------
set cowos_node1_x %cowos_node1_x%
set cowos_node1_y %cowos_node1_y%
set cowos_node3_x %cowos_node3_x%
set cowos_node3_y %cowos_node3_y%
set lsi_dim_list %lsi_dim_list%   ### [list [list node1_x/y node3_x/y] [] [] ... ]
set soc_dim_list %soc_dim_list%   ### [list [list node1_x/y node3_x/y] [] [] ... ]
set hbm_dim_list %hbm_dim_list%   ### [list [list node1_x/y node3_x/y] [] [] ... ]

### [build 2d mesh] CoWoS-L
*createnode $cowos_node1_x $cowos_node1_y 0 0 0 0
*createnode $cowos_node3_x $cowos_node1_y 0 0 0 0
*createnode $cowos_node3_x $cowos_node3_y 0 0 0 0
*createnode $cowos_node1_x $cowos_node3_y 0 0 0 0
*createlist nodes 1 -4 -3 -2 -1
*surfacesplineonnodesloop2 1 0
*createmark nodes 1 -4 -3 -2 -1
*deletemark nodes 1

### [build 2d mesh] LSI
foreach lsi_dim $lsi_dim_list {
    set node1_x [lindex $lsi_dim 0]
    set node1_y [lindex $lsi_dim 1]
    set node3_x [lindex $lsi_dim 2]
    set node3_y [lindex $lsi_dim 3]

    *linecreatestraight $node1_x $node1_y 0 $node3_x $node1_y 0
    *linecreatestraight $node3_x $node1_y 0 $node3_x $node3_y 0
    *linecreatestraight $node3_x $node3_y 0 $node1_x $node3_y 0
    *linecreatestraight $node1_x $node3_y 0 $node1_x $node1_y 0
}

### [build 2d mesh] soc
foreach soc_dim $soc_dim_list {
    set node1_x [lindex $soc_dim 0]
    set node1_y [lindex $soc_dim 1]
    set node3_x [lindex $soc_dim 2]
    set node3_y [lindex $soc_dim 3]

    *linecreatestraight $node1_x $node1_y 0 $node3_x $node1_y 0
    *linecreatestraight $node3_x $node1_y 0 $node3_x $node3_y 0
    *linecreatestraight $node3_x $node3_y 0 $node1_x $node3_y 0
    *linecreatestraight $node1_x $node3_y 0 $node1_x $node1_y 0
}

### [build 2d mesh] hbm
foreach hbm_dim $hbm_dim_list {
    set node1_x [lindex $hbm_dim 0]
    set node1_y [lindex $hbm_dim 1]
    set node3_x [lindex $hbm_dim 2]
    set node3_y [lindex $hbm_dim 3]

    set node1_x_inner [lindex $hbm_dim 5]
    set node1_y_inner [lindex $hbm_dim 6]
    set node3_x_inner [lindex $hbm_dim 7]
    set node3_y_inner [lindex $hbm_dim 8]

    *linecreatestraight $node1_x $node1_y 0 $node3_x $node1_y 0
    *linecreatestraight $node3_x $node1_y 0 $node3_x $node3_y 0
    *linecreatestraight $node3_x $node3_y 0 $node1_x $node3_y 0
    *linecreatestraight $node1_x $node3_y 0 $node1_x $node1_y 0

    *linecreatestraight $node1_x_inner $node1_y_inner 0 $node3_x_inner $node1_y_inner 0
    *linecreatestraight $node3_x_inner $node1_y_inner 0 $node3_x_inner $node3_y_inner 0
    *linecreatestraight $node3_x_inner $node3_y_inner 0 $node1_x_inner $node3_y_inner 0
    *linecreatestraight $node1_x_inner $node3_y_inner 0 $node1_x_inner $node1_y_inner 0
}

### [build 2d mesh] do 2D mesh
*??? ### associate the line to the surface
*??? ### mesh the surface

### -------------------------------- 3D drag ----------------------------------
set now_z 0

### [3D drag] daf layer
set daf_thk %daf_thk%
set daf_material %daf_material%

set now_z [smart_drag $element_size $now_z $daf_thk $daf_material [list ] [list ]]

### [3D drag] mc1 layer
set mc1_thk %mc1_thk%
set mc1_material %mc1_material%

set now_z [smart_drag $element_size $now_z $mc1_thk $mc1_material [list ] [list ]]

### [3D drag] rw layer (structure???)
set lsi_material %lsi_material%
set lsi_thk $lsi_thk$


### [3D drag] fsRDL layer
set fsRDL_material %fsRDL_material%
set fsRDL_pm_material %fsRDL_pm_material%
set fsRDL_thk_list %fsRDL_thk_list% ### [list thick thick thick ...]

for {set i 0} {$i < [llength $fsRDL_thk_list]} {incr i 1} {
    set fsRDL_thk [lindex $fsRDL_thk_list $i]
    if { $i > 0} {
        set comp_name "${fsRDL_pm_material}dup[expr $i+1]"
    } else {
        set comp_name $fsRDL_pm_material
    }
    set now_z [smart_drag $element_size $now_z $fsRDL_thk $comp_name [list ] [list ]]
}

### [3D drag] cow layer
set hbm_layers $hbm_layers$
set hbm1_material %hbm_material%
set hpm1_thk %hpm1_thk%
set hbm2_material %hbm_material%
set hpm2_thk %hpm2_thk%

set soc_material %soc_material%

set mc_material %mc_material%

set microBump_material %microBump_material%
set microBump_thk %microBump_thk%

set underDie_thk %underDie_thk%
set underDie_thk %underDie_material%

set underDie_dim_list %underDie_dim_list%
set underDie_comp_list %underDie_comp_list%
set hbm1_dim_list %hbm1_dim_list%
set hbm1_comp_list %hbm1_comp_list%
set hbm2_dim_list %hbm2_dim_list%
set hbm2_comp_list %hbm2_comp_list%

### cow microBump layer
set now_z [smart_drag $element_size $now_z $microBump_thk $mc_material [???] [???]]  ###??? only under hbm and soc

### underDie layer
set now_z [smart_drag $element_size $now_z $underDie_thk $mc_material $underDie_comp_list $underDie_comp_list]

### hbm&soc layer
for {set i 0} {$i < hbm_layers} {incr i 1} {
    ### bottom
    set now_z [smart_drag $element_size $now_z $hpm1_thk $mc_material $hbm1_comp_list $hbm1_dim_list]

    ### top
    set now_z [smart_drag $element_size $now_z $hpm2_thk $mc_material $hbm2_comp_list $hbm2_dim_list]
}


### -------------------------------- 3D drag ----------------------------------
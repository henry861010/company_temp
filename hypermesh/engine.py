'''
obj
    z: float (the position in the parent object)
    type: BOX / CIRCLE / ...
    dim: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...
    layer: [layer, layer, layer, ...]
    obj: [obj, obj, ...]
layer
    thk: float
    material: string
    metal: string
    density: 0.0~100.0
    
layer
    z: float
    area: [
        type: BOX / CIRCLE / ...
        dim: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...
        hole: [hole, hole, ...]
        material: string
        metal: string
        density: 0.0~100.0
    ]
hole:
    type: BOX / CIRCLE / ...
    dim: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...
'''

def engine_get_z(obj, base_z, parent_obj) {
    layer_info_list = []
    
    ### get the main-object
    z = base_z
    for layer in obj["layer"]:
        ### get the hole
        hole = []
        for sub_obj in obj["obj"]:
            thk = sum({layer["thk"] for layer in sub_obj})
            begin_z = base_z + sub_obj["z"]
            end_z = base_z + sub_obj["z"] + thk
            if begin_z <= z and z <= end_z:
                hole.append({
                    "type": sub_obj["type"],
                    "dim": sub_obj["dim"]
                })
        
        ### append the layer info
        layer_info_list.append({
            "z": z,
            "area": [
                "type": obj["type"],
                "dim": obj["dim"],
                "material": layer["material"],
                "metal": layer["metal"],
                "density": obj["density"],
                "hole": hole
            ]
        })
        z += layer["thk"]
        
    ### append the end layer info
    ### connected-hole
    hole = []
    for sub_obj in parent_obj["obj"]:
        thk = sum({layer["thk"] for layer in sub_obj["layer"]})
        begin_z = base_z + sub_obj["z"]
        if begin_z == z:
            hole.append({
                "type": sub_obj["type"],
                "dim": sub_obj["dim"]
            })
            # ??? should add the dim identify
    ### default material
    temp_z = 0
    for layer in parent_obj["layer"]:
        if temp_z <= z and z <= (temp_z + layer["thk"]):
            default_material = layer["material"]
            break
        temp_z += layer["thk"]
        
    layer_info_list.append({
        "z": z,
        "area": [
            "type": obj["type"],
            "dim": obj["dim"],
            "material": ,
            "metal": default_material,
            "density": 0,
            "hole": hole
        ]
    })
        
    ### get the sub-object z info
    for sub_obj in obj["obj"]:
        temp_layer_info_list + engine_get_z(sub_obj, base_z, obj)
        layer_info_list = layer_info_list + temp_layer_info_list
    return layer_info_list
}

def merge_z(layer_info_list) {
    ### sort the list base on the "z"
    layer_info_list = sorted(layer_info_list, key=lambda item: item["z"])
    
    ### merge based on the z
    merged_layer_info_list = []
    z = layer_info_list[0]["z"]
    area_list = layer_info_list[0]["area"]
    for i in range(1, len(layer_info_list)):
        if z == layer_info_list[i]["z"]:
            area_list = area_list + layer_info_list[i]["area"]
        else:
            merged_layer_info_list.append({
                "z": z,
                "area": area_list
            })
            z = layer_info_list[i]["z"]
            area_list = layer_info_list[i]["area"]
    merged_layer_info_list.append({
        "z": z,
        "area": area_list
    })
    
    return merged_layer_info_list
}

'''
Obj
    z: Float
    face: Face
    layers: [layer, layer, layer, ...]
    objs: [Obj, Obj, ...]
    
Layer
    thk: Float
    material: String
    metals: [Metal ,Metal, Metal, ...]
    
z_info
    z: float
    area: [
        face: Face
        holes: [Face, Face, ...]
        materials: String
        metals: [Metal, Metal, ...]
    ]
    
Metal
    type: NORMAL / CONTINUE
    material: String
    density: Float(0.0 ~ 100.0)
    
Face
    type: BOX / CONE / ...
    dim: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...
    
Metal_Boundary
    type: START / END / CONTINUE_ALL / CONTINUE_BOTTOM / CONTINUE_TOP
    material: String
    density: Float(0.0 ~ 100.0)
    thk:
'''

def engine_set_abs_dim(obj, base_x, base_y, base_z):
    ### set the z
    obj.z_abs = obs.z + base_z
    
    ### set the x & y
    if obj.face.type == "BOX":
        if len(obj.face.dim) != 4:
            raise ValueError(f'[engine_set_abs_dim]: The length of dim list of "BOX" should be 4, object: {obj}')
        node1_x = obj.face.dim[0] + base_x
        node1_y = obj.face.dim[1] + base_y
        node3_x = obj.face.dim[2] + base_x
        node3_y = obj.face.dim[3] + base_y
        obj.face.dim_abs = [node1_x, node1_y, node3_x, node3_y]
    elif obj.face.type == "CONE":
        if len(obj.face.dim) != 3:
            raise ValueError(f'[engine_set_abs_dim]: The length of dim list of "CONE" should be 3, object: {obj}')
        center_x = obj.face.dim[0] + base_x
        center_y = obj.face.dim[1] + base_y
        radius = obj.face.dim[2]
        obj.face.dim_abs = [center_x, center_y, radius]
    else:
        raise ValueError(f'[engine_set_abs_dim]: "{obj["type"]""} is unknown type, object: {obj}')
    
    ### set the absolute dim & z of sub object
    for i in range(len(obj["obj"])):
        obj["objs"][i] = engine_set_abs_dim(obj["objs"][i], obj["dim"][0], obj["dim"][1], obj["z_abs"])
    
    return obj

def engine_get_z(obj, parent_obj):
    layer_info_list = []
    
    ### get the main-object
    z = obj[z_abs]
    for layer in obj["layers"]:
        ### get the hole
        hole = []
        for sub_obj in obj["objs"]:
            begin_z = sub_obj["z_abs"]
            end_z = sub_obj["z_abs"] + sum([layer["thk"] for layer in sub_obj["layers"]])
            if begin_z <= z and z < end_z:
                hole.append({
                    "type": sub_obj["type"],
                    "dim": sub_obj["dim_abs"]
                })
        
        ### append the layer info
        layer_info_list.append({
            "z": z,
            "faces": [{
                "type": obj["type"],
                "dim": obj["dim_abs"],
                "material": layer["material"],
                "metals": layer["metals"],
                "holes": hole
            }]
        })
        z += layer["thk"]
        
    ### append the end layer info
    hole = []
    default_material = ""
    if parent_obj != "MAIN":
        ### connected-hole
        for sub_obj in parent_obj["objs"]:
            if sub_obj["z_abs"] == z:
                hole.append({
                    "type": sub_obj["type"],
                    "dim": sub_obj["dim_abs"]
                })
                # ??? should add the dim identify
        ### default material
        temp_z = 0
        for layer in parent_obj["layers"]:
            if temp_z <= z and z <= (temp_z + layer["thk"]):
                default_material = layer["material"]
                break
            temp_z += layer["thk"]
        
    layer_info_list.append({
        "z": z,
        "faces": [{
            "type": obj["type"],
            "dim": obj["dim_abs"],
            "material": default_material,
            "metals": [],
            "holes": hole
        }]
    })
        
    ### get the sub-object z info
    for sub_obj in obj["objs"]:
        temp_layer_info_list = engine_get_z(sub_obj, obj)
        layer_info_list = layer_info_list + temp_layer_info_list
    return layer_info_list

def merge_z(layer_info_list):
    ### sort the list base on the "z"
    layer_info_list = sorted(layer_info_list, key=lambda item: item["z"])
    
    ### merge based on the z
    merged_layer_info_list = []
    z = layer_info_list[0]["z"]
    area_list = layer_info_list[0]["faces"]
    for i in range(1, len(layer_info_list)):
        if z == layer_info_list[i]["z"]:
            area_list = area_list + layer_info_list[i]["faces"]
        else:
            merged_layer_info_list.append({
                "z": z,
                "faces": area_list
            })
            z = layer_info_list[i]["z"]
            area_list = layer_info_list[i]["faces"]
    merged_layer_info_list.append({
        "z": z,
        "faces": area_list
    })
    
    return merged_layer_info_list

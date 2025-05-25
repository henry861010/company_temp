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
Face:
    type: BOX / CONE / ...
    dim: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...

'''

def engine_set_abs_dim(obj, base_x, base_y, base_z):
    ### set the z
    obj["z_abs"] = obs["z"] + base_z
    
    ### set the x & y
    if dim_type == "BOX":
        if len(obj["dim"]) != 4:
            raise ValueError(f'[engine_set_abs_dim]: The length of dim list of "BOX" should be 4, object: {obj}')
        node1_x = obj["dim"][0] + base_x
        node1_y = obj["dim"][1] + base_y
        node3_x = obj["dim"][2] + base_x
        node3_y = obj["dim"][3] + base_y
        obj["dim_abs"] = [node1_x, node1_y, node3_x, node3_y]
    elif dim_type == "CONE":
        if len(obj["dim"]) != 3:
            raise ValueError(f'[engine_set_abs_dim]: The length of dim list of "CONE" should be 3, object: {obj}')
        center_x = obj["dim"][0] + base_x
        center_y = obj["dim"][1] + base_y
        radius = obj["dim"][2]
        obj["dim_abs"] = [center_x, center_y, radius]
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

def get_box_obj(x, y, z, material, thk, node1_x, node1_y, node3_x, node3_y):
    layer = {
        "thk": thk,
        "material": material,
        "metals": []
    }
    obj = {
        "z": z,
        "type": "BOX",
        "dim": [node1_x, node1_y, node3_x, node3_y],
        "layers": [layer],
        "objs": []
    }
    return obj
    
def get_CONE_obj(x, y, z, material, thk, center_x, center_y, radius):
    layer = {
        "thk": thk,
        "material": material,
        "metals": []
    }
    obj = {
        "z": z,
        "type": "CONE",
        "dim": [center_x, center_y, radius],
        "layers": [layer],
        "objs": []
    }
    return obj   
    
def get_obj2():
    layer1 = {
        "thk": 10,
        "material": "obj2-1",
        "metals": []
    }
    layer2 = {
        "thk": 40,
        "material": "obj2-2",
        "metals": []
    }
    layer3 = {
        "thk": 40,
        "material": "obj2-3",
        "metals": []
    }
    
    obj = {
        "z": 10,
        "type": "BOX",
        "dim": [10, 10, 20, 20],
        "layers": [layer1, layer2, layer3],
        "objs": []
    }
    
    return obj

def get_main():
    layer1 = {
        "thk": 70,
        "material": "main-1",
        "metals": []
    }
    layer2 = {
        "thk": 100,
        "material": "main-2",
        "metals": []
    }
    
    obj2 = get_obj2()
    
    obj = {
        "z": 0,
        "type": "BOX",
        "dim": [0, 0, 30, 30],
        "layers": [layer1, layer2],
        "objs": [obj2]
    }
    return obj

obj_main = get_main()
temp_z_list = engine_get_z(obj_main, 0, "MAIN")
temp_z_list = merge_z(temp_z_list)

print(temp_z_list)
'''
Obj
    z: Float
    z_abs: Float
    face: Face
    layers: [layer, layer, layer, ...]
    objs: [Obj, Obj, ...]
    
Layer
    thk: Float
    material: String
    metals: [Metal ,Metal, Metal, ...]
    
Metal
    type: NORMAL / CONTINUE
    material: String
    density: Float(0.0 ~ 100.0)
    
Face
    type: BOX / CONE / ...
    dim: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...
    dim_abs: [node1_x, node1_y, node3_x, node3_y] / [center_x, center_y, diameter] / ...
    
Metal_Boundary
    type: THROUGHT / FROM_BOTTOM / FROM_TOP / FROM_BOTTOM_TO_OBJ / FROM_TOP_TO_OBJ
    material: String
    density: Float(0.0 ~ 100.0)
    thk: Float(optional)

z_info
    z: float
    area: [
        face: Face
        holes: [Face, Face, ...]
        materials: String
        metals: [Metal, Metal, ...]
    ]
'''

class Face:
    def __init__(self, type_: str, dim: list[float]):
        if type_ not in ["BOX", "CONE"]:
            raise ValueError(f'[Face init]: "{type_}" is the unknown type')
        if type_ == "BOX":
            if len(dim) != 4:
                raise ValueError(f'[Face init]: the length of BOX-dim should be 4')
        if type_ == "CONE":
            if len(dim) != 3:
                raise ValueError(f'[Face init]: the length of CONE-dim should be 3')
        
        self.type = type_
        self.dim = dim
        self.dim_abs = None
        
    def if_intersection(self, face = Face):
        return true

class Metal:
    def __init__(self, type: str, material: str, density: float):
        self.type = type_
        self.material = material
        self.density = density

class Layer:
    def __init__(self, thk: float, material: str, metals: list[Metal]):
        self.thk = thk
        self.material = material
        self.metals = metals

class Metal_Boundary:
    def __init__(self. _type: str, material: str, density: float, z: float):
        self.type = _type # TOP_START / THROUGHT / FROM_BOTTOM / FROM_TOP
        self.material = material
        self.density = density
        self.z = z
    
    def copy(self):
        return Metal_Boundary(_type = self.type, material = self.material, density = self.density, thk = self.thk)

class Obj:
    def __init__(self, z: float, face: Face):
        self.z = z
        self.face = face
        self.layers: []
        self.objs: []
        self.metal_boundaries: []
        self.thk = 0
        
        self.x_abs = None
        self.y_abs = None
        self.z_abs = None
        
    def set_metal_boundary(self, metal_boundary: Metal_Boundary):
        if metal_boundary.type == "THROUGHT":
            for sub_obj in self.objs:
                sub_obj.set_metal_boundary(metal_boundary: metal_boundary)
        elif metal_boundary.type == "FROM_BOTTOM":
            for sub_obj in self.objs:
                material = metal_boundary.material
                density = metal_boundary.density
                if  (sub_obj.z + sub_obj.thk) <= metal_boundary.z:
                    _type = "THROUGHT"
                    z = None
                elif sub_obj.z < metal_boundary.z and metal_boundary.z < (sub_obj.z + sub_obj.thk):
                    _type = "FROM_BOTTOM"
                    z = metal_boundary.z - sub_obj.z
                new_metal_boundary = Metal_Boundary(_type = _type, material = material, density = density, z = z)
                sub_obj.set_metal_boundary(metal_boundary: new_metal_boundary)
        elif metal_boundary.type == "FROM_TOP":
            for sub_obj in self.objs:
                material = metal_boundary.material
                density = metal_boundary.density
                if (self.thk - sub_obj.z) <= metal_boundary.z:
                    _type = "THROUGHT"
                    z = None
                elif (self.thk - sub_obj.z - sub_obj.thk) < metal_boundary.z and metal_boundary.z < (self.thk - sub_obj.z):
                    _type = "FROM_TOP"
                    z = metal_boundary.z - sub_obj.z
                new_metal_boundary = Metal_Boundary(_type = _type, material = material, density = density, z = z)
                sub_obj.set_metal_boundary(metal_boundary: new_metal_boundary)
        self.metal_boundaries.append(Metal_Boundary)

    def add_layer(self, layer: Layer):
        self.layers.append(layer)
        self.thk += layer.thk
        
    def add_subobj(self, subobj: Obj, metal_boundaries: [Metal_Boundary]):
        for metal_boundary in metal_boundaries:
            subobj.set_metal_boundary(metal_boundary)
        
        self.objs.append(subobj)

    def set_gap(self, material, z, gap, thk):
        print("aaaa")
        
    def set_abs_dim(self, base_x, base_y, base_z):
        ### set the z
        self.z_abs = self.z + base_z
        
        ### set the x & y
        if self.face.type == "BOX":
            if len(self.face.dim) != 4:
                raise ValueError(f'[engine_set_abs_dim]: The length of dim list of "BOX" should be 4, object: -')
            node1_x = self.face.dim[0] + base_x
            node1_y = self.face.dim[1] + base_y
            node3_x = self.face.dim[2] + base_x
            node3_y = self.face.dim[3] + base_y
            self.face.dim_abs = [node1_x, node1_y, node3_x, node3_y]
        elif self.face.type == "CONE":
            if len(self.face.dim) != 3:
                raise ValueError(f'[engine_set_abs_dim]: The length of dim list of "CONE" should be 3, object: -')
            center_x = self.face.dim[0] + base_x
            center_y = self.face.dim[1] + base_y
            radius = self.face.dim[2]
            self.face.dim_abs = [center_x, center_y, radius]
        else:
            raise ValueError(f'[engine_set_abs_dim]: "{obj["type"]""} is unknown type, object: -')
        
        ### set the absolute dim & z of sub object
        for subobj in self.objs:
            subobj.set_abs_dim(self.z_abs, self.face.dim[0], self.face.dim[1])

    def get_layer_info(self, parent_obj):
        layer_info_list = []
        
        ### get the main-object
        z = self.z_abs
        for layer_index, layer in enumerate(self.layers):
            ### get the hole
            hole = []
            for sub_obj in self.objs:
                begin_z = sub_obj.z_abs
                end_z = sub_obj.z_abs + sub_obj.thk
                if begin_z <= z and z < end_z:
                    hole.append({
                        "type": sub_obj.face.type,
                        "dim": sub_obj.face.dim_abs
                    })
            
            ### set the metal of layer & metal_boundary to each layers
            metals = []
            for metal in self.layer.metals:
                metals.append({
                    "type": metal.type,
                    "material": metal.material,
                    "density": metal.density
                })
            for metal_boundary in self.metal_boundaries:
                if metal_boundary.type == "THROUGHT":
                    metals.append({
                        "type": "CONTINUE",
                        "material": metal.material,
                        "density": metal.density
                    })
                elif metal_boundary.type == "FROM_BOTTOM":
                    if (z + layer.thk) <= metal_boundary.z:
                        metals.append({
                            "type": "CONTINUE",
                            "material": metal.material,
                            "density": metal.density
                        })
                elif metal_boundary.type == "FROM_TOP":
                    if metal_boundary.z < z:
                        metals.append({
                            "type": "CONTINUE",
                            "material": metal.material,
                            "density": metal.density
                        })
                    elif metal_boundary.z == z:
                        metals.append({
                            "type": "NORMAL",
                            "material": metal.material,
                            "density": metal.density
                        })
            
             ### append the layer info
            
            layer_info_list.append({
                "z": z,
                "faces": [{
                    "type": self.face.type,
                    "dim": self.face.dim_abs,
                    "material": layer.material,
                    "metals": metals,
                    "holes": hole
                }]
            })
            z += layer.thk
            
        ### append the end layer info
        hole = []
        default_material = ""
        if parent_obj != "MAIN":
            ### connected-hole
            for sub_obj in parent_obj.objs:
                if sub_obj.z_abs == z and self.face.if_intersection(face = sub_obj.face):
                    hole.append({
                        "type": sub_obj.face.type,
                        "dim": sub_obj.face.dim_abs
                    })
            ### default material
            temp_z = 0
            for layer in parent_obj.layers:
                if temp_z <= z and z <= (temp_z + layer.thk):
                    default_material = layer.material
                    break
                temp_z += layer.thk
                
        metals = []
        for metal_boundary in self.metal_boundaries:
            if metal_boundary.type == "THROUGHT" or metal_boundary.type == "FROM_TOP":
                metals.append({
                    "type": "CONTINUE",
                    "material": metal.material,
                    "density": metal.density
                })
            
        layer_info_list.append({
            "z": z,
            "faces": [{
                "type": self.face.type,
                "dim": self.face.dim_abs,
                "material": default_material,
                "metals": metals,
                "holes": hole
            }]
        })
            
        ### get the sub-object z info
        for sub_obj in self.objs:
            temp_layer_info_list = sub_obj.get_layer_info(self)
            layer_info_list = layer_info_list + temp_layer_info_list
            
        return layer_info_list
from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

'''
This is the wrapper function for Obj.build_cdb(). The purpose of Obj is to describe the geometry 
of the model. To generate a CDB file, the user should first create a 2D mesh with Mesh2D, and 
then extend it to a 3D mesh with Mesh3D. For convenience, this function allows users to build 
simple models directly with Obj. It wraps the meshing process by combining Mesh2D and Mesh3D, 
making it easier for users to generate a CDB without calling them separately.
1. build_cdb() provide two mesh strategy for user by param "algorithm_2D"
    1. "AUTO": Required using HyperMesh for both 2D and 3D meshing
    2. "CHECKERBOARD": default use Python for both 2D and 3D meshing
2. build_cdb() allow user use user-define 2D mesh by set param "mesh2D" with Mesh2D obj
    NOTE: the 2d meshing would not excuted and use 2D mesh in mesh2D directly

model_type
element_size
element_type
cdb_path
algorithm_2D: "AUTO"(default)/"CHECKERBOARD"
mesh2D: Mesh2D = None -> user define 2d mmesh
mesher_2D_type: "PYTHON"(default)/ "HYPERMESH"
mesher_3D_type: "PYTHON"(default) / "HYPERMESH"

NOTE:
algo_2D         "AUTO"                  "CHECKERBOARD"
mesher_2D_type  "HYPERMESH"             "PYTHON"/"HYPERMESH" 
mesher_3D_type  "PYTHON"/"HYPERMESH"    "PYTHON"/"HYPERMESH" 
* if mesh2D is setted, the 2D mesh would not excuted. (check you 2D mesh already mesh in mesh2D)
* if mesher_3D_type is "HYPERMESH", then the mesher_2D_type must be "HYPERMESH"

Obj.build_CDB(self, cdb_path, model_type="Full Model", isHMagent=True):
    ### center
    if self.face.type == "BOX":
        center_x = (self.face.dim[0] + self.face.dim[2])/2
        center_y = (self.face.dim[1] + self.face.dim[3])/2
    elif self.face.type == "CYLINDER":
        center_x = self.face.dim[0]
        center_y = self.face.dim[1]
    elif self.face.type == "POLYGON":
        center_x = -10000000
        center_y = -10000000
        
    ### ref node
    ref_x = -10000000
    ref_y = -10000000
    if model_type=="Quarter Model" and model_type=="Half-x Model"
        ref_x = center_x
    if model_type=="Quarter Model" and model_type=="Half-y Model"
        ref_y = center_y
    
    ### Algorithm
    if algorithm_2D == "CHECKERBOARD":
        faces = self.get_faces()
        x_list = []
        y_list = []
        
        ### obj geometry
        for face in faces:
            if face["type] == "CYLINDER" or face["type] == "POLYGON":
                raise ValueError("Cylinder/POLYGON not support CHECKERBOARD 2D mesh")
            elif face["type] == "BOX":
                if ref_x < face[dim][2] and ref_y < face[dim][3]:
                    x_list.append(face[dim][0])
                    x_list.append(face[dim][2])
                    y_list.append(face[dim][1])
                    y_list.append(face[dim][3])
                    
        ### user define mesh setting
        ???
                    
        if mesher_2D_type = "HYPERMESH":
            pattern_info = {
                "LINE": []
            }
            
            pkg1_x = -1000000
            pkg1_y = -1000000
            pkg3_x = 1000000
            pkg3_y = 1000000
            for x in x_list:
                pattern_info["LINE"].append([x, pkg1_y, x, pkg3_y])
            for y in y_list:
                pattern_info["LINE"].append([pkg1_x, y, pkg3_x, y])
            
            info_2D = {}
            info_2D["model_type] = model_type
            info_2D["element_size] = element_size
            info_2D["element_type] = element_type
            info_2D["face_type] = self.face.dim
            info_2D["face_dim] = self.face.type
            info_2D["pattern_info] = pattern_info
            info_2D["source_path"] = source_path
            info_2D["cdb_target"] = cdb_path 
            
    elif algorithm_2D == "AUTO":
        mesher_2D_type = "HYPERMESH"
        faces = self.get_faces()
        
        pattern_info = {
            "BOX": [],
            "CYLINDER": [],
            "POLYGON": [],
            "LINE": []
        }
        
        ### obj geometry
        for face in faces:
            if face["type"] == "BOX":
                if ref_x < face["dim"][2] and ref_y < face["dim"][3]:
                    pattern_info["BOX"].append(face["dim"])
            elif face["type"] == "CYLINDER":
                if ref_x < face["dim"][0]+face["dim"][2] and ref_y < face["dim"][1]+face["dim"][2]:
                    pattern_info["CYLINDER"].append(face["dim"])
            elif face["type"] == "POLYGON":
                pattern_info["POLYGON"].append(face["dim"])
                
        ### user define mesh setting
        ???
        
        info_2D = {}
        info_2D["model_type] = model_type
        info_2D["element_size] = element_size
        info_2D["element_type] = element_type
        info_2D["face_type] = self.face.dim
        info_2D["face_dim] = self.face.type
        info_2D["pattern_info] = pattern_info
        info_2D["source_path"] = source_path
        info_2D["cdb_target"] = cdb_path

    ### 3D info (temp for this version)
    info_3D = self.get_info_3D()
    info_3D["simulate_sbt_polish"] = ???
    info_3D["simulate_mc"] = ???

    ### mesher
    if mesher_2D_type = "PYTHON" and mesher_3D_type = "PYTHON":
        if mesh2D is None:
            mesh2D = Mesh2D()
            mesh2D.mesh_checkboard(element_size, x_list, y_list)
        mesh3D = Mesh3D()
        mesh3D.set_2D(mesh2D)
        mesh3D.engine(info_3D)
        mesh3D.write(path)
        
    elif mesher_2D_type = "HYPERMESH" and mesher_2D_type = "PYTHON":
        if mesh2D is None:
            mesh2D = Mesh2D()
            mesh2D.mesh_HyperMesh(info_2d)
        mesh3D = Mesh3D()
        mesh3D.set_2D(mesh2D)
        mesh3D.engine(info_3D)
        mesh3D.write(path)
        
    elif mesher_2D_type = "HYPERMESH" and mesher_2D_type = "HYPERMESH":
        mesh2D = Mesh2D()
        mesh2D.mesh_HyperMesh(info_2d, info_3D)

    elif mesher_2D_type = "PYTHON" and mesher_2D_type = "HYPERMESH":
        NO THIS TYPE !!!

--------

'''

main_obj = Obj()

element_size = 1
x_list = [0,100]
y_list = [0,100]
object_list = [] ### get from Obj()

mesh2D_obj = Mesh2D()
mesh2D_obj.mesh_checkerboard(element_size, x_list, y_list)

mesh3D_obj = Mesh3D()
mesh3D_obj.set_2D(mesh2D_obj)
mesh3D_obj.engine(object_list)

### show the result
mesh3D_obj.show_info()

# nodes, elements, element_comps, comps = mesh3D_obj.get_byIndex()
# node_ids, nodes, element_ids, elements_cdb, element_coords, element_comps, comps = mesh3D_obj.get()
        
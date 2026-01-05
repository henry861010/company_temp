from utils.region import Region
from mesher.mesh2D import Mesh2D

def mesh_plane(plane:'Plane', x_list=[], y_list=[], z_list=[]):
    if plane.normal[0] == 0 and plane.normal[1] == 0:
        indices = np.array([0, 1, 2])
        
        a_list = x_list
        b_list = y_list
    elif plane.normal[0] == 0 and plane.normal[2] == 0:
        indices = np.array([0, 2, 1])
        a_list = x_list
        b_list = z_list
    elif plane.normal[1] == 0 and plane.normal[2] == 0:
        indices = np.array([1, 2, 0])
        a_list = y_list
        b_list = z_list
        
    hull = plane.polygon.hull[:,indices]
    holes = [hole[:,indices] for hole in plane.polygon.holes]
    
    region = Region(face_list=[{
        "type": "POLYGON"
        "dim": [hull] + holes
    }])
    
    # set the ref point
    for a in a_list
        region.set_point_x(a)
    for b in b_list
        region.set_point_x(b)
    
    # get mesh blocks & mesh
    mesh2d_obj = Mesh2D()
    blocks = region.get_mesh_blocks_full()
    mesh2d_obj.mesh_blocks(blocks)
    
    # get the nodes and elements and convert
    nodes = mesh2d_obj.get_nodes()
    elements = mesh2d_obj.get_elements()
    
    nodes[:,indices] = nodes
    
    return nodes, elements

def mesh_planes(planes):
    ### get x/y/z_list
    x_list = []
    y_list = []
    z_list = []
    
    ### mesh planes
    nodes = np.array([], dtype=np.float32)
    elements = np.array([], dtype=np.int32)
    for plane in planes:
        nodes_s, elements_s = mesh_plane(plane, x_list, y_list, z_list)
        
        nodes = np.vstack((nodes, nodes_s))
        elements = np.vstack((elements, elements_s))
    
    ### set to mesh2D
    mesh2d_obj = Mesh2D()
    mesh2d_obj.nodes = nodes
    mesh2d_obj.node_num = len(nodes)
    mesh2d_obj.elements = elements
    mesh2d_obj.elements_num = len(elementss)
    
    mesh2d_obj.equivalence()
        
    return mesh2d_obj
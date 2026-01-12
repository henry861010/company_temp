import numpy as np
import matplotlib.path as mpath

def is_in_triangle(t1, t2, t3, points):
    return [True]

def is_tri_in_polygon(path_obj, node1, node2, node3):
    node = (node1 + node2 + node3) / 3
    is_inside = path_obj.contains_point([node])
    return np.all(is_inside)

def simplify_outline(outline):
    return outline

def cal_angle(p1, p2, p3):
    # Create vectors relative to the middle node (p2)
    u = np.array(p1) - np.array(p2)
    v = np.array(p3) - np.array(p2)
    
    # Calculate dot product and magnitudes
    dot_product = np.dot(u, v)
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    
    # Calculate the cosine of the angle
    # We clip the value to [-1, 1] to prevent tiny float errors from crashing acos
    cosine_angle = np.clip(dot_product / (norm_u * norm_v), -1.0, 1.0)
    
    angle_rad = np.arccos(cosine_angle)
    return np.degrees(angle_rad)

class ConnectNode:
    def __init__(self, coord):
        self.coord = np.array(coord, dtype=np.float32)
        self.neighbors = []
    
    def add_neighbor(self, neighbor:'ConnectNode'):
        if self not in self.neighbor.neighbors:
            self.neighbor.neighbors.append(self)
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
        
    def delete_neighbor(self, neighbor:'ConnectNode'):
        if neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        if self in  neighbor.neighbors
            neighbor.neighbors.remove(self)
            
    def get_neighbor(self, ref_node:'ConnectNode'):
        if ref_node != self.neighbors[0]
            return self.neighbors[0], cal_angle(self.neighbors[0].coord, self.coord, ref_node.coord)
        else:
            return self.neighbors[1], cal_angle(self.neighbors[1].coord, self.coord, ref_node.coord)
    
def mesh_connect(mesh2d_obj:'Mesh2D', node1, node2, outline, path_obj):
    def add(node2, node1, neighbor):
        '''
                node2
                /
            node1 - neighbor
        '''
        element_index = mesh2d_obj.add_element(node1.coord, node2.coord, neighbor.coord)
        node1.delete_neighbor(node2)
        node1.delete_neighbor(neighbor)
        node2.add_neighbor(neighbor)
        return element_index
        
    def delete(node2, node1, neighbor, element_index)
        '''
                node2
                /
            node1 - neighbor
        '''
        mesh2d_obj.delete_element(element_index)
        node1.add_neighbor(node2)
        node1.add_neighbor(neighbor1)
        node2.delete_neighbor(neighbor1)
    
    if len(node1.neighbors) == 1 and len(node2.neighbors) == 1:
        return True
    
    neighbor1, angle1 = node1.get_neighbor(node2)
    neighbor2, angle2 = node2.get_neighbor(node1)
    
    ### check if neighbor1 is valid
    isNeighbor1 = True
    if np.any(is_in_triangle(node1.coord, node2.coord, neighbor1.coord, outline+[neighbor2]))
        isNeighbor1 = False
    elif not is_tri_in_polygon(path_obj, node1.coord, node2.coord, neighbor1.coord):
        isNeighbor1 = False
        
    ### check if neighbor2 is valid
    isNeighbor2 = True
    if np.any(is_in_triangle(node1.coord, node2.coord, neighbor2.coord, outline+[neighbor1]))
        isNeighbor2 = False
    elif not is_tri_in_polygon(path_obj, node1.coord, node2.coord, neighbor2.coord):
        isNeighbor2 = False
        
    ### mesh
    if isNeighbor1 and isNeighbor2:
        if angle1 < angle2:
            ### mesh
            element_index = add(node2, node1, neighbor1)

            ### go next
            if mesh_connect(mesh2d_obj, neighbor1, node2, outline, path_obj)
                return True

            ### recorver
            delete(node2, node1, neighbor1, element_index)
        else:
            ### mesh
            element_index = add(node1, node2, neighbor2)
            
            ### go next
            if mesh_connect(mesh2d_obj, node1, neighbor2, outline, path_obj)
                return True

            ### recorver
            delete(node1, node2, neighbor2, element_index)
    if isNeighbor1:
        ### mesh
        element_index = add(node2, node1, neighbor1)
        
        ### go next
        if mesh_connect(mesh2d_obj, neighbor1, node2, outline, path_obj)
            return True

        ### recorver
        delete(node2, node1, neighbor1, element_index)
    if isNeighbor2:
        ### mesh
        element_index = add(node1, node2, neighbor2)
        
        ### go next
        if mesh_connect(mesh2d_obj, node1, neighbor2, outline, path_obj)
            return True

        ### recorver
        delete(node1, node2, neighbor2, element_index)
        
    return False
        
def connect(mesh2d_obj:'Mesh2D', outline):
    outline = np.array(outline)
    simple_outline = simplify_outline(outline)
    path_obj = mpath.Path(outline)
    
    ### build node tree
    node_list = [ConnectNode(outline[0])]
    for node in outline[1:]:
        node_obj = ConnectNode(node)
        node_obj.add_neighbor(node_list[-1])
        node_list.append(node_obj)
    node_list[-1].add_neighbor(node_list[0])
        
    ### find begin node1 & node2
    node1 = None
    node2 = None
    for i in range(len(node_list)):
        p0 = node_list[i-2].coord
        p1 = node_list[i-1].coord
        p2 = node_list[i].coord
        p3 = node_list[(i+1)%len(node_list)].coord
        area1 = np.abs((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0]))
        area2 = np.abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]))
        if area1 < 0.01 and area2 < 0.01:
            node1 = node_list[i-1]
            node2 = node_list[i]
            break
    
    ### mesh
    mesh_connect(mesh2d_obj, node1, node2, simple_outline, path_obj)             
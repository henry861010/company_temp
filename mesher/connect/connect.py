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

class ConnectNode:
    def __init__(self):
        self.coord = []
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
        return self.neighbors[0]

def mesh_connect(mesh2d_obj:'Mesh2D', node1, node2, simple_outline, path_obj):
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
    if np.any(is_in_triangle(node1.coord, node2.coord, neighbor1.coord, simple_outline+[neighbor2]))
        isNeighbor1 = False
    elif not is_tri_in_polygon(path_obj, node1.coord, node2.coord, neighbor1.coord):
        isNeighbor1 = False
        
    ### check if neighbor2 is valid
    isNeighbor2 = True
    if np.any(is_in_triangle(node1.coord, node2.coord, neighbor2.coord, simple_outline+[neighbor1]))
        isNeighbor2 = False
    elif not is_tri_in_polygon(path_obj, node1.coord, node2.coord, neighbor2.coord):
        isNeighbor2 = False
        
    ### mesh
    if isNeighbor1 and isNeighbor2:
        if angle1 < angle2:
            ### mesh
            element_index = add(node2, node1, neighbor1)

            ### go next
            if mesh_connect(mesh2d_obj, neighbor1, node2, simple_outline, path_obj)
                return True

            ### recorver
            delete(node2, node1, neighbor1, element_index)
        else:
            ### mesh
            element_index = add(node1, node2, neighbor2)
            
            ### go next
            if mesh_connect(mesh2d_obj, node1, neighbor2, simple_outline, path_obj)
                return True

            ### recorver
            delete(node1, node2, neighbor2, element_index)
    if isNeighbor1:
        ### mesh
        element_index = add(node2, node1, neighbor1)
        
        ### go next
        if mesh_connect(mesh2d_obj, neighbor1, node2, simple_outline, path_obj)
            return True

        ### recorver
        delete(node2, node1, neighbor1, element_index)
    if isNeighbor2:
        ### mesh
        element_index = add(node1, node2, neighbor2)
        
        ### go next
        if mesh_connect(mesh2d_obj, node1, neighbor2, simple_outline, path_obj)
            return True

        ### recorver
        delete(node1, node2, neighbor2, element_index)
        
    return False
        
    
                
import numpy as np
from utils.outline import get_outline
from utils.polygon import polygon_expand
'''
    nodes: (n, 3)
        * record the coordinates of each nodes
    elements: (m, 4)
        * record the reference node ids of each elements
'''

class Plane:
    def __init__(self, a=None, b=None, c=None, d=None, polygons=None):
        if self.a is None or self.b is None or self.c is None:
            self.normal = None
        else:
            self.normal = np.array([a, b, c], np.float32)
        self.d = d
        self.polygons = polygons
    
    # initialized
    def set_byNodes(self, p1, p2, p3):
        # Calculate normal vector
        v1 = p2 - p1
        v2 = p3 - p1
        normal = np.cross(v1, v2)
        
        norm_val = np.linalg.norm(normal)
        if norm_val < 1e-10:
            return None # Collinear points, cannot form a plane

        # 1. Normalize (a, b, c) to unit length
        a, b, c = normal / norm_val
        # 2. Calculate d
        d = -np.dot([a, b, c], p1)
        
        # 3. Standardize orientation: first non-zero coefficient must be positive
        # We check a, then b, then c, then d to ensure consistent sign
        coeffs = np.array([a, b, c, d])
        for val in coeffs:
            if abs(val) > 1e-10:
                if val < 0:
                    coeffs *= -1
                break
        
        temp =  tuple(np.round(coeffs, decimals=6))
        self.normal = temp[:3]
        self.d = temp[3]

    # get property
    def get_polygons(self):
        if self.polygons is None:
            raise ValueError("polygons is not setted")
        return self.polygons

    def get_normal(self):
        if self.normal is None:
            raise ValueError("normal is not setted")
        return self.normal

    def get_d(self):
        if self.d is None:
            raise ValueError("d is not setted")
        return self.d
    
    # others
    def get_intersections(self, plane:'Plane', expanding=0):
        """Returns the start and end point of the intersection segment."""

        def _intersect_edge_with_plane(p1, p2, plane_n, plane_d, eps=0.001):
            dot1 = np.dot(plane_n, p1) + plane_d
            dot2 = np.dot(plane_n, p2) + plane_d

            # Case 1: Both points are on the plane (Coplanar edge)
            if abs(dot1) < eps and abs(dot2) < eps:
                return None

            # Case 2: Edge is parallel to the plane but not on it
            if abs(dot1 - dot2) < eps:
                return None

            # Case 3: Points are on opposite sides (or one is exactly on the plane)
            if dot1 * dot2 <= eps:
                t = -dot1 / (dot2 - dot1)
                return [p1 + t * (p2 - p1)]
            
            return None

        def _is_point_in_polygon(point, polygons, normal):
            return True
            """Checks if a 3D point is inside a 3D polygon by projecting to 2D."""
            # Find the best 2D projection (drop the dimension where normal is largest)
            idx = np.argmax(np.abs(normal))
            p2d = np.delete(point, idx)
            poly2d = np.delete(polygon, idx, axis=1)
            
            # Standard Ray-Casting algorithm for 2D Point-in-Polygon
            inside = False
            n = len(poly2d)
            for i in range(n):
                p1 = poly2d[i]
                p2 = poly2d[(i + 1) % n]
                if ((p1[1] > p2d[1]) != (p2[1] > p2d[1])) and \
                (p2d[0] < (p2[0] - p1[0]) * (p2d[1] - p1[1]) / (p2[1] - p1[1] + 1e-9) + p1[0]):
                    inside = not inside
            return inside

        n1 = self.get_normal()
        d1 = self.get_d()
        polygons1 = polygon_expand(self.get_polygons(), expanding)
        
        n2 = plane.get_normal()
        d2 = plane.get_d()
        polygons2 = polygon_expand(plane.get_polygons(), expanding)
        
        # 1. Check if planes are parallel
        if np.abs(np.dot(n1, n2)) > 0.9999:
            return None  # Parallel or Co-planar (handled separately usually)

        intersection_points = []
        
        # 2. Check edges of poly1 against plane of poly2
        for poly1 in polygons1:
            for i in range(len(poly1)):
                pt = _intersect_edge_with_plane(poly1[i], poly1[(i+1)%len(poly1)], n2, d2)
                if pt is not None and _is_point_in_polygon(pt, polygons2, n2):
                    intersection_points.append(pt)
                
        # 3. Check edges of poly2 against plane of poly1
        for poly2 in polygons2:
            for i in range(len(poly2)):
                pt = _intersect_edge_with_plane(poly2[i], poly2[(i+1)%len(poly2)], n1, d1)
                if pt is not None and _is_point_in_polygon(pt, polygons1, n1):
                    intersection_points.append(pt)
                
        # Clean duplicates and return the segment
        if len(intersection_points) < 2:
            return []
        else:
            points = np.unique(np.array(intersection_points).round(decimals=6), axis=0)
            
            indices = points[:, 0].argsort()
            points = points[indices]
            
            intersections = []
            for i in range(len(points), 2):
                intersections.append(np.array([points[i], points[i+1]]))
                
            return intersections
        
    def is_normal(self):
        if (plane[1]==0 and plane[2]==0):
            return True
        if plane[0]==0 and plane[2]==0:
            return True
        if plane[0]==0 and plane[1]==0:
            return True
        return False

    def get_area(self):
        if self.polygons is None:
            raise ValueError("polygons is not setted")
        
        def _is_clockwise(polygon, reference_normal):
            """
            Identifies if a 3D polygon is CW or CCW relative to a reference normal.
            
            Formula:
            1. Area Vector: A_vec = 0.5 * sum(P_i x P_{i+1})
            2. Alignment: dot_product = A_vec ⋅ reference_normal
            """
            # Calculate the Area Vector (Right-Hand Rule)
            # A_vec = 0.5 * Σ (P_i × P_{i+1})
            cross_products = np.cross(polygon, np.roll(polygon, -1, axis=0))
            area_vector = 0.5 * np.sum(cross_products, axis=0)
            
            # Dot product tells us if area_vector aligns with reference_normal
            dot_product = np.dot(area_vector, reference_normal)
            
            if dot_product > 0:
                return False
            else:
                return True

        def _area(polygon, reference_normal):
            """
            Calculates the signed area of a 3D polygon.
            
            Mathematical Formula:
            1. Area Vector: A_vec = 0.5 * sum(P_i x P_{i+1})
            2. Signed Area: Area = A_vec ⋅ n_ref
            """
            if len(polygon) < 3:
                    return 0.0
                
            # Sum the cross products of adjacent polygon
            # np.roll shifts the array to align P_i with P_{i+1}
            cross_products = np.cross(polygon, np.roll(polygon, -1, axis=0))
            
            # The area vector is half the sum of these cross products
            area_vector = 0.5 * np.sum(cross_products, axis=0)
            
            # The scalar area is the magnitude (norm) of the area vector
            return np.linalg.norm(area_vector)
        
        area = 0
        for polygon in self.polygons:
            if _is_clockwise(polygon, self.normal)
                area += _area(polygon, self.normal)
            else:
                area -= _area(polygon, self.normal)
        
        return area

'''
    this function funtion group the elements where the element in the same planes 
    are in the same groupm and it would return the list of the Plane obj
    input
    * nodes: the list of the coordinates of nodes
    * elements: the list of the elements, each element record 4 ref node ids
    output
    * the list of the Plane obj
'''
def get_planes(nodes, elements, decimals=5):
    # 1. Vectorized plane calculation
    p1 = nodes[elements[:, 0]]
    p2 = nodes[elements[:, 1]]
    p3 = nodes[elements[:, 2]]

    v1 = p2 - p1
    v2 = p3 - p1
    normals = np.cross(v1, v2)

    # 2. Normalize
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms[norms == 0] = 1.0 
    abc = normals / norms
    d = -np.sum(abc * p1, axis=1, keepdims=True)
    planes = np.hstack([abc, d])

    # 3. Standardization (Fix sign ambiguity)
    # We find the first column (a, b, c, or d) that isn't zero and force it positive
    # For speed at 100M, we can just use the 'a' sign or a combination
    signs = np.sign(planes[:, 0:1]) # Use 'a' for sign
    # If 'a' is 0, use 'b', etc. A more robust way:
    first_nonzero = np.argmax(np.abs(planes) > 1e-9, axis=1)
    row_indices = np.arange(len(planes))
    signs = np.sign(planes[row_indices, first_nonzero]).reshape(-1, 1)
    planes *= signs

    # 4. Find Unique Planes and Group IDs
    planes_rounded = np.round(planes, decimals=decimals)
    unique_planes, group_ids = np.unique(planes_rounded, axis=0, return_inverse=True)

    # 5. Group element indices
    sorted_indices = np.argsort(group_ids)
    sorted_groups = group_ids[sorted_indices]
    boundaries = np.where(np.diff(sorted_groups) != 0)[0] + 1
    list_of_groups = np.split(sorted_indices, boundaries)

    plane_objs = []
    for plane, group in zip(unique_planes, list_of_groups):
        a, b, c, d = plane
        outlines = get_outline(nodes, elements[group], isSimple=True)
        plane_objs.append(Plane(a=a, b=b, c=c, d=d, polygons=outlines))
        
    return plane_objs
        
    

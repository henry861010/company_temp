import numpy as np
from utils.plane import get_planes

def get_intersect(line1, line2, eps=0.01):
    """
    Finds the intersection of two 3D lines.
    Each line is a numpy array of shape (2, 3).
    """
    # Define points and direction vectors
    A, B = line1[0], line1[1]
    C, D = line2[0], line2[1]
    
    v1 = B - A
    v2 = D - C
    
    # Check if lines are parallel (cross product is zero)
    cross_v1_v2 = np.cross(v1, v2)
    cross_norm_sq = np.dot(cross_v1_v2, cross_v1_v2)
    
    if cross_norm_sq < eps:
        return None  # Lines are parallel
    
    # Vector between starting points
    dc = C - A
    
    # Check if lines are coplanar using the scalar triple product
    # (dc . (v1 x v2)) must be 0 for them to intersect
    if abs(np.dot(dc, cross_v1_v2)) > eps:
        return None  # Lines are skew (don't intersect)

    # Solve for t (parameter for line 1)
    # Using the formula: t = ( (C-A) x v2 ) . (v1 x v2) / |v1 x v2|^2
    t = np.dot(np.cross(dc, v2), cross_v1_v2) / cross_norm_sq
    
    # Calculate the intersection point
    intersection_point = A + t * v1
    
    return intersection_point

def decorner(nodes, elements, elements_size, filter="NORMAL"):
    # find the plane
    plane_objs = get_planes(nodes, elements)
    
    # find the plane which normal to x/y/z axis only
    plane_objs_n = []
    if filter == "NORMAL":
        for plane_obj in plane_objs:
            if plane_obj.is_normal():
                plane_objs_n.append(plane_obj)
    
    # find the outline of each plane
    for plane1_obj in plane_objs:
        interections = []
        
        # find the intersection between plane1_obj and all plane_objs
        for plane2_obj in plane_objs:
            if plane1_obj != plane2_obj:
                plane_inters = plane1_obj.get_intersections(plane=plane2_obj, expanding=elements_size)
                interections += plane_inters
                
        # new outline of plane1_obj
        new_polygons = []
        new_polygon = []
        intersection_now = interections[0]
        interections = interections[1:]
        while interections:
            isSet = False
            for index, intersection in enumerate(intersections):
                inter_point = get_intersect(intersection_now, intersection)
                if inter_point is not None:
                    new_polygon.append(inter_point)
                    
                    # if the len of new_polygon is zero, add to end, it ensure first intersection would get tow point
                    if len(new_polygon) == 0:
                        intersections.append(intersection_now)
                    
                    # set intersection as new intersection_now and pop it from list
                    intersection_now = intersection
                    intersections.pop(index)
                    isSet = True
                    break
                
            if not isSet:
                intersections = intersections[:-1]
                new_polygons.append(new_polygon)
                new_polygon = []
        if new_polygon:
            new_polygons.append(new_polygon)
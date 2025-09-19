import random
from mesh3D import Mesh3D
from mesh2D import Mesh2D
from vision import Vision

random.seed(1)

def cal_vertical(len_x, len_y, sub_len, density, space=100):
    """
    Generate coordinates for vertical or horizontal strips within a region.
    
    Args:
        len_x (float): Length of the region in x direction.
        len_y (float): Length of the region in y direction.
        sub_len (float): Desired approximate sub-strip length.
        density (float): Percentage of strips to keep (0–100).
    
    Returns:
        list of [x1, y1, x2, y2] representing rectangles.
    """
    coords = []
    
    total_num = int(len_x / sub_len)
    sub_len = len_x / total_num
    rect_count = int(total_num * density / 100)
    chosen = random.sample(range(total_num), rect_count)

    for idx in chosen:
        x1 = idx * sub_len
        x2 = (idx + 1) * sub_len
        
        coords.append([x1, 0, x2, len_y])
        coords.append([x1, 0, x2, len_y])
    return coords
    
def cal_horizon(len_x, len_y, sub_len, density, space=100):
    """
    Generate coordinates for vertical or horizontal strips within a region.
    
    Args:
        len_x (float): Length of the region in x direction.
        len_y (float): Length of the region in y direction.
        sub_len (float): Desired approximate sub-strip length.
        density (float): Percentage of strips to keep (0–100).
    
    Returns:
        list of [x1, y1, x2, y2] representing rectangles.
    """
    coords = []
    
    total_num = int(len_y / sub_len)
    sub_len = len_y / total_num
    rect_count = int(total_num * density / 100)
    chosen = random.sample(range(total_num), rect_count)

    for idx in chosen:
        y1 = idx * sub_len
        y2 = (idx + 1) * sub_len
        coords.append([0, y1, len_x, y2])

    return coords
    
def cal_center(len_x, len_y, coords1, coords2, density):
    """
    Pick random intersection cells (rectangles) between coords1 & coords2
    until the accumulated area reaches the requested density of the full region.

    Args:
        len_x, len_y: size of the full region (area = len_x * len_y)
        coords1: rectangles (e.g., vertical strips) [x1,y1,x2,y2]
        coords2: rectangles (e.g., horizontal strips) [x1,y1,x2,y2]
        density: percent of total area to cover (0..100)

    Returns:
        List of intersection coords whose total area ≈ density% of region.
    """

    ### Clamp density to [0, 100]
    total_area = len_x * len_y
    target_area = total_area * density / 100.0
    if target_area <= 0.0:
        return []

    ### find intersections
    intersections = []
    for vx1, vy1, vx2, vy2 in coords1:
        for hx1, hy1, hx2, hy2 in coords2:
            x1 = max(vx1, hx1)
            y1 = max(vy1, hy1)
            x2 = min(vx2, hx2)
            y2 = min(vy2, hy2)
            if (x2 - x1) > 0 and (y2 - y1) > 0:
                intersections.append([x1, y1, x2, y2])
    if not intersections:
        return []

    ### select the metal are
    random.shuffle(intersections)
    target_coords = []
    covered = 0.0
    for x1, y1, x2, y2 in intersections:
        area = (x2 - x1) * (y2 - y1)
        target_coords.append([x1, y1, x2, y2])
        covered += area
        if covered >= target_area:
            break

    return target_coords

def generate_area(len_x, len_y, metal_coords, mat_base, mat_metal):
    area_list = []
    
    ### base area
    area_list.append({
        "type": "BOX",
        "dim": [0, 0,len_x, len_y],
        "material": mat_base
    })
    
    ### metal are
    for metal_coord in metal_coords:
        area_list.append({
            "type": "BOX",
            "dim": [metal_coord[0], metal_coord[1], metal_coord[2], metal_coord[3]],
            "material": mat_metal
        })
        
    return area_list
            

layer_thk_list = [5,5,5,5,5,5,5,5,5]
layer_len_list = [5,5,5,5,5,5,5,5,5]
layer_density_list = [40,5,40,5,40,5,40,5,40]
material_base = "PM"
material_metal = "METAL"

element_size = 1
len_x = 500
len_y = 500

mesh2D_obj = Mesh2D()
mesh2D_obj.mesh_checkerboard(element_size, [0,len_x], [0,len_y])

mesh3D_obj = Mesh3D()
mesh3D_obj.set_2D(mesh2D_obj)

### calculate the metal area
coords_list = []
isVertical = True
for i, (len, density) in enumerate(zip(layer_len_list, layer_density_list)):
    if i % 2 == 0:
        if isVertical:
            print(f"{i} vertical")
            coords = cal_vertical(len_x, len_y, len, density)
            isVertical = False
        else:
            print(f"{i} horizon")
            coords = cal_horizon(len_x, len_y, len, density)
            isVertical = True
        coords_list.append(coords)
    else:
        print(f"{i} center")
        coords_list.append([])

for i, density in enumerate(layer_density_list):
    if i % 2 == 1:
        pre_coords = coords_list[i-1]
        post_coords = coords_list[i+1]
        coords_list[i] = cal_center(len_x, len_y, pre_coords, post_coords, density)
        
### begin to drag
z = 0
for coords, thk in zip(coords_list, layer_thk_list):
    areas = generate_area(len_x, len_y, coords, material_base, material_metal)
    for area in areas:
        mesh3D_obj.organize(area)
    mesh3D_obj.drag(element_size, z, z + thk)
    z += thk
    
### show (debug)
mesh3D_obj.show_info()

vision_obj = Vision()
nodes, elements, element_comps, comps = mesh3D_obj.get_byIndex()
vision_obj.set(comps, elements, element_comps, nodes)
vision_obj.show()
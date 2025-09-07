from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()

l = 10
mesh2D_obj.mesh_checkerboard(1, [0,l], [0, l])
indices = mesh2D_obj.search_element("CYLINDER", [0, 0, l], isReverse=True)

mesh2D_obj.delete_element(indices)
mesh2D_obj.show_info()
mesh2D_obj.show_graph_2D()

outline_list, outline_coord_list = mesh2D_obj.get_outline()
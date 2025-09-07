from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()

l = 2
mesh2D_obj.mesh_checkerboard(1, [0,l], [0, l])
mesh2D_obj.mesh_checkerboard(1, [0,l], [l, 2*l])

mesh2D_obj.show_info()
mesh2D_obj.equivalence()
mesh2D_obj.show_info()
mesh2D_obj.show_graph_2D()
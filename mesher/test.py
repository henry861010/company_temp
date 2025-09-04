from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()
mesh2D_obj.build_checkerboard(1, [0,1000], [0, 1000])
a = mesh2D_obj.get_outline()
print(a)
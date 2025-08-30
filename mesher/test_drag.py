from mesh2D import Mesh2D
from mesh3D import Mesh3D

mesh2D_obj = Mesh2D()
mesh2D_obj.build_checkerboard(1,[0,3],[0,3])

mesh3D_obj = Mesh3D()
mesh3D_obj.initial(mesh2D_obj)

area1 = {
    "type": "BOX",
    "dim": [0,0,2,2],
    "material": "comp1"
}
mesh3D_obj.organize(area1)
mesh3D_obj.drag(1,0,2)
mesh3D_obj.drag(1,2,5)

print(mesh3D_obj.nodes[mesh3D_obj.elements])
mesh3D_obj.show_info()
mesh3D_obj.show_graph_2D()

        
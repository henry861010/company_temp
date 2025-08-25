from mesh2D import Mesh2D
from mesh3D import Mesh3D

mesh2D_obj = Mesh2D()
mesh2D_obj.build_checkerboard(1,[0,100],[0,100])

mesh3D_obj = Mesh3D()
mesh3D_obj.initial(mesh2D_obj)

area = {
    "type": "BOX",
    "dim": [20,20,80,80],
    "holes": [{
        "type": "BOX",
        "dim": [30,30,50,50]
    }],
    "metals": [{
        "type": "NORMAL",
        "material": "comp2",
        "density": 50
    }],
    "material": "comp1"
}
mesh3D_obj.organize(area)

mesh3D_obj.show_graph_2D()
        
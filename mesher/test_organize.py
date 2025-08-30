from mesh2D import Mesh2D
from mesh3D import Mesh3D

mesh2D_obj = Mesh2D()
mesh2D_obj.build_checkerboard(1,[0,100],[0,100])

mesh3D_obj = Mesh3D()
mesh3D_obj.initial(mesh2D_obj)

area1 = {
    "type": "BOX",
    "dim": [10,10,90,90],
    "holes": [{
        "type": "BOX",
        "dim": [10,10,40,40]
    }],
    "metals": [
        {
            "type": "NORMAL",
            "material": "metal1",
            "density": 10,
            "holes":[
                {
                    "type": "BOX",
                    "dim": [50, 50, 60, 60]
                }
            ]
        }, {
            "type": "NORMAL",
            "material": "metal2",
            "density": 50,
            "ranges": [
                {
                    "type": "BOX",
                    "dim": [70, 70, 90, 90]
                }
            ]
        }
    ],
    "material": "comp1"
}
mesh3D_obj.organize(area1)


mesh3D_obj.show_graph_2D()
        
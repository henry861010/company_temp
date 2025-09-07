from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()
mesh2D_obj.mesh_checkerboard(1,[0,100],[0,100])

mesh3D_obj = Mesh3D()
mesh3D_obj.set_2D(mesh2D_obj)

area1 = {
    "type": "BOX",
    "dim": [0,0,100,100],
    "holes": [{
        "type": "BOX",
        "dim": [0,0,40,40]
    }],
    "metals": [
        {
            "type": "NORMAL",
            "material": "metal1",
            "density": 10,
            "holes":[
                {
                    "type": "BOX",
                    "dim": [40, 40, 70, 70]
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
mesh3D_obj.drag(1,0,5)

area2 = {
    "type": "BOX",
    "dim": [0,0,100,100],
    "material": "comp2",
    "metals": [
        {
            "type": "CONTINUE",
            "material": "metal1"
        }
    ]
}
mesh3D_obj.organize(area2)
mesh3D_obj.drag(1,5,10)

area3 = {
    "type": "BOX",
    "dim": [50,50,100,100],
    "material": "comp3",
    "metals": [
        {
            "type": "CONVERT",
            "material_o": "metal1",
            "material": "metal3"
        }
    ]
}
mesh3D_obj.organize(area3)
mesh3D_obj.drag(5,10,20)


area4 = {
    "type": "POLYGON",
    "dim": [[20,60], [40,60], [40,80], [60,80], [90,10]],
    "material": "comp4"
}
mesh3D_obj.organize(area4)
area4 = {
    "type": "BOX",
    "dim": [0, 0, 100, 100],
    "material": "EMPTY",
    "holes": [{
        "type": "POLYGON",
        "dim": [[20,60], [40,60], [40,80], [60,80], [90,10]],
    }]
}
mesh3D_obj.organize(area4)
mesh3D_obj.drag(1,20,30)

### show the result
mesh3D_obj.show_info()

vision_obj = Vision()
nodes, elements, element_comps, comps = mesh3D_obj.get_byIndex()
vision_obj.set(comps, elements, element_comps, nodes)
vision_obj.show()
        
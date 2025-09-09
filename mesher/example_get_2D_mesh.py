from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()
mesh2D_obj.mesh_checkerboard(20,[0,100],[0,100])

mesh3D_obj = Mesh3D()
mesh3D_obj.set_2D(mesh2D_obj)

area1 = {
    "type": "BOX",
    "dim": [0,0,100,100],
    "holes": [{
        "type": "BOX",
        "dim": [20,20,80,80]
    }],
    "material": "comp1"
}
mesh3D_obj.organize(area1)
mesh3D_obj.drag(5,0,5)

mesh3D_obj.organize_empty()
area3_1 = {
    "type": "BOX",
    "dim": [0,20,20,80],
    "material": "comp1"
}
mesh3D_obj.organize(area3_1)
area3_1 = {
    "type": "BOX",
    "dim": [80,20,100,80],
    "material": "comp1"
}
mesh3D_obj.organize(area3_1)
mesh3D_obj.drag(5,5,10)

mesh3D_obj.organize_empty()
area3 = {
    "type": "BOX",
    "dim": [0,20,100,80],
    "material": "comp1"
}
mesh3D_obj.organize(area3)
mesh3D_obj.drag(5,10,15)

### show the result
mesh3D_obj.equivalence()

### get 2D mesh
element_2D = mesh3D_obj.get_2D_mesh()
print(len(element_2D))

### show result
mesh3D_obj.show_info()
vision_obj = Vision()
nodes, elements, element_comps, comps = mesh3D_obj.get_byIndex()
vision_obj.set(comps, elements, element_comps, nodes)
vision_obj.show()
        
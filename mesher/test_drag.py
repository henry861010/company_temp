from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()
mesh2D_obj.build_checkerboard(1,[0,100],[0,100])

mesh3D_obj = Mesh3D()
mesh3D_obj.initial(mesh2D_obj)

area1 = {
    "type": "BOX",
    "dim": [0,0,50,50],
    "material": "comp1"
}
mesh3D_obj.organize(area1)

area2 = {
    "type": "BOX",
    "dim": [70,70,90,90],
    "material": "comp2"
}
mesh3D_obj.organize(area2)

mesh3D_obj.drag(1,0,2)

### show the result
mesh3D_obj.show_info()

vision_obj = Vision()
vision_obj.set(mesh3D_obj)
vision_obj.show()
        
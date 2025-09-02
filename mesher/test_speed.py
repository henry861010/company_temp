from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh2D_obj = Mesh2D()
x = 100
y = 100
z = 50
mesh2D_obj.build_checkerboard(1,[0,x],[0,y])

mesh3D_obj = Mesh3D()
mesh3D_obj.initial(mesh2D_obj)

for i in range(z):
    area = {
        "type": "BOX",
        "dim": [0,0,x,y],
        "material": f"comp{i}"
    }
    mesh3D_obj.organize(area)
    mesh3D_obj.drag(1,10*i,10*(i+1))
    
mesh3D_obj.equivalence()

### show the result
mesh3D_obj.show_info()

vision_obj = Vision()
comps, elements, element_comps, nodes = mesh3D_obj.get()
vision_obj.set(comps, elements, element_comps, nodes)
vision_obj.show()
        
import numpy as np
from mesh2D import Mesh2D
from mesh3D import Mesh3D
from vision import Vision

mesh3D_obj = Mesh3D()

elements = [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14, 15]]
nodes = [
    [0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [1.0, 1.0, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0],
    [0.0, 1.0, 1.0],
    [1.0, 1.0, 1.0],
    [1.0, 0.0, 1.0],
    [0.0, 0.0, 1.0],
    [0.0, 1.0, 1.0],
    [1.0, 1.0, 1.0],
    [1.0, 0.0, 1.0],
    [0.0, 0.0, 2.0],
    [0.0, 1.0, 2.0],
    [1.0, 1.0, 2.0],
    [1.0, 0.0, 2.0],
]
mesh3D_obj.comps = {"comp": 1}
mesh3D_obj.element_comps = np.array([1 for _ in elements], dtype=np.int32)

mesh3D_obj.elements = np.array(elements, dtype=np.int32)
mesh3D_obj.element_num = len(elements)

mesh3D_obj.nodes = np.array(nodes, dtype=np.float32)
mesh3D_obj.node_num = len(nodes)

mesh3D_obj.equivalence()

### show the result
mesh3D_obj.show_info()
vision_obj = Vision()
comps, elements, element_comps, nodes = mesh3D_obj.get()
vision_obj.set(elements, element_comps, nodes)
vision_obj.show()
        
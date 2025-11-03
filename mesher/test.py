from region import Region
from mesh2D import Mesh2D

face_list = [
    {
        "type": "POLYGON",
        "dim":[[0,0], [0,10], [30,10], [30,5], [20,5], [20,-10], [10,-10], [10,0]]
    }
]
ref_face_list = [
    {
        "type": "POLYGON",
        "dim":[[0,0], [0, 5], [5, 5], [5, 0]]
    }
]
region_obj = Region()
region_obj.set(face_list=face_list, ref_face_list=ref_face_list)
blocks = region_obj.get_mesh_blocks_full(1, 1)

for block in blocks:
    print(block[0])
    print(block[1])
    print("")
region_obj.show_graph()
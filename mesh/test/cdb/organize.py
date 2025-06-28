from cdb import *

area = {
        "material": "comp1",
        "ranges": [
            {
                "type": "BOX",
                "dim": [2, 2, 8, 8]
            }
        ],
        "holes": [
            {
                "type": "BOX",
                "dim": [4, 4, 6, 6]
            }
        ],
        "metals": []
    }

cdb_obj = CDB()
element_size = 1
x_list = [0, 40]
y_list = [0, 40]
cdb_obj.build_block(element_size, x_list, y_list)
cdb_obj.organize(area)
cdb_obj.show_2d_graph()
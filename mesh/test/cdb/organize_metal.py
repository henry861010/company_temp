from cdb import *

area = {
        "material": "comp1",
        "ranges": [
            {
                "type": "BOX",
                "dim": [10, 10, 40, 40]
            }
        ],
        "holes": [
            {
                "type": "BOX",
                "dim": [20, 20, 30, 30]
            }
        ],
        "metals": [
            {
                "material": "metal1",
                "type": "NORMAL",
                "density": 40
            },             {
                "material": "metal2",
                "type": "NORMAL",
                "density": 10
            }
        ]
    }

cdb_obj = CDB()
element_size = 1
x_list = [0, 50]
y_list = [0, 50]
cdb_obj.build_block(element_size, x_list, y_list)
cdb_obj.cal_areas()
cdb_obj.organize(area)
cdb_obj.drag(5, 10)
cdb_obj.show_info()
cdb_obj.show_2d_graph()
cdb_obj.generate_cdb(path = 'cdb.txt')

from cdb import *

cdb_obj = CDB()
element_size = 5
x_list = [0, 25]
y_list = [0, 25]

cdb_obj.build_block(element_size, x_list, y_list)

area = {
        "material": "comp1",
        "ranges": [
            {
                "type": "BOX",
                "dim": [0, 0, 25, 25]
            }
        ],
        "holes": [
            {
                "type": "BOX",
                "dim": [5, 5, 20, 20]
            }    
        ],
        "metals": []
    }
cdb_obj.organize(area)

cdb_obj.drag(5, 10)

cdb_obj.generate_cdb(path = 'cdb.txt')
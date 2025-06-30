from cdb import *
import time
from test.test_util import *

num = 300
cdb_obj = CDB()
element_size = 1
x_list = [0, num]
y_list = [0, num]

### build the 2D mesh
start = time.time()
cdb_obj.build_block(element_size, x_list, y_list)
end = time.time()
print(f"[2D mesh] time: {end - start:.6f} seconds")
show_memory_CDB(cdb_obj)
print("")

### organize
area = {
        "material": "comp1",
        "ranges": [
            {
                "type": "BOX",
                "dim": [0, 0, num, num]
            }
        ],
        "holes": [],
        "metals": []
    }
start = time.time()
cdb_obj.organize(area)
end = time.time()
print(f"[organize] time: {end - start:.6f} seconds")
show_memory_CDB(cdb_obj)
print("")

### drag 3D
start = time.time()
cdb_obj.drag(1, num/10)
end = time.time()
print(f"[3D mesh] time: {end - start:.6f} seconds")
show_memory_CDB(cdb_obj)
print("")

###
start = time.time()
cdb_obj.generate_cdb(path = 'cdb.txt')
end = time.time()
print(f"[generate CDB] time: {end - start:.6f} seconds")
show_memory_CDB(cdb_obj)
print("")


print("")
print("")
cdb_obj.show_info()
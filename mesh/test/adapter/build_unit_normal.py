from cdb import *
from adapter import *

cdb = CDB()
#edge1 = [[0, 0], [0 ,2], [0 ,4], [0 ,6], [0 ,8], [0 ,10]]
#edge2 = [[0, 10], [10 ,10]]
#edge3 = [[10, 0], [10 ,10]]
#edge4 = [[0, 0], [10 ,0]]

#edge1 = [[0,0], [0,10]]
#edge2 = [[0,10], [2,10], [4,10], [6,10], [8,10], [10,10]]
#edge3 = [[10,0], [10,10]]
#edge4 = [[0,0], [10,0]]

#edge1 = [[0,0], [0,10]]
#edge2 = [[0,10], [10,10]]
#edge3 = [[10,0], [10,2], [10,4], [10,6], [10,8], [10,10]]
#edge4 = [[0,0],[10,0]]

edge1 = [[0,0], [0,10]]
edge2 = [[0,10], [10,10]]
edge3 = [[10,0], [10,10]]
edge4 = [[0,0], [2,0], [4,0], [6,0], [8,0], [10,0]]

build_unit_normal(cdb, edge1, edge2, edge3, edge4)
cdb.show_graph()
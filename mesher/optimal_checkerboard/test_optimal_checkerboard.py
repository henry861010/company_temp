import numpy as np
from optimal_checkerboard import cluster_parallel_lines_dict, cluster_parallel_lines_dict,_is_dependent

# dict of bands keyed by avg-x (vertical) or avg-y (horizontal)
p1 = [[0,0], [0,10]]
p2 = [[1,0], [1,10]]
p3 = [[10,0], [10,10]]
p4 = [[20,0], [20,10]]
pattern_list = [p1, p2, p3, p4]
bands = cluster_parallel_lines_dict(pattern_list, is_vertical=True,
                                    criteria_dis=2, criteria_angle=2.0,
                                    key_round=6, return_dict=True)
for b, lines in bands.items():
    print(b)
    for line in lines:
        print(f"  {line}")
        

line1 = np.array([[[0,0],[0,10]],])
line2 = np.array([[10,0],[10,10]])
criteria_dis = 5
criteria_angle = 2
res = _is_dependent(line1, line2, criteria_dis, criteria_angle)
print(res)
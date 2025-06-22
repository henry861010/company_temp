import numpy as np
import time
import random
import resource
from tool import *

rows = 10000000
cols = 4
arr = [[random.random() for _ in range(cols)] for _ in range(rows)]
evaluate_memory()

sub_arr = []
start_time = time.time()
for element in arr:
    if element[0] < 0.5:
        sub_arr.append(0)
    else:
        continue
    if element[1] < 0.5:
        sub_arr.append(0)
    else:
        continue
    if element[2] < 0.5:
        sub_arr.append(0)
    else:
        continue
    if element[3] < 0.5:
        sub_arr.append(0)
    else:
        continue
end_time = time.time()
elapsed = end_time - start_time
print(f"Elapsed time: {elapsed:.8f} seconds")

evaluate_memory()
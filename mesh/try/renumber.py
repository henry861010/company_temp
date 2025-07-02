import numpy as np
import time
from test.test_util import *


### got [1 2 3 0 4 5 0 6]
#arr = np.array([12, 4, 5, 0, 9, 4, 0, 9])

### got [1 2 0 3 0 4 0 0 5 0 6 7 0 8]
#arr = np.array([12, 4, 0, 100, 0, 80, 0 ,0, 5, 0, 9, 4, 0, 9])

arr = np.random.rand(10000000)
print(len(arr))
start = time.time()

show_memory_CDB()

table = np.zeros_like(arr)

# Get indices where arr != 0
nonzero_indices = np.nonzero(arr)[0]

# Assign sequential IDs starting from 1 to non-zero elements
table[nonzero_indices] = np.arange(1, len(nonzero_indices) + 1)

end = time.time()
print(f"[2D mesh] time: {end - start:.6f} seconds")
print(len(table))
show_memory_CDB()
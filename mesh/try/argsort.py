import numpy as np
import time
from test.test_util import *

arr = np.random.rand(10000000)
start = time.time()
sorted_indices = np.argsort(arr)
end = time.time()
print(f"[2D mesh] time: {end - start:.6f} seconds")
show_memory_CDB()
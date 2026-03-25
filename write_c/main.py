import numpy as np
import fastio

nodes = np.random.rand(1000, 3).astype(np.float64)
elements = np.random.randint(0, 1000, (500, 8)).astype(np.int64)

filename = "mesh.txt"

# 1. Write nodes first (use "w" to create/overwrite)
fastio.write_nodes(filename, "w", nodes)

# 2. Append elements to the same file (use "a" to append)
fastio.write_elements(filename, "a", elements, 101, 202, 303)
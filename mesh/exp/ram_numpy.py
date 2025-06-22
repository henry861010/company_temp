from tool import *
import numpy as np

boxes = np.random.rand(10000000, 4) * 100  # random boxes in a 100x100 space
evaluate_memory()
from tool import *
import random

rows = 10000000
cols = 4
arr = [[random.random() for _ in range(cols)] for _ in range(rows)]
evaluate_memory()
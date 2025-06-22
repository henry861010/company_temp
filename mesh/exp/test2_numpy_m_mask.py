import numpy as np
import time
import random
import resource
from tool import *

# Example box data: shape (10000, 4)
boxes = np.random.rand(10000000, 15) * 100  # random boxes in a 100x100 space
evaluate_memory()

# Ensure left_x <= right_x and bottom_y <= top_y
boxes[:, 2] = boxes[:, 0] + np.abs(boxes[:, 2] - boxes[:, 0])
boxes[:, 3] = boxes[:, 1] + np.abs(boxes[:, 3] - boxes[:, 1])

# Define the range to filter
f1_1 = 0
f1_2 = 0
f1_3 = 10
f1_4 = 10

f2_1 = 0
f2_2 = 0
f2_3 = 5
f2_4 = 5

f3_1 = 0
f3_2 = 0
f3_3 = 3
f3_4 = 3

start_time = time.time()

# Apply the condition: box is completely within the given range
mask1 = (
    (boxes[:, 0] >= f1_1) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= f1_2) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= f1_3) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= f1_4)  # top_y of box ≤ range top_y
)

mask2 = (
    (boxes[:, 0] >= f2_1) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= f2_2) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= f2_3) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= f2_4)  # top_y of box ≤ range top_y
)

mask3 = (
    (boxes[:, 0] >= f3_1) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= f3_2) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= f3_3) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= f3_4)  # top_y of box ≤ range top_y
)

# Get the filtered boxes
filtered_boxes = boxes[mask1 & mask2 & mask3]

end_time = time.time()
elapsed = end_time - start_time
print(f"Elapsed time: {elapsed:.8f} seconds")

evaluate_memory()
import numpy as np
import time
import random
import resource
from tool import *

# Example box data: shape (10000, 4)
boxes = np.random.rand(10000000, 4) * 100  # random boxes in a 100x100 space
evaluate_memory()

# Ensure left_x <= right_x and bottom_y <= top_y
boxes[:, 2] = boxes[:, 0] + np.abs(boxes[:, 2] - boxes[:, 0])
boxes[:, 3] = boxes[:, 1] + np.abs(boxes[:, 3] - boxes[:, 1])

# Define the range to filter
filter_left_x = 10
filter_bottom_y = 20
filter_right_x = 60
filter_top_y = 80

start_time = time.time()

# Apply the condition: box is completely within the given range
mask1 = (
    (boxes[:, 0] >= filter_left_x) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= filter_bottom_y) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= filter_right_x) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= filter_top_y)  # top_y of box ≤ range top_y
)
mask2 = (
    (boxes[:, 0] >= filter_left_x) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= filter_bottom_y) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= filter_right_x) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= filter_top_y)  # top_y of box ≤ range top_y
)
mask3 = (
    (boxes[:, 0] >= filter_left_x) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= filter_bottom_y) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= filter_right_x) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= filter_top_y)  # top_y of box ≤ range top_y
)
mask4 = (
    (boxes[:, 0] >= filter_left_x) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= filter_bottom_y) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= filter_right_x) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= filter_top_y)  # top_y of box ≤ range top_y
)
mask5 = (
    (boxes[:, 0] >= filter_left_x) &  # left_x of box ≥ range left_x
    (boxes[:, 1] >= filter_bottom_y) &  # bottom_y of box ≥ range bottom_y
    (boxes[:, 2] <= filter_right_x) &  # right_x of box ≤ range right_x
    (boxes[:, 3] <= filter_top_y)  # top_y of box ≤ range top_y
)

# Get the filtered boxes
filtered_boxes = boxes[mask1 & mask2 & mask3 & mask4 & mask5]

end_time = time.time()
elapsed = end_time - start_time
print(f"Elapsed time: {elapsed:.8f} seconds")

evaluate_memory()
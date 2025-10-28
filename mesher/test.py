from checkerboard import _checkerboard_cylinder
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle

element_size = 5
dim = [0, 0, 21]
x_list = [i for i in range(-dim[2], dim[2]+1)]
y_list = [i for i in range(-dim[2], dim[2]+1)]

nodes, elements = _checkerboard_cylinder(element_size, dim, x_list, y_list)

### show mesh graph
coords = nodes[:len(nodes)][elements[:len(elements)]]
fig, ax = plt.subplots()
pc = PolyCollection(
    coords[:, :, :2], closed=True,
    facecolors='blue', edgecolors='black', linewidths=1,
)
ax.add_collection(pc)
circle = Circle((dim[0], dim[1]), dim[2], fill=False, linewidth=2)
ax.add_patch(circle)
ax.plot([dim[0]], [dim[1]], marker='o')
ax.set_aspect('equal', adjustable='box')
ax.autoscale()
plt.show()
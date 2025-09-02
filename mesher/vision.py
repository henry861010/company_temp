# https://pyvista.org/projects/index.html

import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

class Vision:
    def __init__(self):
        ### 3D elements
        self.elements = np.empty((0, 8), dtype=np.int32)
        self.element_comps = np.empty((0), dtype=np.int32)
        self.nodes = np.empty((0, 3), dtype=np.float32)
    
    def set(self, elements, element_comps, nodes):
        self.elements = elements
        self.element_comps = element_comps
        self.nodes = nodes
        
    def show(self):
        ### Build the cell
        n = self.elements.shape[0]
        cells = np.hstack([np.column_stack([np.full((n,1), 8, dtype=self.elements.dtype), self.elements]).ravel()])
        
        ### Cell types
        celltypes = np.full(n, pv.CellType.HEXAHEDRON, dtype=np.uint8)
        
        ### Create grid
        grid = pv.UnstructuredGrid(cells, celltypes, self.nodes)
        
        ### Attach component ids as cell data for coloring
        grid.cell_data['comp'] = self.element_comps.astype(np.int32)
        
        ### colors
        if 'comp' in grid.point_data and 'comp' not in grid.cell_data:
            grid = grid.point_data_to_cell_data(pass_point_data=False)
        comp = grid.cell_data['comp'].astype(int)
        vals, counts = np.unique(comp, return_counts=True)
        base = plt.get_cmap('tab20')           # a ListedColormap
        palette = [to_hex(c) for c in base.colors]   # ['#1f77b4', '#ff7f0e', ...]
        colors  = palette[:len(vals)]          # as many as you need
        
        ### Plot
        plotter = pv.Plotter()
        plotter.add_mesh(
            grid,
            scalars='comp',
            categories=True,
            preference='cell',
            cmap=colors,               # <-- hex strings OK
            show_edges=True,
            smooth_shading=False,
            annotations={int(v): f"{int(v)}" for v in vals},
            show_scalar_bar=False
        )
        
        legend = [[f"comp {v}: {int(c)} elems", colors[i]] for i, (v, c) in enumerate(zip(vals, counts))]
        legend = [[f"Node Num: {len(self.nodes)}", "black"]] + legend
        legend = [[f"Elem Num: {len(self.elements)}", "black"]] + legend
        
        plotter.add_legend(legend, loc='upper left', bcolor='white', border=True) 
        plotter.add_axes()
        plotter.show()

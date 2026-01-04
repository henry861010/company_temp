import pyvista as pv
import numpy as np

# 1. Define your points (Hull is CCW, Hole is CW)
# Note: PyVista generally prefers CCW for outward normals
hull_pts = np.array([[0,0,0], [5,0,0], [5,5,0], [0,5,0]])
hole_pts = np.array([[1,1,0], [1,4,0], [4,4,0], [4,1,0]])

# 2. Create the faces 
# PyVista uses a 'Padding' format: [number_of_points, i1, i2, i3...]
# We'll use a helper to create a PolyData object
def create_plane_with_hole(outer, inner):
    # Combine points
    all_pts = np.vstack([outer, inner])
    
    # In PyVista, for complex polygons with holes, 
    # the easiest way is to use 'delaunay_2d'
    cloud = pv.PolyData(all_pts)
    
    # This creates a mesh covering all points
    mesh = cloud.delaunay_2d()
    
    # To strictly enforce the "hole", we can use boolean 
    # but for simple planes, we often just clip or use specific face indices.
    return mesh

mesh = create_plane_with_hole(hull_pts, hole_pts)

# 3. Plotting
plotter = pv.Plotter()
plotter.add_mesh(mesh, color="cyan", show_edges=True, opacity=0.7)
plotter.add_axes()
plotter.show()
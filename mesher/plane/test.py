from mesh_polygons import Polygon, _get_edge_key, _det_edge_count

# 1. Define Vertices of a simple Cube (1x1x1)
v = [
    (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),  # Bottom 4
    (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)   # Top 4
]

# 2. Define the 6 faces (Planes) of the Cube using vertex indices
cube_faces = [
    Polygon([v[0], v[1], v[2], v[3]]),  # Bottom
    Polygon([v[4], v[5], v[6], v[7]]),  # Top
    Polygon([v[0], v[1], v[5], v[4]]),  # Front
    Polygon([v[1], v[2], v[6], v[5]]),  # Right
    Polygon([v[2], v[3], v[7], v[6]]),  # Back
    Polygon([v[3], v[0], v[4], v[7]])   # Left
]

# 3. Scenario A: Basic solve (No fixed edges)
# The algorithm should default all edges to 1 segment because 1+1+1+1=4 (even)
result_basic = _det_edge_count(cube_faces)

print("--- Scenario A: No Fixed Edges ---")
print(f"Total Unique Edges: {len(result_basic['edge_coords'])}")
print(f"Segment Counts: {result_basic['segment_counts']}")
# All values will likely be 1.

# 4. Scenario B: Force an Odd Edge
# Let's force the first edge (Bottom-Front) to have 3 segments.
# This makes the Bottom Face and Front Face "Odd" (1+1+1+3 = 6, still even... 
# wait, actually let's force an edge to 2 to see the parity change!)
# Better yet: Force an edge to 3, and see if others adjust to stay even.
fixed = {}
fixed[_get_edge_key(v[0], v[1])] = 3

result_fixed = _det_edge_count(cube_faces, fixed_segments=fixed)

print("\n--- Scenario B: Edge (0,0,0)-(1,0,0) Fixed at 3 ---")
for i, count in enumerate(result_fixed['segment_counts']):
    edge = result_fixed['edge_coords'][i]
    print(f"Edge {edge}: {count} segments")

# 5. VALIDATION: Check if every plane is even
print("\n--- Validation Check ---")
for p_idx, e_indices in enumerate(result_fixed['plane_to_edges']):
    total_segments = sum(result_fixed['segment_counts'][e_idx] for e_idx in e_indices)
    is_even = total_segments % 2 == 0
    print(f"Plane {p_idx}: Total Segments = {total_segments} (Even: {is_even})")
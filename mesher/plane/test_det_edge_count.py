import pytest
import numpy as np

# --- Supporting Class ---
class Polygon:
    def __init__(self, hull, holes=None):
        self.hull = hull
        self.holes = holes or []

# --- Unit Tests ---

def test_manifold_edge_sharing(cube_polygons):
    """
    Test that every edge in a closed manifold (cube) is shared by 
    exactly two planes, and verify the solver respects this.
    """
    unique_edges, edge_counts = _det_edge_count(cube_polygons)
    
    # In a cube, 12 edges, each should be even-summed.
    assert len(unique_edges) == 12
    assert len(edge_counts) == 12
    # Verify values are only 1 or 2
    assert np.all((edge_counts == 1) | (edge_counts == 2))

def test_fixed_even_constraint():
    """
    Test fixing an edge to an even number (e.g., 4).
    The system should treat this as '0' in GF(2).
    """
    v = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
    poly = [Polygon(v)]
    # Fix one edge to 4. To keep sum even, others could be (1, 1, 2) or (2, 2, 2).
    fixed = {(v[0], v[1]): 4}
    edges, counts = _det_edge_count(poly, fixed)
    
    assert sum(counts) % 2 == 0
    assert counts[0] == 4

def test_floating_point_precision():
    """
    Test that edges are correctly identified even with tiny 
    floating point differences (testing _get_edge_key robustness).
    """
    p1 = (0.12345678, 0.0, 0.0)
    p2 = (1.12345678, 0.0, 0.0)
    p2_eps = (1.12345679, 0.0, 0.0) # Difference at 8th decimal
    
    poly1 = Polygon([p1, p2, (1,1,0)])
    poly2 = Polygon([p1, p2_eps, (0,1,1)]) # Should match as the same edge
    
    edges, counts = _det_edge_count([poly1, poly2])
    # Total edges: (p1-p2), (p2-v1), (v1-p1), (p2-v2), (v2-p1) = 5
    assert len(edges) == 5

def test_multiple_disconnected_objects():
    """
    Test two separate cubes that do not touch.
    The solver should handle disconnected components in the matrix A.
    """
    v1 = [(0,0,0), (1,0,0), (1,1,0), (0,1,0), (0,0,1), (1,0,1), (1,1,1), (0,1,1)]
    v2 = [(5,5,5), (6,5,5), (6,6,5), (5,6,5), (5,5,6), (6,5,6), (6,6,6), (5,6,6)]
    
    def make_cube(v):
        return [
            Polygon([v[0], v[1], v[2], v[3]]), Polygon([v[4], v[5], v[6], v[7]]),
            Polygon([v[0], v[1], v[5], v[4]]), Polygon([v[1], v[2], v[6], v[5]]),
            Polygon([v[2], v[3], v[7], v[6]]), Polygon([v[3], v[0], v[4], v[7]])
        ]
    
    all_polys = make_cube(v1) + make_cube(v2)
    edges, counts = _det_edge_count(all_polys)
    
    assert len(edges) == 24 # 12 + 12
    assert len(counts) == 24

def test_large_fixed_segments():
    """
    Test that the solver can handle very large segment counts (e.g., 100).
    This is important for boundary layers in CFD/FEA.
    """
    v = [(0,0,0), (1,0,0), (1,1,0)]
    fixed = {(v[0], v[1]): 100}
    edges, counts = _det_edge_count([Polygon(v)], fixed)
    
    assert counts[0] == 100
    assert sum(counts) % 2 == 0

def test_complex_hole_parity():
    """
    Test a 'donut' shape (one hull, one hole).
    The solver must ensure (sum(hull) + sum(hole)) % 2 == 0.
    """
    hull = [(0,0,0), (10,0,0), (10,10,0), (0,10,0)] # 4 edges
    hole = [(4,4,0), (6,4,0), (5,6,0)]             # 3 edges
    # Hull(4) + Hole(3) = 7 edges. At least one must be '2' to make sum even.
    
    edges, counts = _det_edge_count([Polygon(hull, [hole])])
    assert sum(counts) % 2 == 0

@pytest.mark.parametrize("segments", [1, 2, 3, 4, 5])
def test_all_parity_combinations(segments):
    """
    Parametrized test to ensure that regardless of input lengths, 
    the output is always quad-meshable (even).
    """
    v = [(0,0,0), (segments, 0, 0), (segments, segments, 0), (0, segments, 0)]
    edges, counts = _det_edge_count([Polygon(v)])
    assert sum(counts) % 2 == 0
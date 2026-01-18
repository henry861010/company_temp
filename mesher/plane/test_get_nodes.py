import pytest
import numpy as np

# We assume _get_nodes is imported or in the same file
@pytest.mark.parametrize("p1, p2, size, node_type, expected_node_count", [
    # Case 1: Dist 10, Size 2.0 -> 5 segs. Type 1 (Odd nodes) needs EVEN segs -> 6 segs = 7 nodes
    ([0,0,0], [10,0,0], 2.0, 1, 7),
    
    # Case 2: Dist 10, Size 2.0 -> 5 segs. Type 2 (Even nodes) needs ODD segs -> 5 segs = 6 nodes
    ([0,0,0], [10,0,0], 2.0, 2, 6),
    
    # Case 3: Dist 10, Size 3.0 -> 3 segs. Type 1 (Odd nodes) needs EVEN segs -> 4 segs = 5 nodes
    ([0,0,0], [10,0,0], 3.0, 1, 5),
    
    # Case 4: Coincident points should return 1 node
    ([1,1,1], [1,1,1], 1.0, 1, 1),
    
    # Case 5: Very large element size (minimum segments is 1)
    ([0,0,0], [1,0,0], 100.0, 2, 2), # Type 2 -> 1 seg = 2 nodes
])
def test_node_counts(p1, p2, size, node_type, expected_node_count):
    nodes = _get_nodes(p1, p2, size, node_type)
    assert len(nodes) == expected_node_count
    
    # Parity Check
    if node_type == 1:
        assert len(nodes) % 2 != 0  # Total nodes must be ODD
    else:
        assert len(nodes) % 2 == 0  # Total nodes must be EVEN

def test_endpoints():
    p1 = np.array([0, 0, 0])
    p2 = np.array([5, 5, 5])
    nodes = _get_nodes(p1, p2, 1.0, 1)
    
    # Ensure start and end match exactly
    np.testing.assert_array_almost_equal(nodes[0], p1)
    np.testing.assert_array_almost_equal(nodes[-1], p2)

def test_vector_direction():
    p1 = [0, 0, 0]
    p2 = [0, 0, 10]
    nodes = _get_nodes(p1, p2, 2.0, 1)
    
    # Ensure all nodes have x=0 and y=0
    assert np.all(nodes[:, 0] == 0)
    assert np.all(nodes[:, 1] == 0)
    # Ensure z is increasing
    assert np.all(np.diff(nodes[:, 2]) > 0)
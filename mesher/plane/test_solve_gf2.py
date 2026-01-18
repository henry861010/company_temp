import pytest
import numpy as np

'''
To test a GF(2) solver, we need to verify that it handles standard linear systems, 
under-determined systems (multiple solutions), and inconsistent systems (though in a 
manifold mesh, a solution should always exist).
'''

@pytest.mark.parametrize("A, b, expected_x", [
    # Case 1: Identity matrix (1x + 0y = 1, 0x + 1y = 0)
    ([[1, 0], [0, 1]], [1, 0], [1, 0]),
    
    # Case 2: Simple XOR (x + y = 0) -> One valid solution is [1, 1]
    # In GF(2), 1 + 1 = 0
    ([[1, 1]], [0], [1, 1]),
    
    # Case 3: Dependency (x + y = 1, y = 1) -> x must be 0
    ([[1, 1], [0, 1]], [1, 1], [0, 1]),
    
    # Case 4: A "Triangle" of planes (Closed loop)
    # Plane 1: e1 + e2 = 0
    # Plane 2: e2 + e3 = 0
    # Plane 3: e1 + e3 = 0
    # Solution [0, 0, 0] is valid
    ([[1, 1, 0], [0, 1, 1], [1, 0, 1]], [0, 0, 0], [0, 0, 0]),
])
def test_gf2_solutions(A, b, expected_x):
    A_np = np.array(A)
    b_np = np.array(b)
    x = _solve_gf2(A_np, b_np)
    
    assert x is not None
    # Verify Ax % 2 == b
    result = np.dot(A_np, x) % 2
    np.testing.assert_array_equal(result, b_np)

def test_gf2_inconsistent():
    # System: x = 1 AND x = 0 (Impossible)
    A = np.array([[1], [1]])
    b = np.array([1, 0])
    x = _solve_gf2(A, b)
    assert x is None

def test_gf2_underdetermined():
    # x + y + z = 1
    # Many solutions exist; solver should return one that works.
    A = np.array([[1, 1, 1]])
    b = np.array([1])
    x = _solve_gf2(A, b)
    assert x is not None
    assert (np.dot(A, x) % 2) == b[0]
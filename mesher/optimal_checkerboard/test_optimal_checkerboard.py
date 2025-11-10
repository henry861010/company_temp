import math
import pytest

from optimal_checkerboard import _min_list   # replace 'your_module' with the actual filename (without .py)

def test_min_list_basic():
    v0, v1, dist = 0, 10, 5
    result = _min_list(v0, v1, dist, angle=45)

    # expected calculation
    angle_radians = math.pi * ((90 - 45) / 180)
    l = math.tan(angle_radians) * dist
    expected = (min(v0, v1) - l, max(v0, v1) + l)

    assert math.isclose(result[0], expected[0], rel_tol=1e-9)
    assert math.isclose(result[1], expected[1], rel_tol=1e-9)


@pytest.mark.parametrize(
    "v0,v1,dist,angle",
    [
        (0, 10, 0, 45),   # zero distance → no extension
        (5, 5, 10, 0),    # zero angle → large tangent
        (-10, 10, 5, 60), # symmetric case
        (3, 7, 2, 30),    # arbitrary
    ],
)
def test_min_list_various(v0, v1, dist, angle):
    result = _min_list(v0, v1, dist, angle)
    angle_radians = math.pi * ((90 - angle) / 180)
    l = math.tan(angle_radians) * dist
    expected = (min(v0, v1) - l, max(v0, v1) + l)

    assert math.isclose(result[0], expected[0], rel_tol=1e-9)
    assert math.isclose(result[1], expected[1], rel_tol=1e-9)

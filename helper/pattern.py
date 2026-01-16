# Copyright 2026 M. Alperen Sener (m.alperensener@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import cadquery as cq
import math


def get_height(obj: cq.Workplane, plane_name: str) -> float:
    """
    Returns the height of an object normal to the specified plane.

    :param obj: The CadQuery Workplane/Object
    :param plane_name: String name of the plane ('XY', 'XZ', or 'YZ')
    :return: Float representing the dimension (thickness) normal to the plane
    """
    # 1. Map the plane to the normal axis dimension name
    plane_map = {
        "XY": "zlen",
        "XZ": "ylen",
        "YZ": "xlen"
    }

    axis_attr = plane_map.get(plane_name.upper())

    if not axis_attr:
        raise ValueError("plane_name must be 'XY', 'XZ', or 'YZ'")

    bbox = obj.combine().val().BoundingBox()

    dimension = getattr(bbox, axis_attr)

    return dimension


def get_plane_name(plane):
    mapping = {
        (0, 0, 1): "XY",
        (0, 0, -1): "XY",
        (0, -1, 0): "XZ",
        (0, 1, 0): "XZ",
        (1, 0, 0): "YZ",
        (-1, 0, 0): "YZ"
    }

    z_tuple = (int(plane.zDir.x), int(plane.zDir.y), int(plane.zDir.z))
    return mapping.get(z_tuple)


def create_pattern(object: cq.Workplane, x_lim, y_lim,
                         x_space, y_space, odd_row_shift=True) -> cq.Workplane:
    """
    Generate distribution points within x and y limits, with w and h spaces.

    :param object: The CadQuery Workplane/Object that will be populated.
    :param x_lim: Dimention limit in x direction
    :param y_lim: Dimention limit in y direction
    :param x_space: Spacing in x
    :param y_space: Spacing in y
    """
    raw_points = []
    # intentinally going just out of limit.
    cols = int(-(-x_lim // x_space))
    rows = int(-(-y_lim // y_space))
    
    for col in range(cols):
        for row in range(rows):
            x_pos = col * x_space
            y_pos = row * y_space
            # some objects might need bi-row shifting
            if col % 2 == 1 and odd_row_shift:
                y_pos += y_space / 2
            raw_points.append((x_pos, y_pos))
            
    # Re-adjust each node around the geometric (approximated center of mass) center
    avg_x = sum(p[0] for p in raw_points) / len(raw_points)
    avg_y = sum(p[1] for p in raw_points) / len(raw_points)
    centered_points = [(p[0] - avg_x, p[1] - avg_y) for p in raw_points]

    cut_frame = (
        cq.Workplane(get_plane_name(object.plane))
        .box(x_lim, y_lim, 2 * get_height(object, get_plane_name(object.plane)))
    )

    x, y = centered_points[0]
    result = object.translate((x, y, 0))
    for x, y in centered_points[1:]:
        result = result.union(object.translate((x, y, 0)))

    result = cut_frame.intersect(result)

    return result


def honeycomb(size: tuple, radius, depth, distance,
              rotation: tuple = (0, 0, 0), translation: tuple = (0, 0, 0)) -> cq.Workplane:
    """
    Geneartes honeycomb pattern on XY plane cut out by size.

    :param size: limits in X and Y directions
    :type size: tuple
    :param radius: radius of the hexagons, radius will be reduced by the half of distance
    :param depth: thickness of the patern
    :param distance: distance between hexagons
    :param rotation: rotation parameter
    :type rotation: tuple vector0 vector1 degree
    :param translation: translation parameter
    :type translation: tuple x y z
    """
    
    x_limit, y_limit = size
    
    # spacing in both width and height for hexagons in honeycomb
    w = 1.5 * radius
    h = math.sqrt(3) * radius
    
    # resize the radius of the hexagons to have 'distance' in between
    dist_to_flat = (radius * math.sqrt(3)/2) - (distance / 2)
    actual_r = dist_to_flat / (math.sqrt(3)/2)

    result = (
        cq.Workplane('XY')
        .polygon(6, 2 * actual_r)
        .rotate((0, 0, 0), (0, 0, 1), 90)
        .extrude(depth)
    )

    result = create_pattern(result, x_limit, y_limit, w, h, odd_row_shift=True)
    
    v1, v2, degree = rotation
    result = result.rotate(v1, v2, degree)
    result = result.translate(translation)

    return result

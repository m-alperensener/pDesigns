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



def create_pattern(object: cq.Workplane, size: tuple, depth, x_space, y_space,
                   odd_row_shift=True, invert=False) -> cq.Workplane:
    """
    Generate distribution points within x and y limits, with w and h spaces.

    :param object: The CadQuery Workplane/Object that will be populated.
    :param x_lim: Dimention limit in x direction
    :param y_lim: Dimention limit in y direction
    :param depth: Depth of the object
    :param x_space: Spacing in x
    :param y_space: Spacing in y
    """
    x_lim, y_lim = size

    raw_points = []
    # intentinally going just out of limit.
    cols = int(x_lim // x_space) + 2
    rows = int(y_lim // y_space) + 2

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
        cq.Workplane('XY')
        .box(x_lim, y_lim, depth * 2)
    )

    result = (
        cq.Workplane('XY')
        .pushPoints(centered_points)
        .eachpoint(lambda loc: object.val().located(loc), combine=True)
    )

    if invert:
        result = cut_frame.cut(result)
    else:
        result = cut_frame.intersect(result)

    return result


def honeycomb(size: tuple, radius, depth, distance, rotation: tuple, translation: tuple,
              invert: bool) -> cq.Workplane:
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

    # resize the radius of the hexagons to have 'distance' in between
    dist_to_flat = (radius * math.sqrt(3)/2) - (distance / 2)
    actual_r = dist_to_flat / (math.sqrt(3)/2)

    result = (
        cq.Workplane('XY')
        .polygon(6, 2 * actual_r)
        .rotate((0, 0, 0), (0, 0, 1), 90)
        .extrude(depth)
    )

    # spacing in both width and height for hexagons in honeycomb
    x = 1.5 * radius
    y = math.sqrt(3) * radius
    result = create_pattern(result, size, depth, x, y, odd_row_shift=True, invert=invert)
    
    v1, v2, degree = rotation
    result = result.rotate(v1, v2, degree)
    result = result.translate(translation)
    return result


def diamond(size: tuple, radius, depth, distance, rotation: tuple, translation: tuple,
            invert: bool) -> cq.Workplane:
    """
    Created diamond pattern on XY plane cut out by size.

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

    disk = (
        cq.Workplane('XY')
        .circle(radius)
        .extrude(depth)
    )

    cdisk = (
        cq.Workplane('XY')
        .circle(radius - distance)
        .extrude(depth)
    )

    points = [
        (radius, radius, 0),
        (-radius, radius, 0),
        (-radius, -radius, 0),
        (radius, -radius, 0)
    ]

    disks = disk.translate(points[0])
    for point in points[1:]:
        disks = disks.union(disk.translate(point))

    disk = cdisk.cut(disks)

    # spacing in both width and height for hexagons in honeycomb
    x = radius - distance
    y = 2 * (radius - distance)
    result = create_pattern(disk, size, depth, x, y, odd_row_shift=True, invert=invert)

    v1, v2, degree = rotation
    result = result.rotate(v1, v2, degree)
    result = result.translate(translation)

    return result


def star(size: tuple, radius, depth, distance, rotation: tuple, translation: tuple,
         invert: bool) -> cq.Workplane:
    outer_radius = radius
    inner_radius = radius * 0.4
    points = []
    for i in range(10):
        # Alternate between outer and inner radius
        r = outer_radius if i % 2 == 0 else inner_radius
        angle = math.radians(i * 36)

        x = r * math.cos(angle)
        y = r * math.sin(angle)
        points.append((x, y))

    # Close the loop by adding the first point at the end
    points.append(points[0])

    star = (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(depth)
        .rotate((0, 0, 0), (0, 0, 1), 18)
    )

    x = 2 * radius + distance
    y = 2 * radius + distance
    result = create_pattern(star, size, depth, x, y, odd_row_shift=False, invert=invert)

    result = result.rotate(rotation[0], rotation[1], rotation[2])
    result = result.translate(translation)

    return result


def plus(size: tuple, radius, depth, distance, rotation: tuple, translation: tuple,
         invert: bool) -> cq.Workplane:

    legth = 2 * radius

    H = cq.Workplane("XY").slot2D(legth, legth / 4, angle=90)
    V = cq.Workplane("XY").slot2D(legth, legth / 4)
    plus = V.extrude(depth).union(H.extrude(depth))
    # plus = plus.edges(">Z").fillet(depth / 2)

    x = radius + radius / 4 + distance
    y = 2 * radius + distance
    result = create_pattern(plus, size, depth, x, y, odd_row_shift=True, invert=invert)

    return result.rotate(rotation[0], rotation[1], rotation[2]).translate(translation)


def slot(size: tuple, radius, depth, distance, rotation: tuple, translation: tuple,
         invert: bool) -> cq.Workplane:
    length = 2 * radius
    slot = cq.Workplane("XY").slot2D(length, length / 4, angle=90).extrude(depth)

    x = length / 4 + distance
    y = 2 * radius + distance
    result = create_pattern(slot, size, depth, x, y, odd_row_shift=True, invert=invert)

    return result.rotate(rotation[0], rotation[1], rotation[2]).translate(translation)


def square(size: tuple, radius, depth, distance, rotation: tuple, translation: tuple,
           invert: bool)-> cq.Workplane:

    length = 2 * radius

    square = (
        cq.Workplane("XY")
        .box(length, length, depth)
        .rotate((0, 0, 0), (0, 0, 1), 45)
        .translate((0, 0, depth / 2))
    )

    x = (math.sqrt(2) * length) / 2 + distance
    y = math.sqrt(2) * length + distance

    result = create_pattern(square, size, depth, x, y, odd_row_shift=True, invert=invert)

    return result.rotate(rotation[0], rotation[1], rotation[2]).translate(translation)


def generate_pattern(type: str, size: tuple, radius, depth, distance,
              rotation: tuple, translation: tuple, invert: bool) -> cq.Workplane:
    if type == 'honeycomb':
        return honeycomb(size, radius, depth, distance, rotation, translation, invert)
    elif type == 'diamond':
        return diamond(size, radius, depth, distance, rotation, translation, invert)
    elif type == 'star':# resize the radius of the hexagons to have 
        return star(size, radius, depth, distance, rotation, translation, invert)
    elif type == 'plus':
        return plus(size, radius, depth, distance, rotation, translation, invert)
    elif type == 'slot':
        return slot(size, radius, depth, distance, rotation, translation, invert)
    elif type == 'square':
        return square(size, radius, depth, distance, rotation, translation, invert)
    else:
        raise ValueError("Invalid pattern type")

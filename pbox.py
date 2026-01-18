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

import os
import sys
import json
import logging
import cadquery as cq
from pathvalidate import sanitize_filename

# _________________ BOX PARAMETERS ________________

"""
    All dimentions are in mm
    Please modify only the following dimentions, all other parameteres are only tested in
    print so be cautious if you play with them.
    
    Well please use values that make sense, I have put no value check :D
"""
height = 30 # in z
width = 60 # in x
length = 30 # in y
wall_thickness = 1.2 # adjustend box wall will be 2 times of this value

# following sizes are to define how many cells we want to have in both size
# keep in mind that the resulting box size will be deepending on unit width
# and length. Nxwidth, Mxlength
N = 1
M = 3

 # overall thickness of the lid. This value is also used to calculate the
 # assembly holes for the lid.
lid_thickness = 2
lid_handle_length = 10
lid_handle_height = 4
lid_handle_width = 3
lid_margin_top = 1.8 # Distance of the lid from top, also used for the latch
lid_margin_sides = 0.2 # Distance of the lid from internal walls of the box

# Text paramaters and text list
font_name = 'DejaVu Sans' # System font name
font_kind = 'bold' # Set to None if innvalid
font_size = 6.4
font_height = 0.8
engraved = False
vertical_text = False

text_list = [ '#1\npBox', '#2\npBox', '#3\npBox']

# exported file extention
file_format = '.stl'

#_________ Be careful changing following ____________

# internal clearens and margins
# those values are chosen with trial according to 3D printer presision and quality
latch_width = 6
latch_pitch = 0.8
lid_support_size = 6 # height and extrude size
lid_support_pitch = 1.2

#_____________________ WORKFLOW _____________________

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    force=True
)

file_path = None
if len(sys.argv) > 1:
    file_path = sys.argv[1]

if file_path is not None and os.path.exists(file_path):
    logging.info(f"Using file: {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
        height = data.get('height', height)
        width = data.get('width', width)
        length = data.get('length', length)
        wall_thickness = data.get('wall_thickness', wall_thickness)
        N = data.get('N', N)
        M = data.get('M', M)
        lid_thickness = data.get('lid_thickness', lid_thickness)
        lid_margin_top = data.get('lid_margin_top', lid_margin_top)
        lid_margin_sides = data.get('lid_margin_sides', lid_margin_sides)
        font_name = data.get('font_name', font_name)
        font_kind = data.get('font_kind', font_kind)
        font_size = data.get('font_size', font_size)
        font_height = data.get('font_height', font_height)
        engraved = data.get('engraved', engraved)
        vertical_text = data.get('vertical_text', vertical_text)
        text_list = data.get('text_list', text_list)
        file_format = data.get('file_format', file_format)
else:
    logging.info(f'Using parameters from script')


logging.info("Generating unit box with width:%.2fmm, length:%.2fmm, height:%.2fmm",
             width, length, height)
logging.info("Wall thickness is %.2fmm", wall_thickness)
logging.info("Compound box will be the size of %.2fx%.2fx%.2fmm",
             N * width, M * length, height)

folder = f'output_pbox_{N}_{M}'
if not os.path.exists(folder):
    os.makedirs(folder)

# To move the box in positive 3D space, well I don't like working in negative dimentions
# easier for me to calculate things
x_offset = width / 2
y_offset = length / 2
z_offset = height / 2

logging.info("Creating box")
# create the box
box = (
       cq.Workplane('XY').box(width, length, height)
       .translate((x_offset, y_offset, z_offset))
       )

# calculated pocket dimentions
p_w = width - (2 * wall_thickness)
p_l = length - (2 * wall_thickness)
p_h = height - wall_thickness

# create the box that is going to be cut out
pocket = (
    cq.Workplane('XY')
    .box(p_w, p_l, p_h)
    .translate((x_offset, y_offset, wall_thickness + z_offset))
    )

# cut out the pocket
box = box.cut(pocket)

# calculate the position of the lid assembly holes
hole_radius = lid_thickness / 2
hole_z_margin = height - (hole_radius + lid_margin_top)
hole_x_margin = hole_radius + lid_margin_sides + wall_thickness

# create the hole
hole = (
        cq.Workplane('XZ').cylinder(length, hole_radius)
        .translate((hole_x_margin, length / 2, hole_z_margin))
        )

# cut out the hole
box = box.cut(hole)

# create the latch, the thingy that holds the lid in place
translation = (
    width - wall_thickness,
    (latch_width / 2) + y_offset,
    height - lid_margin_top
    )

latch_arc = (
        cq.Workplane('XZ')
        .threePointArc((-latch_pitch, lid_margin_top / 2), (0, lid_margin_top))
        .close()
        .extrude(latch_width)
        .translate(translation)
        )

box = box.union(latch_arc)

# create the lid holder
# Lid support is on XZ plane so the points are
lid_support_points = [
    (0,0),
    (-lid_support_pitch, lid_support_size),
    (0, lid_support_size)
    ]

translation = (
    width - wall_thickness,
    (lid_support_size / 2) + y_offset,
    height - (lid_margin_top + (hole_radius * 2) + lid_support_size),
    )

lid_support = (
    cq.Workplane('XZ')
    .polyline(lid_support_points).close()
    .extrude(lid_support_size)
    .translate((translation))
    )

box = box.union(lid_support)
# Keep a copy of unit box
unit_box = box


# populate the unit box in length and width
unit_box = box
for i in range(N):
    box = box.union(unit_box.translate((width * i, 0,0)))
    
unit_array = box
for i in range(M):
    box = box.union(unit_array.translate((0, length * i, 0)))


# Create the lid base
logging.info("Creatinf lid")
lw = width - (2 * (lid_margin_sides + wall_thickness))
ll = length - (2 * (lid_margin_sides + wall_thickness))

translation = (x_offset, y_offset, (height - lid_margin_top - (lid_thickness / 2)))

lid = (
       cq.Workplane('XY')
       .box(lw, ll, lid_thickness)
       .faces('<X')
       .edges('not |Z')
       .fillet(hole_radius - 0.0001)
       .faces('>X')
       .edges('not |Z')
       .fillet(0.5)
       .translate(translation)
       )

# add lid pins
lid_pin = (
        cq.Workplane('XZ').cylinder(p_l + 2, hole_radius)
        .translate((hole_x_margin, length / 2, hole_z_margin))
        .edges('>Y or <Y')
        .fillet(hole_radius)
        )

lid = lid.union(lid_pin)

# add lid handle
translation = (width - wall_thickness - lid_margin_sides - 1,
               y_offset + lid_handle_length / 2,
               height - lid_margin_top)


lid_handle = (
    cq.Workplane('XZ')
    .lineTo(-lid_handle_width, 0)
    .lineTo(-lid_handle_width, lid_handle_height)
    .lineTo(0, lid_handle_height)
    .threePointArc((-0.6, lid_handle_height / 2), (0, 0))
    .close()    
    .extrude(lid_handle_length)
    .translate(translation)
    )

lid = lid.union(lid_handle)
empty_lid = lid

# populate the lid with given texts and export them as individual files
z_offset_text = height - lid_margin_top - font_height if engraved else height - lid_margin_top
# For each text export the lid models and show
lid_pos = [(i, j) for i in range(N) for j in range(M)]
lids = [lid] * len(text_list)
for i, t in enumerate(text_list):
    logging.info("Adding lid with text: \n%s\n%s\n%s", "_" * 10, t, "_" * 10)
    x, y = lid_pos[i]
    translation = ((width * x) + x_offset - (lid_handle_width / 2),
                   (length * y) + y_offset,
                   z_offset_text)
    
    if vertical_text:
        degree = 90
    else:
        degree = 0

    text = (
        cq.Workplane('XY')
        .text(t, font_size, font_height, font=font_name, kind=font_kind)
        .rotate((0,0,0), (0,0,1), degree)
        .translate(translation)
        )

    lids[i] = lids[i].translate((width * x, length * y, 0))
    if engraved:
        lids[i] = lids[i].cut(text)
    else:
        lids[i] = lids[i].union(text)
    
    name = sanitize_filename(f'{t}_{width}_{length}{file_format}')
    file = f'{folder}/{name}'
    logging.info("Exporting lid file %s", file)
    cq.exporters.export(lids[i], file)
    if 'show_object' in globals():
        show_object(lids[i])


# Export model files
name = f'unit_box_{width}_{length}_{height}{file_format}'
file = f'{folder}/{name}'
logging.info("Exporting unit box file %s", file)
cq.exporters.export(unit_box, file)

name = f'box_{N}x{M}_{N * width}_{M * length}_{height}{file_format}'
file = f'{folder}/{name}'
logging.info("Exporting box file %s", file)
cq.exporters.export(box, file)

name = f'emppty_lid_{width}_{length}_{height}{file_format}'
file = f'{folder}/{name}'
logging.info("Exporting empty lid file %s", file)
cq.exporters.export(empty_lid, file)

if 'show_object' in globals():
    show_object(unit_box)
    show_object(box)
    show_object(empty_lid)

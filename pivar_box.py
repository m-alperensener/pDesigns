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
import logging
import cadquery as cq

from helper.pattern import honeycomb

# [Mount Parameters]s
mount_count = 1
mount_thickness = 1.6
mount_beam_size = 3
dowel_length = 10

clearence = 0.2

box_width = 40
box_depth = 40
box_height = 20
box_wall_thickness = 1.6
box_attachment_thickness = 3
box_fillet_r = 4

lid_thickness = 2
lid_clearence = 0.1
lid_text = "pIVAR" # Set to none for no text

font_name = 'DejaVu Serif' # System font name
font_size = 10
font_height = 0.1
engraved = True

# [Pattern Parameters]
pattern = 'honeycomb'
p_radius = 2.5
p_depth = 0.4
p_clearence = 0.8
p_engraved = True

#_____________START  GENERATING BOX________________________
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    force=True
)

# Create Mount Part
if box_height < (mount_count * 32) + box_wall_thickness:
    logging.warning("Box height can not be smaller than %.2fmm",
                    (mount_count * 32) + box_wall_thickness)
    box_height = (mount_count * 32) + box_wall_thickness

if mount_thickness < 0.8:
    logging.warning("Mount thickness can not be smaller than 0.8mm")
    mount_thickness = 0.8

if  box_wall_thickness < 0.8:
    logging.warning("Box wall thickness can not be smaller than 0.8mm")
    box_wall_thickness = max(0.8, box_wall_thickness)

min_w = mount_thickness + mount_beam_size + box_attachment_thickness
min_w = -(min_w + 22 + box_fillet_r + clearence) // -1

if box_width < 2 * min_w:
    logging.warning("Box width can not be smaller than %.2fmm", 2 * min_w)
    box_width = max(box_width, 2 * min_w)

logging.info('Generating box with width:%.2fmm, depth:%.2fmm, height:%.2fmm',
             box_width, box_depth, box_height)
logging.info('Wall thickness is %.2fmm', box_wall_thickness)

logging.info('Creating mount part: made of %d units and %.2fmm long dowel',
             mount_count, dowel_length)

mount = (
    cq.Workplane('XY')
    .lineTo(0, 32.4)
    .lineTo(22, 32.4)
    .lineTo(22, 0)
    .lineTo(22 + mount_thickness + mount_beam_size, 0)
    .lineTo(22 + mount_thickness + mount_beam_size, mount_beam_size)
    .lineTo(22 + mount_thickness, mount_beam_size)
    .lineTo(22 + mount_thickness, 32.4 + mount_thickness)
    .lineTo(0, 32.4 + mount_thickness)
    .close()
    .extrude(-32))

dowel = (
    cq.Workplane('XZ')
    .cylinder(dowel_length, 2.8)
    .translate((12.5, 32.4 - dowel_length / 2, -16))
    )

mount = mount.union(dowel)

mirror_mount = mount.mirror('YZ')
mount = mount.union(mirror_mount)

final_mount = mount
if mount_count > 1:
    for i in range(mount_count):
        final_mount = final_mount.union(mount.translate((0, 0, -32 * i)))

# Create box
logging.info("Generating box")
box = (
    cq.Workplane('XY')
    .box(box_width, box_depth, box_height)
    .edges('|Z').fillet(box_fillet_r)
    .translate((0, -box_depth/2, -box_height/2 + box_wall_thickness))
    )

psize_w = box_width - (2 * box_wall_thickness)
psize_d = box_depth - (2 * box_wall_thickness)

box_pocket = (
    cq.Workplane('XY')
    .box(psize_w, psize_d, box_height - box_wall_thickness)
    .edges('|Z').fillet(box_fillet_r)
    .translate((0, -box_depth/2, -box_height/2 + 1.5 * box_wall_thickness))
    )

box = box.cut(box_pocket)

translation = (22 + mount_thickness + clearence + (box_attachment_thickness + mount_beam_size) / 2,
               (box_attachment_thickness + mount_beam_size) / 2,
               -mount_count * 32 / 2 + box_wall_thickness / 2)

mount_hole = (
    cq.Workplane('XY')
    .box(box_attachment_thickness + mount_beam_size,
         box_attachment_thickness + mount_beam_size,
         mount_count * 32 + box_wall_thickness)
    )

mount_hole_cutout = (
    cq.Workplane('XY')
    .box(mount_beam_size + clearence,
         mount_beam_size + clearence,
         mount_count * 32)
    .translate((-(box_attachment_thickness - clearence) / 2,
                -(box_attachment_thickness - clearence) / 2,
                -box_wall_thickness / 2))
    )

mount_hole = (
    mount_hole.cut(mount_hole_cutout)
    .translate(translation)
    )

box = box.union(mount_hole)
box = box.union(mount_hole.mirror('YZ'))

# lid
logging.info("Generating lid")
lid = (cq.Workplane('XY')
       .box(psize_w - lid_clearence,
            psize_d - lid_clearence,
            box_wall_thickness)
       .edges('|Z').fillet(box_fillet_r)
       .translate((0, -box_depth/2, box_wall_thickness / 2))
       )

lid_pocket = (cq.Workplane('XY')
              .box(psize_w - lid_clearence - 2,
                   psize_d - lid_clearence - 2,
                   box_wall_thickness)
              .edges('|Z').fillet(box_fillet_r)
              .translate((0, -box_depth/2, box_wall_thickness / 2))
              )

lid = lid.cut(lid_pocket)

lid = lid.union(
    cq.Workplane('XY')
    .box(box_width, box_depth, lid_thickness)
    .edges('|Z').fillet(box_fillet_r)
    .translate((0, -box_depth/2, box_wall_thickness + (lid_thickness / 2)))
    )

lid_notch = (
    cq.Workplane('XY')
    .box(10, 5, lid_thickness)
    .edges('|Z').fillet(2)
    .translate((0, -box_depth, box_wall_thickness + (lid_thickness / 2)))
    )

lid = lid.union(lid_notch)

if lid_text is not None:
    logging.info("Adding lid text: \n%s\n%s\n%s", "_" * 10, lid_text, "_" * 10)
    text = (
        cq.Workplane('XY')
        .text(lid_text,
              font_size,
              font_height,
              # Here add the kind to select bold italic etc
              kind='bold',
              font=font_name)
        .translate((0, -box_depth/2, box_wall_thickness + lid_thickness))
        )

    if engraved:
        lid = lid.cut(text.translate((0, 0, -font_height)))
    else:
        lid = lid.union(text)
else:
    logging.info("No lid text")

# Add pattern to front
sx = box_width - (2 * box_fillet_r) - 4
sz = box_height -4
rotation = ((0, 0, 0), (1, 0, 0), 90)

y = -box_depth
if p_engraved:
    y = y + p_depth
translation = (0, y, -box_height / 2 + box_wall_thickness)

if pattern is not None:
    logging.info("Adding %s %s pattern",
                 "engraved" if p_engraved else "emmbossed", pattern)
else:
    logging.info("No pattern")

if pattern == 'honeycomb':
    u = honeycomb((sx, sz), p_radius, p_depth, p_clearence, rotation, translation)
    if p_engraved:
        box = box.cut(u)
    else:
        box = box.union(u)

out_dir = f'output_pivar_{box_width}x{box_depth}x{box_height}'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

file = f'{out_dir}/ivar_mount_{mount_count}.stl'
logging.info("Exporting mount to %s", file)
cq.exporters.export(final_mount, file)

file = f'{out_dir}/ivar_box_{box_width}x{box_depth}x{box_height}.stl'
logging.info("Exporting box to %s", file)
cq.exporters.export(box, file)

file = f'{out_dir}/ivar_lid_{box_width}x{box_depth}x{lid_thickness}.stl'
logging.info("Exporting lid to %s", file)
cq.exporters.export(lid, file)

if 'show_object' in globals():
    show_object(lid)
    show_object(box)
    show_object(final_mount)
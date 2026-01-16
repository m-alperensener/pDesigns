# pBox

A simple script for creating basic, functional boxes with lids.

If you need to build straightforward, utilitarian boxes rather than fancy ones, this is for you. I originally created this to make a tiny set of boxes for storing my SMD components.

Just edit the parameters in the script to generate multiple boxes with custom lid text.

## Main Box Dimensions

All dimensions are in millimeters.

* **`width`**: The dimension along the X-axis.
* **`length`**: The dimension along the Y-axis.
* **`height`**: The dimension along the Z-axis.
* **`wall_thickness`**: The thickness of the box walls.
* **`N`** and **`M`**: These define how many box compartments are populated along the X and Y axes, respectively. The final assembly size will be (`width` × `N`) by (`length` × `M`) mm.

## Lid Parameters

Lid assembly holes and dimensions are adjusted using the following parameters:

* **`lid_thickness`**: The thickness of the lid; this also determines the size of the hinge holes.
* **`lid_handle_length`**, **`lid_handle_height`**, and **`lid_handle_width`**: These define the size of the small handle centered on the edge of the lid.
* **`lid_margin_top`**: Sets the vertical position of the lid from the top and defines the size of the snap-fit mechanism on the box.
* **`lid_margin_sides`**: Defines the clearance between the lid and the inner walls of the box. **0.2mm** is usually sufficient; use caution if you set this value lower.

## Lid Text

* **`font_name`**: This pulls from your system fonts, so ensure the font is installed on your OS.
* **`font_kind`**: Specify the font style (e.g., 'bold', 'italic', etc.).
* **`font_size`** and **`font_height`**: Used to scale your text. The ideal values depend on the box size and font type; some trial and error may be required.
* **`engraved`**: If set to **`True`**, the text will be engraved into the lid. If **`False`**, the text will be embossed (raised).
* **`text_list`**: Enter the strings to be placed on each lid. Regardless of the **`N`** and **`M`** values, lids will only be created for the entries provided in this list. You can use **`\n`** for multiline text.
    * *Note:* The script may fail if the number of items in the list exceeds the total compartments (**`N`** × **`M`**).

# Example Parameters

```python
height = 30
width = 60
length = 30 
wall_thickness = 2

N = 1
M = 3

lid_thickness = 2
lid_handle_length = 10
lid_handle_height = 4
lid_handle_width = 3
lid_margin_top = 1.8 
lid_margin_sides = 0.2

font_name = 'DejaVu Sans'
font_kind = 'bold'
font_size = 6.4
font_height = 0.8
engraved = False

text_list = ['#1\npBox', '#2\npBox', '#3\npBox']
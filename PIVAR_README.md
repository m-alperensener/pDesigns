# pIVAR

A **parametric** box for your IKEA IVAR shelf system. Consisting of only three parts, the mount allows you to hang your box and hold it securely in place on the IVAR shelf beam. You can also add custom text to the lid.

# Parameters

The setup is straightforward—simply adjust the values and experiment. Please note that all **dimensions are in mm**.

## Box Dimensions

* **`box_width`**, **`box_depth`**, and **`box_height`**: These define your box dimensions, including the wall thickness.
* **`box_wall_thickness`**: The minimum value is 0.8mm (unless you modify the code).
* **`box_attachment_thickness`**: This defines the dimensions of the rear attachment that hangs onto the mount. For larger boxes, increase this value for added strength.
* **`box_fillet_r`**: Adjusts the roundness of the box edges.

> [!IMPORTANT]
> The box width cannot be smaller than the width required for the mount and fillet radius. Additionally, the height must be at least **32mm**, which is the unit size of the mount part.

## Lid and Text

The script automatically generates a fitting lid based on your **`lid_thickness`**.

* **`lid_clearence`**: Adjusts the gap between the lid and the box opening.
* **`lid_text`**: Enter your custom text here, or set it to `None` if you prefer a plain lid.
* **`font_name` & `font_size`**: Choose your font and adjust the size. The text is automatically centered, so you may need to tweak the size to find the "sweet spot."
* **`font_height`**: A value of 0.6mm is usually sufficient.
* **`engraved`**: Set this to **True** for engraved text or **False** for embossed.
    * **Tip:** Engraving is often better for 3D printing, as it allows you to print the lid face-down on the build plate.
    * **Tip:** For multi-color printers, you can set a very low height (e.g., 0.005mm) to color the text surface without affecting geometry.

## Mount Settings

While most mount dimensions are fixed, you can customize its strength:

* **`mount_count`**: A value of 1 creates a mount that fits into one row of holes. Increase this for a taller, stronger mount.
* **`mount_thickness`**: Increase this to reinforce the part.
* **`dowel_length`**: 6mm is usually perfect, but you can increase or decrease this as necessary. Even the smallest size is typically sufficient to hold the mount in place.

## Pattern Settings

You can generate honeycomb pattern on the front face of the box.

* **`pattern`**: Select the pattern type. If you dont want pattern set it to `None`.
    * `honeycomb`
    * `diamond`
    * `star`
    * `plus`
    * `slot`
    * `square` 
* **`p_radius`**: Defines the radius of the pattern.
* **`p_depth`**: Sets the thickness of pattern.
* **`p_clearence`**: Specifies the clearence in between patterns.
* **`p_margin`**: Margin from the edge of the box.
* **`p_engraved`**: Setting this to **`True`** makes the patters engraved, otherwise it is embossed.
* **`p_invert`**: Inverts pattern's poket and extrude.

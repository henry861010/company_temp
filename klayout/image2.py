import pya
import os

# 1. Setup paths and Layer/Datatype
input_gds = "/Users/henry/Desktop/test/input2.gds2"
output_png = "/Users/henry/Desktop/test/output.png"

L_NUM, D_NUM = 64, 0  # Change to your target layer/datatype

# 2. Load Layout
layout = pya.Layout()
layout.read(input_gds)
target_idx = layout.layer(L_NUM, D_NUM)

# 3. Setup the View (this is the "rendering engine")
view = pya.LayoutView()
view.show_layout(layout, False)

# 4. Configure Visuals: Hide Grid and Text
view.set_config("grid-visible", "false")
view.set_config("text-visible", "false")
view.set_config("background-color", "#ffffff") # White background

# 5. Filter Layers: Hide everything except our target
# We also set our target layer to be solid Black (#000000)
lp_it = view.begin_layers()
while not lp_it.at_end():
    lp = lp_it.current()
    if lp.layer_index() == target_idx:
        lp.visible = True
        lp.fill_color = 0x000000 # Black fill
        lp.frame_color = 0xFF0000 # Black border
        lp.dither_pattern = 0     # Solid fill (no dots/patterns)
        lp.transparent = False
    else:
        lp.visible = True
        
    view.set_layer_properties(lp_it, lp)
    lp_it.next()

# 6. Zoom and Save
view.zoom_fit()
# Resolution: 2000x2000 for high quality
view.save_image(output_png, 2000, 2000)

print(f"B&W image of {L_NUM}/{D_NUM} saved to {output_png}")
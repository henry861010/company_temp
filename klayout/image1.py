import pya

input_gds = "/Users/henry/Desktop/test/input.gds"
output_dir = "/Users/henry/Desktop/test/output.png"

image_size = 5000
L_NUM, D_NUM = 64, 0  # Change to your target layer/datatype

# 2. Load Layout
layout = pya.Layout()
layout.read(input_gds)
target_indices = [layout.layer(L_NUM, D_NUM)]
#target_indices = [1,2]

# 3. Setup the View (this is the "rendering engine")
layout_view = pya.LayoutView()
layout_view.show_layout(layout, False)

# 4. Configure Visuals: Hide Grid and Text
layout_view.set_config("background-color", "#FFFFFF")
layout_view.set_config("grid-visible", "false")
layout_view.set_config("background-color", "#ffffff") # White background
layout_view.max_hier()

top_cell = layout.top_cell()
layout_view.active_cellview().cell = top_cell
for lyp in layout_view.each_layer():
    layer_index = lyp.layer_index()
    if layer_index in target_indices:
        #lyp.fill_color = 0x000000  
        #lyp.frame_color = 0x000000  
        lyp.dither_pattern = 0
        lyp.transparent = True
    else:
        lyp.visible = False

# 5. Calculate scaling to maintain aspect ratio
box = top_cell.bbox()
if box.width() > box.height():
    img_w = image_size
    img_h = int(image_size * box.height() / box.width())
else:
    img_h = image_size
    img_w = int(image_size * box.width() / box.height())

# 6. write image
layout_view.save_image(output_dir, img_w, img_h)
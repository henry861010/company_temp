import pya

input_gds = "/Users/henry/Desktop/test/input.gds"

# 1. Load the layout
layout = pya.Layout()
layout.read(input_gds)

# 2. Iterate through all defined layers in the layout
# KLayout stores layer definitions in its internal 'layer_indexes'
for layer_idx in layout.layer_indexes():
    
    # Get the LayerInfo object for this index
    info = layout.get_info(layer_idx)
    
    # Access the XXX (layer) and YYY (datatype)
    layer_num = info.layer
    datatype_num = info.datatype
    name = info.name # This might be empty if no .lyp is loaded
    
    print(f"Internal Index: {layer_idx} -> GDS Layer: {layer_num}, Datatype: {datatype_num}")
    
'''
Accessing Shapes on a Specific Layer
If you want to actually "do" something with the shapes on layer 64/0, you have to 
find the internal index first
'''
# Find the internal index for Layer 64, Datatype 0
target_layer = layout.layer(64, 0)

# Get the top cell (assuming you know the name or take the first one)
top_cell = layout.top_cell()

# Access shapes on that layer
shapes = top_cell.shapes(target_layer)
print(len(shapes))
for shape in shapes:
    if shape.is_polygon():
        print("Polygon: " + str(shape.dpolygon))
    elif shape.is_path():
        print("Path: " + str(shape.dpath))
    elif shape.is_text():
        print("Text: " + str(shape.dtext))
    elif shape.is_box():
        print("Box: " + str(shape.dbox))
        
iter = top_cell.begin_shapes_rec(target_layer)
while not iter.at_end():
    # 'shape' is the local geometry
    shape = iter.shape()
    
    # 'trans' is the total transformation from Top -> Subcell -> Shape
    #trans = iter.itrans() 
    trans = iter.dtrans() 
    
    if shape.is_box():
        #global_box = shape.box.transformed(trans)
        global_box = shape.dbox.transformed(trans)
        print(f"Global Box: {global_box}")
        
    elif shape.is_polygon():
        #global_poly = shape.polygon.transformed(trans)
        global_poly = shape.dpolygon.transformed(trans)
        print(f"Global Polygon: {global_poly}")

    iter.next()
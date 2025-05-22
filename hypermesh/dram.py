def get_dram_info(model, config):
    now_z = 0
    layer_info_list = []
    
    ### substrate layer
    dram = find_key_recursive(model, "dram")
    dram1_x = 0
    dram1_y = 0
    dram3_x = find_key_recursive(dram, "dramSize_x")
    dram3_y = find_key_recursive(dram, "dramSize_y")
    dram_dim = [dram1_x, dram1_y, dram3_x, dram3_y]
    
    bottomBR_material = find_key_recursive("bottomBR_material")
    bottomBR_thk = find_key_recursive("bottomBR_thk")
    topBR_material = find_key_recursive("topBR_material")
    topBR_thk = find_key_recursive("topBR_thk")
    substrate_layer_list = find_key_recursive("substrate_info")
    base1_x = find_key_recursive(substrate_layer_list, "???base1_x")
    base1_y = find_key_recursive(substrate_layer_list, "???base1_y")
    base3_x = find_key_recursive(substrate_layer_list, "???base3_x")
    base3_y = find_key_recursive(substrate_layer_list, "???base3_y")
    
    layer_info_list.append({
        "z": now_z, 
        "areas": [
            "type": "BOX",
            "material": [bottomBR_material],
            "dim": [dram_dim],
        ]})
    now_z += bottomBR_thk
    
    for substrate_layer in substrate_layer_list:
        material = substrate_layer_list["???material"]
        thk = substrate_layer_list["???thk"]
        metal_material = substrate_layer_list["???mametal_materialterial"]
        metal_density = substrate_layer_list["???metal_density"]
        
        layer_info_list.append({
            "z": now_z, 
            "areas": [
                "type": "BOX",
                "material": [material],
                "dim": [dram_dim],
                "metal": [metal_material],
                "density": [metal_density]
            ]})
        now_z += thk
    
    layer_info_list.append({
        "z": now_z, 
        "areas": [
            "type": "BOX",
            "material": [topBR_material],
            "dim": [dram_dim],
        ]})
    now_z += topBR_thk
    
    ### core layer
    core_layer_list = find_key_recursive(substrate_layer_list, "???core_layer")
    dram_molding_material = find_key_recursive(substrate_layer_list, "???dram_molding")
    dram_pm_material = find_key_recursive(substrate_layer_list, "???dram_pm")
    die_dram_material = find_key_recursive(substrate_layer_list, "???die_dram")
    for i in range(len(core_layer_list)):
        core_layer = core_layer_list[i]
        dram_pm_thk = core_layer["dram_pm_thk"]
        die_dram_thk = core_layer["die_dram_thk"]
    
        expand1_x = find_key_recursive(core_layer_list, "???expand1_x")
        expand1_y = find_key_recursive(core_layer_list, "???expand1_y")
        expand3_x = find_key_recursive(core_layer_list, "???expand3_x")
        expand3_y = find_key_recursive(core_layer_list, "???expand3_y")
        
        core1_x = base1_x - expand1_x
        core1_y = base1_y - expand1_y
        core3_x = base3_x + expand3_x
        core3_y = base3_y + expand3_y
        core_dim = [core1_x, core1_y, core3_x, core3_y]
        
        ### pm
        layer_info_list.append({
            "z": now_z, 
            "areas": [
                "type": "BOX",
                "material": [dram_molding_material, dram_pm_material],
                "dim": [dram_dim, core_dim],
            ]})
        now_z += dram_pm_thk
        
        ### core
        layer_info_list.append({
            "z": now_z, 
            "areas": [
                "type": "BOX",
                "material": [dram_molding_material, die_dram_material],
                "dim": [dram_dim, core_dim],
            ]})
        now_z += die_dram_thk
        
    info = {}
    info["layer_info"] = layer_info_list
    
    return info
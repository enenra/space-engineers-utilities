import bpy
import os

from ..utils.seut_xml_utils import *
from ..seut_errors          import seut_report
from ..seut_utils           import get_abs_path
from .seut_planet_utils     import *

def export_planet_sbc(self, context: bpy.types.Context):
    """Saves the SBC values to the mod folder"""

    scene = context.scene
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data")

    # 3 options: no file and no entry, file but no entry, file and entry

    # Create XML tree and add initial parameters.
    output = get_relevant_sbc(os.path.dirname(path_data), 'PlanetGeneratorDefinitions', 'PlanetGeneratorDefinition', scene.seut.subtypeId)
    if output is not None:
        file_to_update = output[0]
        lines = output[1]
        start = output[2]
        end = output[3]
    
    if output is not None and start is not None and end is not None and scene.seut.export_sbc_type == 'update':
        update_sbc = True
        lines_entry = lines[start:end]
        definitions = None
        def_definition = None
    else:
        update_sbc = False
        lines_entry = ""
        definitions = ET.Element('Definitions')

    if not update_sbc:
        add_attrib(definitions, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        add_attrib(definitions, 'xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cube_blocks = add_subelement(definitions, 'PlanetGeneratorDefinitions')
        def_definition = add_subelement(cube_blocks, 'PlanetGeneratorDefinition')

        def_Id = add_subelement(def_definition, 'Id')
        add_subelement(def_Id, 'TypeId', 'PlanetGeneratorDefinition')
        add_subelement(def_Id, 'SubtypeId', scene.seut.subtypeId)
        
    
    # Surface Detail
    def_SurfaceDetail = 'SurfaceDetail'
    if not update_sbc:
        def_SurfaceDetail = add_subelement(def_definition, 'SurfaceDetail')

    if scene.seut.sd_texture == "":
        sd_path = ""
    else:
        sd_path = get_abs_path(scene.seut.sd_texture)
    lines_entry = update_add_subelement(def_SurfaceDetail, 'Texture', os.path.splitext(sd_path)[0], update_sbc, lines_entry)

    lines_entry = update_add_subelement(def_SurfaceDetail, 'Size', scene.seut.sd_size, update_sbc, lines_entry)
    lines_entry = update_add_subelement(def_SurfaceDetail, 'Scale', scene.seut.sd_scale, update_sbc, lines_entry)

    def_SD_Slope = 'Slope'
    if not update_sbc:
        def_SD_Slope = add_subelement(def_SurfaceDetail, 'Slope')

    lines_entry = update_add_attrib(def_SD_Slope, 'Min', scene.seut.sd_slope_min, update_sbc, lines_entry)
    lines_entry = update_add_attrib(def_SD_Slope, 'Max', scene.seut.sd_slope_max, update_sbc, lines_entry)

    lines_entry = update_add_subelement(def_SurfaceDetail, 'Transition', scene.seut.sd_transition, update_sbc, lines_entry)
    
    # Ore Mappings
    if len(scene.seut.ore_mappings) > 0:
        if not update_sbc:
            def_OreMappings = add_subelement(def_definition, 'OreMappings')
        else:
            def_OreMappings = ET.Element('OreMappings')
        
        for om in scene.seut.ore_mappings:
            def_Ore = ET.SubElement(def_OreMappings, 'Ore')
            add_attrib(def_Ore, 'Value', om.value)
            add_attrib(def_Ore, 'Type', om.ore_type)
            add_attrib(def_Ore, 'Start', om.start)
            add_attrib(def_Ore, 'Depth', om.depth)
            add_attrib(def_Ore, 'TargetColor', '#%02x%02x%02x' % (int(om.target_color[0] * 255), int(om.target_color[1] * 255), int(om.target_color[2] * 255)))
            add_attrib(def_Ore, 'ColorInfluence', 256) # This is ignored by the game.
        
        if update_sbc:
            lines_entry = convert_back_xml(def_OreMappings, 'OreMappings', lines_entry, 'PlanetGeneratorDefinition')

    # Complex Materials
    if len(scene.seut.material_groups) > 0:
        if not update_sbc:
            def_ComplexMaterials = add_subelement(def_definition, 'ComplexMaterials')
        else:
            def_ComplexMaterials = ET.Element('ComplexMaterials')
        
        for mg in scene.seut.material_groups:
            def_MaterialGroup = ET.SubElement(def_ComplexMaterials, 'MaterialGroup')
            add_attrib(def_MaterialGroup, 'Name', mg.name)
            add_attrib(def_MaterialGroup, 'Value', mg.value)
            
            if len(mg.rules) > 0:
                for r in mg.rules:
                    def_Rule = ET.SubElement(def_MaterialGroup, 'Rule')

                    if len(r.layers) > 0:
                        def_Layers = add_subelement(def_Rule, 'Layers')

                        for l in r.layers:
                            def_Layer = ET.SubElement(def_Layers, 'Layer')
                            add_attrib(def_Layer, 'Material', l.material)
                            add_attrib(def_Layer, 'Depth', l.depth)
                    
                    def_Height = add_subelement(def_Rule, 'Height')
                    add_attrib(def_Height, 'Min', round(r.height_min, 2))
                    add_attrib(def_Height, 'Max', round(r.height_max, 2))
                    
                    def_Latitude = add_subelement(def_Rule, 'Latitude')
                    add_attrib(def_Latitude, 'Min', round(r.latitude_min, 2))
                    add_attrib(def_Latitude, 'Max', round(r.latitude_max, 2))
                    
                    def_Slope = add_subelement(def_Rule, 'Slope')
                    add_attrib(def_Slope, 'Min', round(r.slope_min, 2))
                    add_attrib(def_Slope, 'Max', round(r.slope_max, 2))

        if update_sbc:
            lines_entry = convert_back_xml(def_ComplexMaterials, 'ComplexMaterials', lines_entry, 'PlanetGeneratorDefinition')

    # Environment Items
    if len(scene.seut.environment_items) > 0:
        if not update_sbc:
            def_EnvironmentItems = add_subelement(def_definition, 'EnvironmentItems')
        else:
            def_EnvironmentItems = ET.Element('EnvironmentItems')

        for ei in scene.seut.environment_items:
            def_Item = ET.SubElement(def_EnvironmentItems, 'Item')

            if len(ei.biomes) > 0:
                def_Biomes = ET.SubElement(def_Item, 'Biomes')
                for biome in ei.biomes:
                    def_Biome = ET.SubElement(def_Biomes, 'Biome')
                    def_Biome.text = str(biome.value)

            if len(ei.materials) > 0:
                def_Materials = ET.SubElement(def_Item, 'Materials')
                for mat in ei.materials:
                    def_Material = ET.SubElement(def_Materials, 'Material')
                    def_Material.text = mat.name

            if len(ei.items) > 0:
                def_SubItems = ET.SubElement(def_Item, 'Items')
                for i in ei.items:
                    def_SubItem = ET.SubElement(def_SubItems, 'Item')
                    add_attrib(def_SubItem, 'TypeId', i.type_id)
                    add_attrib(def_SubItem, 'SubtypeId', i.subtype_id)
                    add_attrib(def_SubItem, 'Density', round(i.density, 2))

            if len(ei.rules) > 0:
                for r in ei.rules:
                    def_Rule = ET.SubElement(def_Item, 'Rule')

                    def_Height = add_subelement(def_Rule, 'Height')
                    add_attrib(def_Height, 'Min', round(r.height_min, 2))
                    add_attrib(def_Height, 'Max', round(r.height_max, 2))
                    
                    def_Latitude = add_subelement(def_Rule, 'Latitude')
                    add_attrib(def_Latitude, 'Min', round(r.latitude_min, 2))
                    add_attrib(def_Latitude, 'Max', round(r.latitude_max, 2))
                    
                    def_Slope = add_subelement(def_Rule, 'Slope')
                    add_attrib(def_Slope, 'Min', round(r.slope_min, 2))
                    add_attrib(def_Slope, 'Max', round(r.slope_max, 2))

        if update_sbc:
            lines_entry = convert_back_xml(def_EnvironmentItems, 'EnvironmentItems', lines_entry, 'PlanetGeneratorDefinition')

    # Hill Params
    def_HillParams = 'HillParams'
    if not update_sbc:
        def_HillParams = add_subelement(def_definition, 'HillParams')

    lines_entry = update_add_attrib(def_HillParams, 'Min', round(scene.seut.hill_params_min, 2), update_sbc, lines_entry)
    lines_entry = update_add_attrib(def_HillParams, 'Max', round(scene.seut.hill_params_max, 2), update_sbc, lines_entry)
    
    # Write to file, place in export folder
    if not update_sbc:
        temp_string = ET.tostring(definitions, 'utf-8')
        try:
            temp_string.decode('ascii')
        except UnicodeDecodeError:
            seut_report(self, context, 'ERROR', True, 'E033')
        xml_string = xml.dom.minidom.parseString(temp_string)
        xml_formatted = xml_string.toprettyxml()
    
    else:
        xml_formatted = lines.replace(lines[start:end], lines_entry)
        xml_formatted = format_entry(xml_formatted)
        target_file = file_to_update

    if update_sbc:
        target_file = file_to_update
    else:
        filename = scene.seut.subtypeId
        target_file = os.path.join(path_data, "PlanetDataFiles", filename + ".sbc")
        if not os.path.exists(os.path.join(path_data, "PlanetDataFiles")):
            os.makedirs(os.path.join(path_data, "PlanetDataFiles"))
        
        # This covers the case where a file exists but the SBC export setting forces new file creation.
        counter = 1
        while os.path.exists(target_file):
            target_file = os.path.splitext(target_file)[0]
            split = target_file.split("_")
            try:
                number = int(split[len(split)-1]) + 1
                target_file = target_file[:target_file.rfind("_")]
                target_file = f"{target_file}_{number}.sbc"
            except:
                target_file = target_file + "_1.sbc"

    exported_xml = open(target_file, "w")
    exported_xml.write(xml_formatted)

    if not update_sbc:
        seut_report(self, context, 'INFO', False, 'I004', target_file)
    else:
        seut_report(self, context, 'INFO', False, 'I015', scene.seut.subtypeId, target_file)

    return {'FINISHED'}


def export_planet_maps(scene: bpy.types.Scene):
    """Saves the baked images saved in the BLEND file to the mod folder"""

    sides = ['front', 'back', 'left', 'right', 'up', 'down']

    for img in bpy.data.images:
        for side in sides:
            if img.name == side and scene.seut.export_map_height:
                filepath = os.path.join(get_abs_path(scene.seut.mod_path), 'Data', 'PlanetDataFiles', scene.seut.subtypeId, img.name + '.png')
                scene.render.image_settings.color_depth = '16'
                scene.render.image_settings.color_mode = 'BW'
                img.save_render(filepath, scene=scene)

            elif img.name == side + '_mat' and scene.seut.export_map_biome:
                filepath = os.path.join(get_abs_path(scene.seut.mod_path), 'Data', 'PlanetDataFiles', scene.seut.subtypeId, img.name + '.png')
                scene.render.image_settings.color_depth = '8'
                scene.render.image_settings.color_mode = 'RGB'
                img.save_render(filepath, scene=scene)

            elif img.name == side + '_add' and scene.seut.export_map_spots:
                filepath = os.path.join(get_abs_path(scene.seut.mod_path), 'Data', 'PlanetDataFiles', scene.seut.subtypeId, img.name + '.png')
                scene.render.image_settings.color_depth = '8'
                scene.render.image_settings.color_mode = 'RGB'
                img.save_render(filepath, scene=scene)

    return {'FINISHED'}


def bake_planet_map(context: bpy.types.Context):
    """Bakes the bake source to the bake target"""

    scene = context.scene

    bake_type = scene.seut.bake_type
    bake_resolution = int(scene.seut.bake_resolution)
    bake_target = scene.seut.bake_target
    bake_source = scene.seut.bake_source

    engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    scene.render.bake.use_selected_to_active = True

    def create_image(name: str, resolution: int) -> bpy.types.Image:
        if name in bpy.data.images:
            img = bpy.data.images[name]
            bpy.data.images.remove(img)

        img = bpy.data.images.new(
            name=name,
            width=resolution,
            height=resolution, 
            alpha=False,
            float_buffer=True,
            is_data=True,
            tiled=False
        )

        return img
    
    mats = []
    for slot in bake_target.material_slots:
        mats.append(slot.material)

    # TODO: SURFACE material changes go in here
    if bake_type == 'height':
        suffix = ""
        scene.render.bake.image_settings.color_depth = '16'
        scene.render.bake.image_settings.color_mode = 'BW'
    elif bake_type == 'biome':
        suffix = "_mat"
        scene.render.bake.image_settings.color_depth = '8'
        scene.render.bake.image_settings.color_mode = 'RGB'
    else:
        scene.render.bake.image_settings.color_depth = '8'
        scene.render.bake.image_settings.color_mode = 'RGB'
        suffix = "_add"

    for mat in mats:
        node = mat.node_tree.nodes['IMAGE']
        node.image = create_image(mat.name + suffix, bake_resolution)
        node.select = True

    bake_source.hide_viewport = False
    bake_source.select_set(True)
    bake_source.hide_set(False)

    bake_target.hide_viewport = False
    bake_target.select_set(True)
    bake_target.hide_set(False)
    context.window.view_layer.objects.active = bake_target

    bpy.ops.object.bake(type='COMBINED')

    scene.render.engine = engine

    return {'FINISHED'}


def import_planet_sbc(self, context):
    """"""

    if self.planet_def == 'none':
        return {'CANCELLED'}

    scene = context.scene
    tree = ET.parse(self.filepath)
    root = tree.getroot()

    planet_root = None

    for definition in root:
        if planet_root is not None:
            break

        elif definition.tag == 'PlanetGeneratorDefinitions':
            for planet in definition:
                for elem in planet:
                    if elem.tag == 'Id':
                        for elem2 in elem:
                            if elem2.tag == 'SubtypeId' and elem2.text == self.planet_def:
                                planet_root = planet
                                break
                    break
                break

        elif definition.tag == 'Definition' and '{http://www.w3.org/2001/XMLSchema-instance}type' in definition.attrib and definition.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == 'PlanetGeneratorDefinition':
            for elem in definition:
                if elem.tag == 'Id':
                    for elem2 in elem:
                        if elem2.tag == 'SubtypeId' and elem2.text == self.planet_def:
                            planet_root = definition
                            break
                break
    
    for elem in planet_root:
        if elem.tag == 'OreMappings' and self.import_ore_mappings:
            for ore in elem:
                ore_mapping = add_ore_mapping(context)
                ore_mapping.value = int(ore.attrib['Value'])
                ore_mapping.ore_type = ore.attrib['Type']
                ore_mapping.start = int(ore.attrib['Start'])
                ore_mapping.depth = int(ore.attrib['Depth'])
                hex = ore.attrib['TargetColor'][1:]
                r, g, b = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
                ore_mapping.target_color = (r / 255, g / 255, b / 255)

        if elem.tag == 'ComplexMaterials' and self.import_material_groups:
            for mg in elem:
                material_group = add_material_group(context)
                material_group.name = mg.attrib['Name']
                material_group.value = int(mg.attrib['Value'])

                for r in mg:
                    rule = material_group.rules.add()
                    rule.name = "Rule " + str(len(material_group.rules))

                    for i in r:
                        if i.tag == 'Height':
                            rule.height_min = float(i.attrib['Min'])
                            rule.height_max = float(i.attrib['Max'])
                        elif i.tag == 'Latitude':
                            rule.latitude_min = float(i.attrib['Min'])
                            rule.latitude_max = float(i.attrib['Max'])
                        elif i.tag == 'Slope':
                            rule.slope_min = float(i.attrib['Min'])
                            rule.slope_max = float(i.attrib['Max'])
                        elif i.tag == 'Layers':
                            for l in i:
                                layer = rule.layers.add()
                                layer.material = l.attrib['Material']
                                layer.depth = int(l.attrib['Depth'])

        if elem.tag == 'EnvironmentItems' and self.import_environment_items:
            for i in elem:
                item = scene.seut.environment_items.add()
                item.name = "EnvironmentItem " + str(len(scene.seut.environment_items))

                for e in i:
                    if e.tag == 'Biomes':
                        for b in e:
                            biome = add_biome(context, item)
                            biome.value = int(b.text)
                    
                    elif e.tag == 'Materials':
                        for m in e:
                            material = item.materials.add()
                            material.name = m.text

                    elif e.tag == 'Items':
                        for itm in e:
                            single_item = item.items.add()
                            single_item.type_id = itm.attrib['TypeId']
                            if 'SubtypeId' in itm.attrib:
                                single_item.subtype_id = itm.attrib['SubtypeId']
                            if 'GroupId' in itm.attrib:
                                single_item.group_id = itm.attrib['GroupId']
                            if 'ModifierId' in itm.attrib:
                                single_item.modifier_id = itm.attrib['ModifierId']
                            single_item.density = float(itm.attrib['Density'])

                    elif e.tag == 'Rule':
                        for r in e:
                            rule = item.rules.add()

                            for i in r:
                                if i.tag == 'Height':
                                    rule.height_min = float(i.attrib['Min'])
                                    rule.height_max = float(i.attrib['Max'])
                                elif i.tag == 'Latitude':
                                    rule.latitude_min = float(i.attrib['Min'])
                                    rule.latitude_max = float(i.attrib['Max'])
                                elif i.tag == 'Slope':
                                    rule.slope_min = float(i.attrib['Min'])
                                    rule.slope_max = float(i.attrib['Max'])

    return {'FINISHED'}
import bpy
import os
import re

from ..materials.seut_materials import get_seut_texture_path
from ..utils.seut_xml_utils     import *
from ..seut_errors              import *
from .seut_export_utils         import create_relative_path


def export_transparent_mat(self, context, subtype_id):
    """Exports a defined transparent material."""

    scene = context.scene
    material = bpy.data.materials[subtype_id]
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data")
    
    output = get_relevant_sbc(os.path.dirname(path_data), 'TransparentMaterials', subtype_id)
    if output is not None:
        file_to_update = output[0]
        lines = output[1]
        start = output[2]
        end = output[3]

    # Neither a TransparentMat file nor an entry for this particular one was found
    if file_to_update is None:
        definitions = ET.Element('Definitions')
        add_attrib(definitions, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        add_attrib(definitions, 'xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
        cube_blocks = add_subelement(definitions, 'TransparentMaterials')
        def_definition = add_subelement(cube_blocks, 'TransparentMaterial')
        update = False
    
    # TransparentMat-tree was found but no entry for this TransparentMat exists
    elif file_to_update is not None and start is None and end is None:
        tree = ET.parse(lines)
        definitions = tree.getroot()
        for elem in definitions:
            if elem.tag == 'TransparentMaterials':
                def_definition = add_subelement(elem, 'TransparentMaterial')
                break
        update = False
    
    # TransparentMat-tree & entry for this particular TransparentMat was found
    else:
        definitions = None
        lines_entry = lines[start:end]
        update = True
    
    lines_entry = update_add_subelement(def_definition, 'AlphaMistingEnable', material.seut.alpha_misting_enable, update, lines_entry)
    lines_entry = update_add_subelement(def_definition, 'AlphaMistingStart', material.seut.alpha_misting_start, update, lines_entry)
    lines_entry = update_add_subelement(def_definition, 'AlphaMistingEnd', material.seut.alpha_misting_end, update, lines_entry)
    
    lines_entry = update_add_subelement(def_definition, 'CanBeAffectedByOtherLights', material.seut.affected_by_other_lights, update, lines_entry)
    
    lines_entry = update_add_subelement(def_definition, 'SoftParticleDistanceScale', material.seut.soft_particle_distance_scale, update, lines_entry)

    cm_path = get_seut_texture_path('CM', material)
    cm_path = os.path.join(os.path.splitext(cm_path)[0], ".dds")
    cm_path = create_relative_path(cm_path, 'Textures')
    lines_entry = update_add_subelement(def_definition, 'Texture', cm_path, update, lines_entry)
    
    if not update:
        def_color = add_subelement(def_definition, 'Color')
    else:
        def_color = ET.Element(def_definition, 'Color')
    add_subelement(def_color, 'X', material.seut.color[0])
    add_subelement(def_color, 'Y', material.seut.color[1])
    add_subelement(def_color, 'Z', material.seut.color[2])
    add_subelement(def_color, 'W', material.seut.color[3])
    if update:
        lines_entry = convert_back_xml(def_color, 'Color', lines_entry)

    if not update:
        def_color_add = add_subelement(def_definition, 'ColorAdd')
    else:
        def_color_add = ET.Element(def_definition, 'ColorAdd')
    add_subelement(def_color_add, 'X', material.seut.color_add[0])
    add_subelement(def_color_add, 'Y', material.seut.color_add[1])
    add_subelement(def_color_add, 'Z', material.seut.color_add[2])
    add_subelement(def_color_add, 'W', material.seut.color_add[3])
    if update:
        lines_entry = convert_back_xml(def_color, 'ColorAdd', lines_entry)

    if not update:
        def_shadow_multiplier = add_subelement(def_definition, 'ShadowMultiplier')
    else:
        def_shadow_multiplier = ET.Element(def_definition, 'ShadowMultiplier')
    if material.seut.technique == 'SHIELD':
        add_subelement(def_shadow_multiplier, 'X', material.seut.shadow_multiplier_x)
        add_subelement(def_shadow_multiplier, 'Y', material.seut.shadow_multiplier_y)
        add_subelement(def_shadow_multiplier, 'Z', 0) # unused
        add_subelement(def_shadow_multiplier, 'W', 0) # unused
    else:
        add_subelement(def_shadow_multiplier, 'X', material.seut.shadow_multiplier[0])
        add_subelement(def_shadow_multiplier, 'Y', material.seut.shadow_multiplier[1])
        add_subelement(def_shadow_multiplier, 'Z', material.seut.shadow_multiplier[2])
        add_subelement(def_shadow_multiplier, 'W', material.seut.shadow_multiplier[3])
    if update:
        lines_entry = convert_back_xml(def_shadow_multiplier, 'ShadowMultiplier', lines_entry)
    
    if not update:
        def_light_multiplier = add_subelement(def_definition, 'LightMultiplier')
    else:
        def_light_multiplier = ET.Element(def_definition, 'LightMultiplier')
    if material.seut.technique == 'SHIELD':
        add_subelement(def_light_multiplier, 'X', material.seut.light_multiplier_x)
        add_subelement(def_light_multiplier, 'Y', material.seut.light_multiplier_y)
        add_subelement(def_light_multiplier, 'Z', material.seut.light_multiplier_z)
        add_subelement(def_light_multiplier, 'W', 0) # unused
    else:
        add_subelement(def_light_multiplier, 'X', material.seut.light_multiplier[0])
        add_subelement(def_light_multiplier, 'Y', material.seut.light_multiplier[1])
        add_subelement(def_light_multiplier, 'Z', material.seut.light_multiplier[2])
        add_subelement(def_light_multiplier, 'W', material.seut.light_multiplier[3])
    if update:
        lines_entry = convert_back_xml(def_light_multiplier, 'LightMultiplier', lines_entry)
    
    lines_entry = update_add_subelement(def_definition, 'Reflectivity', material.seut.reflectivity, update, lines_entry)
    lines_entry = update_add_subelement(def_definition, 'Fresnel', material.seut.fresnel, update, lines_entry)
    lines_entry = update_add_subelement(def_definition, 'ReflectionShadow', material.seut.reflection_shadow, update, lines_entry)

    lines_entry = update_add_subelement(def_definition, 'GlossTextureAdd', material.seut.gloss_texture_add, update, lines_entry)

    ng_path = get_seut_texture_path('NG', material)
    ng_path = os.path.join(os.path.splitext(ng_path)[0], ".dds")
    ng_path = create_relative_path(ng_path, 'Textures')
    lines_entry = update_add_subelement(def_definition, 'Gloss', ng_path, update, lines_entry)

    lines_entry = update_add_subelement(def_definition, 'SpecularColorFactor', material.seut.specular_color_factor, update, lines_entry)
    lines_entry = update_add_subelement(def_definition, 'IsFlareOccluder', material.seut.is_flare_occluder, update, lines_entry)
    
    if not update:
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
    
    # This removes empty lines
    # xml_formatted = re.sub(r'\n\s*\n', '\n', xml_formatted)

    if file_to_update is None:
        target_file = os.path.join(path_data, "TransparentMaterials.sbc")
        if not os.path.exists(path_data):
            os.makedirs(path_data)
    elif file_to_update is not None and start is None and end is None:
        target_file = os.path.join(path_data, file_to_update)
    else:
        target_file = file_to_update

    exported_xml = open(target_file, "w")
    exported_xml.write(xml_formatted)

    return {'FINISHED'}
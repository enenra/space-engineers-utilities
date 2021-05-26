import bpy
import os
import re

from ..utils.seut_xml_utils import *
from ..seut_errors          import *
from ..seut_utils           import get_preferences


def export_transparent_mat(self, context, subtype_id):
    """Exports a defined transparent material."""

    scene = context.scene
    material = bpy.data.materials[subtype_id]
    preferences = get_preferences()
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data")
    
    output = get_relevant_sbc(os.path.dirname(path_data), 'TransparentMaterials', subtype_id)
    if output is not None:
        file_to_update = output[0]
        root = output[1]
        element = output[2]

    # Neither a TransparentMat-tree nor an entry for this particular one was found
    if element is None:
        definitions = ET.Element('Definitions')
        add_attrib(definitions, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        add_attrib(definitions, 'xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cube_blocks = add_subelement(definitions, 'TransparentMaterials')
        def_definition = add_subelement(cube_blocks, 'TransparentMaterial')
        update = False
    
    # TransparentMat-tree was found but no entry for this TransparentMat exists
    elif root is not None:
        definitions = root
        for elem in definitions:
            if elem.tag == 'TransparentMaterials':
                def_definition = add_subelement(elem, 'TransparentMaterial')
                break
        update = True
    
    # TransparentMat-tree & entry for this particular TransparentMat was found
    else:
        definitions = root
        def_definition = element
        update = True
    
    add_subelement(def_definition, 'AlphaMistingEnable', material.seut.alpha_misting_enable, True)
    add_subelement(def_definition, 'AlphaMistingStart', material.seut.alpha_misting_start, True)
    add_subelement(def_definition, 'AlphaMistingEnd', material.seut.alpha_misting_end, True)
    
    add_subelement(def_definition, 'AlphaSaturation', material.seut.alpha_saturation, True)
    
    add_subelement(def_definition, 'CanBeAffectedByOtherLights', material.seut.affected_by_other_lights, True)
    
    add_subelement(def_definition, 'SoftParticleDistanceScale', material.seut.soft_particle_distance_scale, True)
    # TODO: CM texture reference
    add_subelement(def_definition, 'Texture', 'placeholder', True)
    
    def_color = add_subelement(def_definition, 'Color')
    add_subelement(def_color, 'X', material.seut.color[0], True)
    add_subelement(def_color, 'Y', material.seut.color[1], True)
    add_subelement(def_color, 'Z', material.seut.color[2], True)
    add_subelement(def_color, 'W', material.seut.color[3] * (1 + material.seut.color_emission_multiplier), True)
    
    def_color_add = add_subelement(def_definition, 'ColorAdd')
    add_subelement(def_color_add, 'X', material.seut.color_add[0])
    add_subelement(def_color_add, 'Y', material.seut.color_add[1])
    add_subelement(def_color_add, 'Z', material.seut.color_add[2])
    add_subelement(def_color_add, 'W', material.seut.color_add[3] * (1 + material.seut.color_emission_multiplier), True)
    
    def_shadow_multiplier = add_subelement(def_definition, 'ShadowMultiplier')
    add_subelement(def_shadow_multiplier, 'X', material.seut.shadow_multiplier[0], True)
    add_subelement(def_shadow_multiplier, 'Y', material.seut.shadow_multiplier[1], True)
    add_subelement(def_shadow_multiplier, 'Z', material.seut.shadow_multiplier[2], True)
    add_subelement(def_shadow_multiplier, 'W', material.seut.shadow_multiplier[3], True)
    
    def_light_multiplier = add_subelement(def_definition, 'LightMultiplier')
    add_subelement(def_light_multiplier, 'X', material.seut.light_multiplier[0], True)
    add_subelement(def_light_multiplier, 'Y', material.seut.light_multiplier[1], True)
    add_subelement(def_light_multiplier, 'Z', material.seut.light_multiplier[2], True)
    add_subelement(def_light_multiplier, 'W', material.seut.light_multiplier[3], True)
    
    add_subelement(def_definition, 'Reflectivity', material.seut.reflectivity, True)
    add_subelement(def_definition, 'Fresnel', material.seut.fresnel, True)
    add_subelement(def_definition, 'ReflectionShadow', material.seut.reflection_shadow, True)

    add_subelement(def_definition, 'GlossTextureAdd', material.seut.gloss_texture_add, True)
    # TODO: NG texture reference
    add_subelement(def_definition, 'Gloss', 'placeholder', True)

    add_subelement(def_definition, 'SpecularColorFactor', material.seut.specular_color_factor, True)
    add_subelement(def_definition, 'IsFlareOccluder', material.seut.is_flare_occluder, True)
    
    temp_string = ET.tostring(definitions, 'utf-8')
    try:
        temp_string.decode('ascii')
    except UnicodeDecodeError:
        seut_report(self, context, 'ERROR', True, 'E033')
    xml_string = xml.dom.minidom.parseString(temp_string)
    xml_formatted = xml_string.toprettyxml()
    
    xml_formatted = re.sub(r'\n\s*\n', '\n', xml_formatted)

    if update:
        target_file = file_to_update
    else:
        target_file = os.path.join(path_data, "TransparentMaterials.sbc")
        if not os.path.exists(path_data):
            os.makedirs(path_data)

    exported_xml = open(target_file, "w")
    exported_xml.write(xml_formatted)

    return
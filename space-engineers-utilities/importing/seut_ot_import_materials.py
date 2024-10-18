import bpy
import os
import xml.etree.ElementTree as ET

from bpy.props import StringProperty
from bpy.types import Operator

from ..materials.seut_ot_create_material    import create_material
from ..seut_text                            import supported_image_types
from ..seut_errors                          import seut_report, get_abs_path
from ..seut_utils                           import get_preferences


class SEUT_OT_Import_Materials(Operator):
    """Import Materials from XML Material Library"""
    bl_idname = "wm.import_materials"
    bl_label = "Import Materials"
    bl_options = {'REGISTER', 'UNDO'}


    filter_glob: StringProperty(
        default='*.xml',
        options={'HIDDEN'}
        )

    filepath: StringProperty(
        subtype="FILE_PATH"
        )


    @classmethod
    def poll(cls, context):
        return context.scene is not None


    def execute(self, context):
        """Import Materials from XML Material Library"""

        result = import_materials(self, context, self.filepath)

        return result


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def import_materials(self, context, filepath):

    preferences = get_preferences()
    materials_path = os.path.join(get_abs_path(preferences.asset_path), 'Materials')

    if preferences.asset_path == "":
        seut_report(self, context, 'ERROR', True, 'E012', "Asset Directory", get_abs_path(preferences.asset_path))
        return {'CANCELLED'}
    elif not os.path.isdir(materials_path):
        os.makedirs(materials_path, exist_ok=True)

    try:
        tree = ET.parse(filepath)
    except:
        seut_report(self, context, 'ERROR', True, 'E040')
        return {'CANCELLED'}

    root = tree.getroot()
    if not root.tag == 'MaterialsLib' and not root.tag == 'Model':
        seut_report(self, context, 'ERROR', True, 'E040')
        return {'CANCELLED'}

    imported = []
    not_imported = []
    for mat in root:
        if mat.tag != 'Material':
            continue

        if mat.attrib['Name'] in bpy.data.materials:
            nodes = bpy.data.materials[mat.attrib['Name']].node_tree.nodes
            found = False
            for node in nodes:
                if node.name == 'SEUT_NODE_GROUP':
                    found = True

            if found:
                not_imported.append(mat.attrib['Name'])
                continue
            else:
                for node in nodes:
                    nodes.remove(node)
                material = create_material(bpy.data.materials[mat.attrib['Name']])
                material.name = mat.attrib['Name']

        else:
            material = create_material()
            material.name = mat.attrib['Name']

        for node in material.node_tree.nodes:
            if node.name == 'CM':
                cm_node = node
            elif node.name == 'NG':
                ng_node = node
            elif node.name == 'ADD':
                add_node = node
            elif node.name == 'ALPHAMASK':
                am_node = node
            elif node.name == 'SEUT_NODE_GROUP':
                ng = node

        cm_img = None
        ng_img = None
        add_img = None
        am_img = None

        for param in mat:
            if param.attrib['Name'] == 'Technique':
                material.seut.technique = param.text

                for i in ng.inputs:
                    if i.name == 'TM Switch':
                        if material.seut.technique in ['GLASS', 'HOLO', 'SHIELD']:
                            i.default_value = 1
                            material.blend_method = 'BLEND'
                        else:
                            i.default_value = 0
                            material.blend_method = 'CLIP'
                        break

            elif param.attrib['Name'] == 'ColorMetalTexture':
                cm_img = load_image(self, context, param.text, materials_path, material)

            elif param.attrib['Name'] == 'NormalGlossTexture':
                ng_img = load_image(self, context, param.text, materials_path, material)

            elif param.attrib['Name'] == 'AddMapsTexture':
                add_img = load_image(self, context, param.text, materials_path, material)

            elif param.attrib['Name'] == 'AlphamaskTexture':
                am_img = load_image(self, context, param.text, materials_path, material)

            elif param.attrib['Name'] == 'Facing':
                material.seut.facing = param.text

            elif param.attrib['Name'] == 'WindScale':
                material.seut.windScale = float(param.text)

            elif param.attrib['Name'] == 'WindFrequency':
                material.seut.windFrequency = float(param.text)

        if not cm_img is None:
            cm_node.image = cm_img
            cm_node.image.alpha_mode = 'CHANNEL_PACKED'
        else:
            material.node_tree.nodes.remove(cm_node)

        if not ng_img is None:
            ng_node.image = ng_img
            ng_node.image.colorspace_settings.name = 'Non-Color'
            ng_node.image.alpha_mode = 'CHANNEL_PACKED'
        else:
            material.node_tree.nodes.remove(ng_node)

        if not add_img is None:
            add_node.image = add_img
            ng_node.image.alpha_mode = 'CHANNEL_PACKED' # TODO: This doesn't work consistently.
        else:
            material.node_tree.nodes.remove(add_node)

        if not am_img is None:
            am_node.image = am_img
            ng_node.image.alpha_mode = 'CHANNEL_PACKED' # TODO: This doesn't work consistently.
        else:
            material.node_tree.nodes.remove(am_node)

        imported.append(material.name)

    if len(not_imported) > 0:
        materials_string = ""
        for name in imported:
            if materials_string == "":
                materials_string = name
            else:
                materials_string = materials_string + ", " + name
        seut_report(self, context, 'INFO', True, 'I020', len(not_imported), materials_string)

    if len(imported) <= 0:
        seut_report(self, context, 'INFO', True, 'E041', filepath)
        return {'FINISHED'}

    else:
        materials_string = ""
        for name in imported:
            if materials_string == "":
                materials_string = name
            else:
                materials_string = materials_string + ", " + name

        seut_report(self, context, 'INFO', True, 'I019', len(imported), filepath, materials_string)
        return {'FINISHED'}


def load_image(self, context, path: str, materials_path: str, material: bpy.types.Material):
    """Returns image by first checking if it already is in Blender, if not, loading it from the given path."""

    seut_path = os.path.dirname(materials_path)
    name = os.path.splitext(os.path.basename(path))[0]

    img_path = os.path.splitext(os.path.join(seut_path, path))[0]
    for o in supported_image_types:
        if os.path.exists(f"{img_path}.{o}") or os.path.exists(f"{img_path}.{o.lower()}"):
            img_path += f".{o.lower()}"
            break

    if not os.path.exists(img_path):
        seut_report(self, context, 'WARNING', True, 'W011', img_path, material.name)
        return

    if name in bpy.data.images:
        return bpy.data.images[name]

    try:
        return bpy.data.images.load(img_path)
    except:
        seut_report(self, context, 'WARNING', True, 'W011', img_path, material.name)
        return

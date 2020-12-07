import bpy
import os
import xml.etree.ElementTree as ET

from bpy.props import StringProperty
from bpy.types import Operator

from ..materials.seut_ot_create_material    import create_material
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

        wm = context.window_manager
        preferences = get_preferences()
        materials_path = get_abs_path(preferences.materials_path)

        if materials_path == "" or os.path.isdir(materials_path) == False:
            seut_report(self, context, 'ERROR', True, 'E012', "Materials Folder", materials_path)
            return

        try:
            tree = ET.parse(self.filepath)
        except:
            print("AAAAAAAAAAAAAAAAAAAAAH")
            return

        root = tree.getroot()
        imported = []

        # check to make sure it's a material library and not a random xml file

        for mat in root:
            if mat.attrib in bpy.data.materials:
                continue

            else:
                material = create_material()
                material.name = mat.attrib

                for node in material.node_tree.nodes:
                    if node.name == 'CM':
                        cm_node = node
                    elif node.name == 'NG':
                        ng_node = node
                    if node.name == 'ADD':
                        add_node = node
                    if node.name == 'ALPHAMASK':
                        am_node = node

                cm_img = None
                ng_img = None
                add_img = None
                am_img = None

                for param in mat:
                    if param.attrib == 'Technique':
                        material.seut.technique = param.text

                    elif param.attrib == 'ColorMetalTexture':
                        cm_img = load_image(param.text, materials_path)

                    elif param.attrib == 'NormalGlossTexture':
                        ng_img = load_image(param.text, materials_path)

                    elif param.attrib == 'AddMapsTexture':
                        add_img = load_image(param.text, materials_path)

                    elif param.attrib == 'AlphamaskTexture':
                        am_img = load_image(param.text, materials_path)

                    elif param.attrib == 'Facing':
                        material.seut.facing = param.text

                    elif param.attrib == 'WindScale':
                        material.seut.windScale = param.text

                    elif param.attrib == 'WindFrequency':
                        material.seut.windFrequency = param.text

                # Error for textures not having been able to be loaded, delete mat after

                # Error if textures are incompatible DDS format (via splitext)
                

                if cm_img != False and cm_img != None:
                    cm_node.image = cm_img
                elif cm_img == None:
                    material.node_tree.nodes.remove(cm_node)

                if ng_img != False and ng_img != None:
                    ng_node.image = ng_img
                elif ng_img == None:
                    material.node_tree.nodes.remove(ng_node)

                if add_img != False and add_img != None:
                    add_node.image = add_img
                elif add_img == None:
                    material.node_tree.nodes.remove(add_node)

                if am_img != False and am_img != None:
                    am_node.image = am_img
                elif am_img == None:
                    material.node_tree.nodes.remove(am_node)
                
                imported.append(material.name)
                

        materials_string = ""
        for name in imported:
            if materials_string == "":
                materials_string = name
            else:
                materials_string = materials_string + ", " + name

        seut_report(self, context, 'INFO', True, 'I019', len(imported), self.filepath, materials_string)

        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def load_image(path: str, materials_path: str):
    """Returns image by first checking if it already is in Blender, if not, loading it from the given path."""

    name = os.path.splitext(os.path.basename(path))
    name_split = os.path.splitext(name)[0]

    if name in bpy.data.images:
        return bpy.data.images[name]

    elif name_split in bpy.data.images:
        return bpy.data.images[name_split]
        
    else:
        try:
            return bpy.data.images.load(path) # need to properly join materials path with this
        except:
            return False

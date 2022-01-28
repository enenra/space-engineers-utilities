import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types  import Operator

from .seut_export_utils import create_mat_entry, format_xml
from ..seut_errors      import seut_report, get_abs_path


class SEUT_OT_ExportMaterials(Operator):
    """Export local materials to XML library file"""
    bl_idname = "scene.export_materials"
    bl_label = "Export Materials"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        counter = 0
        for mat in bpy.data.materials:
            if mat.library is None and mat.asset_data is not None and not mat.name.startswith('SMAT_'):
                counter += 1
        
        if not counter > 0:
            Operator.poll_message_set("No materials marked as assets available in BLEND file")

        return counter > 0


    def execute(self, context):
        
        if not bpy.data.is_saved:
            seut_report(self, context, 'ERROR', True, 'E008')
            return {'FILE_NOT_SAVED'}

        return export_materials(self, context)

    
def export_materials(self, context):
    """Export local materials to XML file"""
    
    offset = bpy.path.basename(bpy.context.blend_data.filepath).find(".blend")
    filename = bpy.path.basename(bpy.context.blend_data.filepath)[:offset]
    
    # This culls the MatLb_ from the filename
    filename = filename.replace("MatLib_", "")

    materials = ET.Element('MaterialsLib')
    materials.set('Name', filename)

    for mat in bpy.data.materials:
        if mat.library is None and mat.asset_data is not None:
            create_mat_entry(self, context, materials, mat)
                
    # Create file with subtypename + collection name and write string to it
    xml_formatted = format_xml(self, context, materials)
    
    exported_xml = open(bpy.path.abspath('//') + filename + ".xml", "w")
    exported_xml.write(xml_formatted)

    seut_report(self, context, 'INFO', True, 'I004', bpy.path.abspath('//') + filename + ".xml")

    return {'FINISHED'}

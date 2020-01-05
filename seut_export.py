import bpy
import xml.etree.ElementTree as ET
import xml.dom.minidom

from .seut_export_exportMain        import SEUT_OT_ExportMain
from .seut_export_exportBS          import SEUT_OT_ExportBS
from .seut_export_exportLOD         import SEUT_OT_ExportLOD
from .seut_export_exportHKT         import SEUT_OT_ExportHKT

class SEUT_OT_Export(bpy.types.Operator):
    """Exports shit."""
    bl_idname = "object.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}


    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH"
        )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):

        # Debug
        print('OT: Export')

        # Call all the individual export opeartors
        SEUT_OT_ExportMain.export_Main(context)
        SEUT_OT_ExportBS.export_BS(context)
        SEUT_OT_ExportLOD.export_LOD(context)
        SEUT_OT_ExportHKT.export_HKT(context)

        return {'FINISHED'}


    def export_XML(context, collection, filepath):
        """Exports the XML file for a defined collection"""
        
        # analyze what collection type it is by looking at its name

        # create string and add initial nodes

        # set up LOD nodes, depending on what type of collection it is and what LOD collections have children

        # iterate through all materials of all objects within the collection and create nodes for them

        # if the material is not a linked material, create material instead of materialref
        # will need to iterate through the image textures of the selected material
        # ========== TODO ==========
        # add support for those custom material paremeters?

        # Create file with subtypename + collection name and write string to it
        # Always create on blend file location?

        return

    
    def export_FBX(context, collection, filepath):
        """Exports the FBX file for a defined collection"""

        # Copy dummies over if not present as safety? to LOD1 for sure, but are they needed in LOD2?

        # What happens if there's multiple objects in the collection? Can I input a collection into the export operator?

        return

    
    def export_SBC(context, filepath):
        """Exports the SBC file for a defined collection"""

        # Pull info together and create nodes

        # Write to file, place in export folder

        return
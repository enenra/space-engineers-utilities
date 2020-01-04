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

    def execute(self, context):

        # Debug
        print('OT: Export')

        # Call all the individual export opeartors
        SEUT_OT_ExportMain.export_Main(context)
        SEUT_OT_ExportBS.export_BS(context)
        SEUT_OT_ExportLOD.export_LOD(context)
        SEUT_OT_ExportHKT.export_HKT(context)

        return {'FINISHED'}

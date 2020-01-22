import bpy
import os
import glob
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator

from .seut_ot_exportMain             import SEUT_OT_ExportMain
from .seut_ot_exportBS               import SEUT_OT_ExportBS
from .seut_ot_exportHKT              import SEUT_OT_ExportHKT
from .seut_ot_exportLOD              import SEUT_OT_ExportLOD
from .seut_ot_exportMWM              import SEUT_OT_ExportMWM
from .seut_ot_exportSBC              import SEUT_OT_ExportSBC
from ..seut_ot_recreateCollections   import SEUT_OT_RecreateCollections

class SEUT_OT_Export(Operator):
    """Exports all enabled file types and collections"""
    bl_idname = "object.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.get_Collections()
        return collections['main'] is not None

    def execute(self, context):

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export'")
        
        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        exportPath = os.path.normpath(bpy.path.abspath(scene.seut.export_exportPath))

        if preferences.looseFilesExportFolder == '1' and scene.seut.export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            print("SEUT Error: No export folder defined. (003)")
        elif preferences.looseFilesExportFolder == '1' and os.path.exists(exportPath) == False:
            self.report({'ERROR'}, "SEUT: Export path '%s' doesn't exist. (003)" % (exportPath))
            print("SEUT Error: Export path '" + exportPath + "' doesn't exist. (003)")
            return {'CANCELLED'}

        if scene.seut.export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export path '%s' does not contain 'Models\\'. Cannot be transformed into relative path. (014)" % (exportPath))
            print("SEUT Error: Export path '" + exportPath + "' does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.seut.subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            print("SEUT Error: No SubtypeId set. (004)")
            return {'CANCELLED'}
        
        # Call all the individual export operators
        SEUT_OT_ExportMain.export_Main(self, context, True)
        SEUT_OT_ExportBS.export_BS(self, context, True)
        SEUT_OT_ExportLOD.export_LOD(self, context, True)

        # HKT and SBC export are the only two filetypes those operators handle so I check for enabled here.
        if scene.seut.export_hkt:
            SEUT_OT_ExportHKT.export_HKT(self, context, True)

        if scene.seut.export_sbc:
            SEUT_OT_ExportSBC.export_SBC(self, context)
        
        # Finally, compile everything to MWM
        SEUT_OT_ExportMWM.export_MWM(self, context)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export'")

        return {'FINISHED'}

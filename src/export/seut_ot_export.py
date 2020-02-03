import bpy
import os
import glob
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator

from .seut_ot_exportMain            import SEUT_OT_ExportMain
from .seut_ot_exportBS              import SEUT_OT_ExportBS
from .seut_ot_exportHKT             import SEUT_OT_ExportHKT
from .seut_ot_exportLOD             import SEUT_OT_ExportLOD
from .seut_ot_exportMWM             import SEUT_OT_ExportMWM
from .seut_ot_exportSBC             import SEUT_OT_ExportSBC
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral

class SEUT_OT_Export(Operator):
    """Exports all collections in the current scene and compresses them to MWM"""
    bl_idname = "scene.export"
    bl_label = "Export Current Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'scene.export'")
        
        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)

        # If mode is not object mode, export fails horribly.
        if bpy.context.object is not None and bpy.context.object.mode is not 'OBJECT':
            currentMode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == 'CONTINUE':
            return {result}
        
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
        
        # Reset interaction mode
        if bpy.context.object is not None:
            bpy.ops.object.mode_set(mode=currentMode)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'scene.export'")

        return {'FINISHED'}

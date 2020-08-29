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
from ..seut_preferences             import get_addon_version
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral

class SEUT_OT_Export(Operator):
    """Exports all collections in the current scene and compresses them to MWM"""
    bl_idname = "scene.export"
    bl_label = "Export Current Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        print("\n============================================================ Exporting Scene '" + scene.name + "' with SEUT " + str(get_addon_version()) + ".")

        # If mode is not object mode, export fails horribly.
        currentArea = context.area.type
        context.area.type = 'VIEW_3D'
        if context.object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
            context.object.select_set(False)
            context.view_layer.objects.active = None

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        # Character animations need at least one keyframe
        if scene.seut.sceneType == 'character_animation' and len(scene.timeline_markers) <= 0:
            scene.timeline_markers.new('F_00', frame=0)
        
        # This exports to large grid, if selected, but also exports character-type scenes
        if scene.seut.export_largeGrid or scene.seut.sceneType == 'character_animation' or scene.seut.sceneType == 'character':
            
            if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
                subtypeId = str(scene.seut.subtypeId)
                if scene.seut.subtypeId.find("_SG_") != -1:
                    scene.seut.subtypeId = scene.seut.subtypeId.replace("_SG_", "_LG_")

                elif scene.seut.subtypeId[:3] == "SG_":
                    scene.seut.subtypeId = scene.seut.subtypeId.replace("SG_", "LG_")

                elif scene.seut.subtypeId[:3] == "LG_":
                    pass

                elif scene.seut.subtypeId.find("_LG_") == -1:
                    scene.seut.subtypeId = "LG_" + scene.seut.subtypeId

            gridScale = str(scene.seut.gridScale)
            scene.seut.gridScale = 'large'

            # Set rescaleFactor only if grid wasn't previously large already (in which case the assumption is that it was modelled on a large grid and already the right size)
            rescaleFactor = int(scene.seut.export_rescaleFactor)
            if gridScale == 'small':
                scene.seut.export_rescaleFactor = 5.0
            else:
                scene.seut.export_rescaleFactor = 1.0

            exportPath = scene.seut.export_exportPath
            if scene.seut.export_exportPath.find("/small/") != -1:
                scene.seut.export_exportPath = scene.seut.export_exportPath.replace("/small/", "/large/")
            

            # Call all the individual export operators
            SEUT_OT_ExportBS.export_BS(self, context, True)
            SEUT_OT_ExportLOD.export_LOD(self, context, True)
            result_main = SEUT_OT_ExportMain.export_Main(self, context, True)

            # HKT and SBC export are the only two filetypes those operators handle so I check for enabled here.
            SEUT_OT_ExportHKT.export_HKT(self, context, True)

            if scene.seut.export_sbc:
                SEUT_OT_ExportSBC.export_SBC(self, context)
            
            # Finally, compile everything to MWM
            if result_main == {'FINISHED'}:
                SEUT_OT_ExportMWM.export_MWM(self, context)

            # Resetting the variables
            if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
                scene.seut.subtypeId = subtypeId
                scene.seut.gridScale = gridScale
                scene.seut.export_rescaleFactor = rescaleFactor
                scene.seut.export_exportPath = exportPath
        
        # This exports to large grid, if selected, but also exports character-type scenes
        if scene.seut.export_smallGrid:

            if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
                subtypeId = str(scene.seut.subtypeId)
                if scene.seut.subtypeId.find("_LG_") != -1:
                    scene.seut.subtypeId = scene.seut.subtypeId.replace("_LG_", "_SG_")

                elif scene.seut.subtypeId[:3] == "LG_":
                    scene.seut.subtypeId = scene.seut.subtypeId.replace("LG_", "SG_")

                elif scene.seut.subtypeId[:3] == "SG_":
                    pass
                
                elif scene.seut.subtypeId.find("_SG_") == -1:
                    scene.seut.subtypeId = "SG_" + scene.seut.subtypeId

            gridScale = str(scene.seut.gridScale)
            scene.seut.gridScale = 'small'

            # Set rescaleFactor only if grid wasn't previously small already (in which case the assumption is that it was modelled on a small grid and already the right size)
            rescaleFactor = int(scene.seut.export_rescaleFactor)
            if gridScale == 'large':
                scene.seut.export_rescaleFactor = 0.2
            else:
                scene.seut.export_rescaleFactor = 1.0

            exportPath = scene.seut.export_exportPath
            if scene.seut.export_exportPath.find("/large/") != -1:
                scene.seut.export_exportPath = scene.seut.export_exportPath.replace("/large/", "/small/")
            

            # Call all the individual export operators
            SEUT_OT_ExportBS.export_BS(self, context, True)
            SEUT_OT_ExportLOD.export_LOD(self, context, True)
            result_main = SEUT_OT_ExportMain.export_Main(self, context, True)

            # HKT and SBC export are the only two filetypes those operators handle so I check for enabled here.
            SEUT_OT_ExportHKT.export_HKT(self, context, True)

            if scene.seut.export_sbc:
                SEUT_OT_ExportSBC.export_SBC(self, context)
            
            # Finally, compile everything to MWM
            if result_main == {'FINISHED'}:
                SEUT_OT_ExportMWM.export_MWM(self, context)

            # Resetting the variables
            if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
                scene.seut.subtypeId = subtypeId
                scene.seut.gridScale = gridScale
                scene.seut.export_rescaleFactor = rescaleFactor
                scene.seut.export_exportPath = exportPath
            
        context.area.type = currentArea

        return {'FINISHED'}

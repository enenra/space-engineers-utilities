import bpy
import os

from os.path    import join
from bpy.types  import Operator

from .seut_mwmbuilder               import mwmbuilder
from .seut_export_utils             import ExportSettings, delete_loose_files
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral

class SEUT_OT_ExportMWM(Operator):
    """Compiles the MWM from the previously exported loose files"""
    bl_idname = "object.export_mwm"
    bl_label = "Compile MWM"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Compiles all loose files into a MWM"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_main'")

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == 'CONTINUE':
            return {result}

        SEUT_OT_ExportMWM.export_MWM(self, context)
                
        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_mwm'")

        return {'FINISHED'}

    def export_MWM(self, context):
        """Compiles all loose files into a MWM"""
        
        scene = context.scene
        depsgraph = None
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        settings = ExportSettings(scene, depsgraph)
        mwmbPath = os.path.normpath(bpy.path.abspath(preferences.mwmbPath))
        materialsPath = os.path.normpath(bpy.path.abspath(preferences.materialsPath))
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)

        if preferences.mwmbPath == "" or os.path.exists(mwmbPath) == False:
            self.report({'ERROR'}, "SEUT: Path to MWM Builder '%s' not valid. (018)" % (mwmbPath))
            print("SEUT Info: Path to MWM Builder '" + mwmbPath + "' not valid. (018)")
            return {'CANCELLED'}

        if preferences.materialsPath == "" or os.path.exists(materialsPath) == False:
            self.report({'ERROR'}, "SEUT: Path to Materials Folder '%s' not valid. (017)" % (materialsPath))
            print("SEUT Info: Path to Materials Folder '" + materialsPath + "' not valid. (017)")
            return {'CANCELLED'}

        if preferences.looseFilesExportFolder == '0':
            path = os.path.dirname(bpy.data.filepath) + "\\"
        elif preferences.looseFilesExportFolder == '1':
            path = bpy.path.abspath(scene.seut.export_exportPath)
            
        mwmpath = bpy.path.abspath(scene.seut.export_exportPath)
        mwmfile = join(mwmpath, scene.seut.subtypeId + ".mwm")
        materialspath = bpy.path.abspath(preferences.materialsPath)

        try:
            mwmbuilder(self, context, path, settings, mwmfile, materialspath)
        finally:
            if scene.seut.export_deleteLooseFiles:
                delete_loose_files(path)
                
        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_mwm'")

        return {'FINISHED'}
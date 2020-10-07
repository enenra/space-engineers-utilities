import bpy
import os

from os.path    import join
from bpy.types  import Operator

from .seut_mwmbuilder               import mwmbuilder
from .seut_export_utils             import ExportSettings, delete_loose_files
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import check_export, check_toolpath, report_error

class SEUT_OT_ExportMWM(Operator):
    """Compiles the MWM from the previously exported loose files"""
    bl_idname = "object.export_mwm"
    bl_label = "Compile MWM"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Compiles all loose files into a MWM"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = SEUT_OT_ExportMWM.export_MWM(self, context)

        return result

    def export_MWM(self, context):
        """Compiles all loose files into a MWM"""
        
        scene = context.scene
        depsgraph = None
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        settings = ExportSettings(scene, depsgraph)
        mwmbPath = os.path.abspath(bpy.path.abspath(preferences.mwmbPath))
        materialsPath = os.path.abspath(bpy.path.abspath(preferences.materialsPath))
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        result = check_toolpath(self, context, mwmbPath, "MWM Builder", "MwmBuilder.exe")
        if not result == {'CONTINUE'}:
            return result

        if preferences.materialsPath == "" or preferences.materialsPath == "." or os.path.isdir(materialsPath) == False:
            report_error(self, context, True, 'E012', "Materials Folder", materialsPath)
            return {'CANCELLED'}

        path = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath)) + "\\"
            
        mwmpath = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath)) + "\\"
        mwmfile = join(mwmpath, scene.seut.subtypeId + ".mwm")
        materialspath = bpy.path.abspath(preferences.materialsPath)
        
        try:
            mwmbuilder(self, context, path, mwmpath, settings, mwmfile, materialspath)
        finally:
            if scene.seut.export_deleteLooseFiles:
                delete_loose_files(path)

        return {'FINISHED'}
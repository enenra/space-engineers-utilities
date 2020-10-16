import bpy
import os

from os.path    import join
from bpy.types  import Operator

from .seut_mwmbuilder               import mwmbuilder
from .seut_export_utils             import ExportSettings, delete_loose_files
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_toolpath, seut_report, get_abs_path


class SEUT_OT_ExportMWM(Operator):
    """Compiles to MWM from the previously exported temp files"""
    bl_idname = "object.export_mwm"
    bl_label = "Compile MWM"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Calls the function to compile to MWM"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = export_mwm(self, context)

        return result


def export_mwm(self, context):
    """Compiles to MWM from the previously exported temp files"""
    
    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()
    path = get_abs_path(scene.seut.export_exportPath) + "\\"
    materials_path = get_abs_path(preferences.materialsPath)
    settings = ExportSettings(scene, None)

    # Check for availability of MWM Builder
    result = check_toolpath(self, context, preferences.mwmbPath, "MWM Builder", "MwmBuilder.exe")
    if not result == {'CONTINUE'}:
        return result

    # Check materials path
    if materials_path == "" or os.path.isdir(materials_path) == False:
        seut_report(self, context, 'ERROR', True, 'E012', "Materials Folder", materials_path)
        return {'CANCELLED'}
        
    mwmfile = join(path, scene.seut.subtypeId + ".mwm")
    
    try:
        mwmbuilder(self, context, path, path, settings, mwmfile, materials_path)
    finally:
        if scene.seut.export_deleteLooseFiles:
            delete_loose_files(path)

    return {'FINISHED'}
import bpy
import os

from os.path                        import join
from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_ot_export                import ExportSettings, delete_loose_files
from .seut_mwmbuilder               import mwmbuilder

class SEUT_OT_ExportMWM(Operator):
    """Compiles the MWM from the previously exported loose files"""
    bl_idname = "object.export_mwm"
    bl_label = "Compile MWM"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Compiles all loose files into a MWM"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_main'")

        scene = context.scene
        depsgraph = None
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        settings = ExportSettings(scene, depsgraph)
        mwmbPath = os.path.normpath(bpy.path.abspath(preferences.pref_mwmbPath))
        materialsPath = os.path.normpath(bpy.path.abspath(preferences.pref_materialsPath))

        if preferences.pref_mwmbPath == "" or os.path.exists(mwmbPath) == False:
            self.report({'ERROR'}, "SEUT: Path to MWM Builder '%s' not valid. (018)" % (mwmbPath))
            print("SEUT Info: Path to MWM Builder '" + mwmbPath + "' not valid. (018)")
            return {'CANCELLED'}

        if preferences.pref_materialsPath == "" or os.path.exists(materialsPath) == False:
            self.report({'ERROR'}, "SEUT: Path to Materials Folder '%s' not valid. (017)" % (materialsPath))
            print("SEUT Info: Path to Materials Folder '" + materialsPath + "' not valid. (017)")
            return {'CANCELLED'}

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            print("SEUT Info: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return {'CANCELLED'}
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)
            
            mwmpath = bpy.path.abspath(scene.prop_export_exportPath)

        mwmfile = join(mwmpath, scene.prop_subtypeId + ".mwm")
        materialspath = bpy.path.abspath(preferences.pref_materialsPath)

        try:
            mwmbuilder(self, context, path, settings, mwmfile, materialspath)
        finally:
            if scene.prop_export_deleteLooseFiles:
                delete_loose_files(path)
                
        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_mwm'")

        return {'FINISHED'}
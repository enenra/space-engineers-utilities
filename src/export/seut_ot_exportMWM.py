import bpy
import os

from os.path    import join
from bpy.types  import Operator

from .seut_mwmbuilder                import mwmbuilder
from ..seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from ..seut_utils                    import ExportSettings, delete_loose_files

class SEUT_OT_ExportMWM(Operator):
    """Compiles the MWM from the previously exported loose files"""
    bl_idname = "object.export_mwm"
    bl_label = "Compile MWM"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Compiles all loose files into a MWM"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_main'")
        
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

        SEUT_OT_ExportMWM.export_MWM(self, context)
                
        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_mwm'")

        return {'FINISHED'}

    def export_MWM(self, context):
        """Compiles all loose files into a MWM"""
        
        scene = context.scene
        depsgraph = None
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        settings = ExportSettings(scene, depsgraph)
        mwmbPath = os.path.normpath(bpy.path.abspath(preferences.mwmbPath))
        materialsPath = os.path.normpath(bpy.path.abspath(preferences.materialsPath))

        if preferences.mwmbPath == "" or os.path.exists(mwmbPath) == False:
            self.report({'ERROR'}, "SEUT: Path to MWM Builder '%s' not valid. (018)" % (mwmbPath))
            print("SEUT Info: Path to MWM Builder '" + mwmbPath + "' not valid. (018)")
            return {'CANCELLED'}

        if preferences.materialsPath == "" or os.path.exists(materialsPath) == False:
            self.report({'ERROR'}, "SEUT: Path to Materials Folder '%s' not valid. (017)" % (materialsPath))
            print("SEUT Info: Path to Materials Folder '" + materialsPath + "' not valid. (017)")
            return {'CANCELLED'}

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            print("SEUT Info: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return {'CANCELLED'}
        else:
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
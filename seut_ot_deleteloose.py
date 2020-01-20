import bpy
import os

from bpy.types                      import Operator
from os.path                        import join
from .seut_ot_export                import delete_loose_files


class SEUT_OT_DeleteLoose(Operator):
    """Delete all loose files"""
    bl_idname = "object.deleteloose"
    bl_label = "Delete Loose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return {'CANCELLED'}
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)
            
        fbxfile = join(path, scene.prop_subtypeId + ".fbx")
        havokfile = join(path, scene.prop_subtypeId + ".hkt")
        paramsfile = join(path, scene.prop_subtypeId + ".xml")
        
        delete_loose_files(fbxfile, havokfile, paramsfile)

        return {'FINISHED'}
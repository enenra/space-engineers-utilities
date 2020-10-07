import bpy

from bpy.types      import Operator

from ..seut_errors                  import check_export


class SEUT_OT_CopyExportFolder(Operator):
    """Copies the export folder of the current scene to all other scenes"""
    bl_idname = "scene.copy_export_folder"
    bl_label = "Copy Export Folder"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        for scn in bpy.data.scenes:
            scn.seut.export_exportPath = scene.seut.export_exportPath
        
        self.report({'INFO'}, "SEUT: Export Folder path '%s' successfully copied to all scenes." % (scene.seut.export_exportPath))

        return {'FINISHED'}
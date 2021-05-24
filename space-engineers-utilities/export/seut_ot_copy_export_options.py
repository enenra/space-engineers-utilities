import bpy

from bpy.types  import Operator

from ..seut_errors  import check_export, seut_report


class SEUT_OT_CopyExportOptions(Operator):
    """Copies the export options of the current scene to all other scenes"""
    bl_idname = "scene.copy_export_options"
    bl_label = "Copy Export Options"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        for scn in bpy.data.scenes:
            scn.seut.export_deleteLooseFiles = scene.seut.export_deleteLooseFiles
            scn.seut.export_largeGrid = scene.seut.export_largeGrid
            scn.seut.export_smallGrid = scene.seut.export_smallGrid
            scn.seut.export_medium_grid = scene.seut.export_medium_grid
            scn.seut.export_sbc = scene.seut.export_sbc
            scn.seut.mod_path = scene.seut.mod_path
            scn.seut.export_exportPath = scene.seut.export_exportPath
        
        seut_report(self, context, 'INFO', True, 'I006', "Export")

        return {'FINISHED'}
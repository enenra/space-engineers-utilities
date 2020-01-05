import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_ExportSBC(bpy.types.Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export SBC"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the SBC file for a defined collection"""

        # Debug
        print('OT: ExportSBC')

        scene = context.scene

        collections = SEUT_OT_RecreateCollections.get_Collections()

        # Pull info together and create nodes

        # Write to file, place in export folder

        return {'FINISHED'}
import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_ExportHKT(bpy.types.Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports collision to HKT"""

        # Debug
        print('OT: ExportHKT')

        return {'FINISHED'}
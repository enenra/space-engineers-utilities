import bpy

from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_ExportHKT(bpy.types.Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports collision to HKT"""

        scene = context.scene

        collections = SEUT_OT_RecreateCollections.get_Collections()

        # Debug
        self.report({'DEBUG'}, "SEUT: OT Export HKT executed.")

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        return {'FINISHED'}
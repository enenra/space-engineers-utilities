import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections

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
        print('OT: ExportHKT')

        # If no SubtypeId is set, error out.
        if scene.prop_subtypeId == "":
            print("SEUT Error 004: No SubtypeId set.")
            return {'CANCELLED'}

        return {'FINISHED'}
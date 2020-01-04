import bpy

class SEUT_OT_RecreateCollections(bpy.types.Operator):
    """Recreates the collections."""
    bl_idname = "object.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        # Debug
        print('OP: Recreate Collections')

        return {'FINISHED'}
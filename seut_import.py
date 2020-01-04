import bpy


class SEUT_OT_Import(bpy.types.Operator):
    """Import FBX files and remap materials."""
    bl_idname = "object.import"
    bl_label = "Import FBX"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Debug
        print('OT: Import')

        # First import FBX
        
        # Then run material remap

        return {'FINISHED'}

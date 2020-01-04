import bpy

class SEUT_OT_ExportMain(bpy.types.Operator):
    """Exports the main model."""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        # Debug
        print('OT: ExportMain')

        return {'FINISHED'}
    

    def export_Main(context, target):

        # a
        
        return
        
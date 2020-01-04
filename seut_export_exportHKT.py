import bpy

class SEUT_OT_ExportHKT(bpy.types.Operator):
    """Exports the HKT."""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        # Debug
        print('OT: ExportHKT')

        return {'FINISHED'}
    

    def export_HKT(context, target):

        # a
        
        return
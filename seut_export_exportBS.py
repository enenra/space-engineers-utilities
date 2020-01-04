import bpy

class SEUT_OT_ExportBS(bpy.types.Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_bs"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        # Debug
        print('OT: ExportBS')

        return {'FINISHED'}
    

    def export_BS(context):

        # Needs to check properties as to whether to export FBX and XML
        
        return
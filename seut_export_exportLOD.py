import bpy

class SEUT_OT_ExportLOD(bpy.types.Operator):
    """Exports all LODs."""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        # Debug
        print('OT: ExportLOD')

        return {'FINISHED'}
    

    def export_LOD(context):

        # Needs to check properties as to whether to export FBX and XML
        
        return
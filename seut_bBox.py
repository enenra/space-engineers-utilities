import bpy

class SEUT_OT_BBox(bpy.types.Operator):
    """Sets the bounding box."""
    bl_idname = "object.bbox"
    bl_label = "Bounding Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):


        return {'FINISHED'}

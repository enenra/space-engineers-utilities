import bpy

class SEUT_OT_BBox(bpy.types.Operator):
    """Sets the bounding box."""
    bl_idname = "object.bbox"
    bl_label = "Bounding Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        print('OT: Bounding Box')

        # Needs to pull in properties regarding size and on/off

        # If operator was triggered with button, determine size of object and adjust the bounding box to its size, but scaled up to multiples of grid scale * 2
        # this may require separating the functionality into a separate function that is then called by update in init as well as execute here

        # Then call draw function with those properties

        return {'FINISHED'}

    def draw(self,context):

        # Draw stuff here according to the tutorial video

        return
import bpy
import bgl
import gpu

from gpu_extras.batch   import batch_for_shader
from bpy.types          import Operator

class SEUT_OT_BBoxAuto(Operator):
    """Sets the bounding box automatically"""
    bl_idname = "object.bbox_auto"
    bl_label = "Bounding Box Automatic"
    bl_options = {'REGISTER', 'UNDO'}
    
    # This is what is executed if "Automatic" is pressed.
    def execute(self, context):

        scene = context.scene

        print("SEUT Debug: BBox Operator used. State: " + scene.prop_bBoxToggle)

        # If the toggle is off, don't do anything.
        if scene.prop_bBoxToggle == 'off':
            return {'CANCELLED'}

        # Calculate max bounding box of all objects in main collection

        # Then get nearest block-compatible bounding box x/y/z and set scene.prop_'s to those values
        
        """
        scene.prop_bBox_X = x
        scene.prop_bBox_Y = y
        scene.prop_bBox_Z = z

        bpy.ops.object.bbox('INVOKE_DEFAULT')
        """

        return {'FINISHED'}
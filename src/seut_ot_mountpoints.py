import bpy

from bpy.types import Operator

class SEUT_OT_Mountpoints(Operator):
    """Handles everything related to mountpoint functionality"""
    bl_idname = "scene.mountpoints"
    bl_label = "Mountpoints"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.mountpointToggle == 'on':
            if scene.seut.mirroringToggle == 'on':
                scene.seut.mirroringToggle = 'off'
            result = SEUT_OT_Mountpoints.mountpointSetup(self, context)

        elif scene.seut.mountpointToggle == 'off':
            result = SEUT_OT_Mountpoints.cleanMountpointSetup(self, context)

        return result
    

    def mountpointSetup(self, context):

        scene = context.scene

        # Check if entries for sides exist. If not, add them.

        # Check if entries for blocks exist. Compare to bounding box. Cull and add.

        # Check if entries for squares exist. If not, add them.

        # Create collection

        # Create empty tree for sides and blocks

        # Add the planes to the empties

        # Start the loop to check for selection

        return {'FINISHED'}
    

    def cleanMountpointSetup(self, context):

        scene = context.scene

        # stop the loop

        # delete planes

        # delete empties

        # delete collection

        return {'FINISHED'}
    

    def toggleSquare(self, context, square):

        scene = context.scene

        # Change plane material

        # Change square bool

        return {'FINISHED'}
import bpy

from bpy.types import Operator


class SEUT_OT_Mirroring(Operator):
    """Handles setup of mirroring options"""
    bl_idname = "scene.mirroring"
    bl_label = "Mirroring"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        SEUT_OT_Mirroring.mirroringSetup(self, context)

        return {'FINISHED'}
    

    def mirroringSetup(self, context):
        """Sets up mirroring utilities"""

        scene = context.scene

        # Create collection if it doesn't exist already

        # Create empties

        # Instance main collection or mirroringScene main collection under empties

        return
    

    def cleanMirroringSetup(self, context):
        """Cleans up mirroring utilities"""

        scene = context.scene

        # Purge empty children

        # Delete empties

        # Delete collection


        return


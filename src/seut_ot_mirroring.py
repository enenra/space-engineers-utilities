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

        # Create empties (using property rotation info) in distance from origin that is relative

        # Instance main collection or mirroringScene main collection under empties

        return
    

    def cleanMirroringSetup(self, context):
        """Cleans up mirroring utilities"""

        scene = context.scene

        # Save empty rotation values to properties
        SEUT_OT_Mirroring.saveRotationToProps(self, context, empty)

        # Purge empty children

        # Delete empties

        # Delete collection

        return
    
    def saveRotationToProps(self, context, empty):
        """Saves the current rotation values of an empty to the scene properties"""

        scene = context.scene

        return


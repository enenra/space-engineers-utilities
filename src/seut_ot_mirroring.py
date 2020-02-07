import bpy

from bpy.types import Operator

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorCollection


class SEUT_OT_Mirroring(Operator):
    """Handles setup of mirroring options"""
    bl_idname = "scene.mirroring"
    bl_label = "Mirroring"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.mirroringToggle == 'on':
            SEUT_OT_Mirroring.mirroringSetup(self, context)

        elif scene.seut.mirroringToggle == 'off':
            SEUT_OT_Mirroring.cleanMirroringSetup(self, context)

        return {'FINISHED'}
    

    def mirroringSetup(self, context):
        """Sets up mirroring utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)
        tag = ' (' + scene.seut.subtypeId + ')'

        result = errorCollection(self, context, collections['seut'], False)
        if not result == 'CONTINUE':
            return {result}

        # Create collection if it doesn't exist already
        if bpy.data.collections['Mirroring' + tag] is None:
            collection = bpy.data.collections.new('Mirroring' + tag)
            collections['seut'].children.link(collection)
        else:
            collection = bpy.data.collections['Mirroring' + tag]
            try:
                collections['seut'].children.link(collection)
            except:
                pass

        # Create empties (using property rotation info) with certain distance from bounding box

        # Instance main collection or mirroringScene main collection under empties

        return {'FINISHED'}
    

    def cleanMirroringSetup(self, context):
        """Cleans up mirroring utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)

        # Save empty rotation values to properties
        SEUT_OT_Mirroring.saveRotationToProps(self, context, empty)

        # Purge empty children

        # Delete empties

        # Delete collection

        return {'FINISHED'}
    
    def saveRotationToProps(self, context, empty):
        """Saves the current rotation values of an empty to the scene properties"""

        scene = context.scene

        return


import bpy

from bpy.types import Operator

class SEUT_OT_StructureConversion(Operator):
    """Ports blend files created with the old plugin to the new structure"""
    bl_idname = "object.structure_conversion"
    bl_label = "Convert to new structure"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        SEUT_OT_StructureConversion.convertToNewStructure(self, context)

        return {'FINISHED'}
    
    def convertToNewStructure(self, context):
        """Converts blend files created with the old plugin to the new structure"""

        print("I work!")

        # Set subtypeId from scene name

        # port subparts in scenes to new layout

        # convert collections created from layers to corresponding SEUT collections

        # convert LOD distances? and other variables

        # how to handle custom materials?

        return
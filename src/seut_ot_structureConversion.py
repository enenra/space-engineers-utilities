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

        scene = context.scene

        # Set scene indexes and SubtypeIds
        for index in range(0, len(bpy.data.scenes)):
            if bpy.data.scenes[index].seut.index == -1:
                bpy.data.scenes[index].seut.index = index
                bpy.data.scenes[index].seut.subtypeId = bpy.data.scenes[index].name

                # For not active scenes, the update doesn't trigger apparently, so I have to add the index to the scene names manually.
                if index > 0:
                    bpy.data.scenes[index].name = bpy.data.scenes[index].name + ' (' + str(index) + ')'

        # port subparts in scenes to new layout

        # convert collections created from layers to corresponding SEUT collections

        # convert LOD distances? and other variables

        # how to handle custom materials?

        return
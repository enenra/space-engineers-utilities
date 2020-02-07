import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

class SEUT_OT_MatCreate(Operator):
    """Create a SEUT material from the defined preset"""
    bl_idname = "object.mat_create"
    bl_label = "Create Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        scene = context.scene

        presetName = scene.seut.matPreset
        
        # Find SMAT to pull preset from.
        presetMat = None

        for mat in bpy.data.materials:
            if mat.name == presetName:
                presetMat = mat
        
        if presetMat == None:
            self.report({'ERROR'}, "SEUT: Cannot find preset '%s' source material. Node Tree cannot be created. Re-link 'MatLib_Presets.blend'! (016)" % (presetName))
            return {'CANCELLED'}
            
        newMat = presetMat.copy()
        newMat.name = "SEUT Material"

        context.active_object.active_material = newMat

        return {'FINISHED'}
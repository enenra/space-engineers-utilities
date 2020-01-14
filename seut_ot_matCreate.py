import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

class SEUT_OT_MatCreate(Operator):
    """Create a SMAT material"""
    bl_idname = "object.mat_create"
    bl_label = "Add Node Tree"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        
        scene = context.scene

        print(scene.prop_matPreset)

        if scene.prop_matPreset == 'SMAT_Full': print("yay")
        if scene.prop_matPreset == 'SMAT_Full_NoEmissive': print("nay")

        return {'FINISHED'}
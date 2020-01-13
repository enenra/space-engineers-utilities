import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

class SEUT_OT_MatCreate(Operator):
    """Create a SMAT material"""
    bl_idname = "object.mat_create"
    bl_label = "Create SEUT Material"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    smatPreset: EnumProperty(
        name='SMAT Preset',
        items=(
            ('SMAT_Full', 'Full', ''),
            ('SMAT_Full_NoEmissive', 'No Emissive', '')
            ),
        default='SMAT_Full'
    )


    def execute(self, context):
        
        scene = context.scene

        print(self.smatPreset)

        if self.smatPreset == 'SMAT_Full': print("yay")
        if self.smatPreset == 'SMAT_Full_NoEmissive': print("nay")

        return {'FINISHED'}
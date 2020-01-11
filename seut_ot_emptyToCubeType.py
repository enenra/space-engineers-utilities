import bpy

from bpy.types import Operator

class SEUT_OT_EmptiesToCubeType(Operator):
    """Changes display type of selected empties to 'Cube'"""
    bl_idname = "object.emptytocubetype"
    bl_label = "Display Empties as 'Cube'"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def execute(self, context):
        """Changes display type of selected empties to 'Cube'"""

        for obj in bpy.context.view_layer.objects.selected:
            if obj.type == "EMPTY":
                obj.empty_display_type = "CUBE"
        
        self.report({'INFO'}, "SEUT: Changed all empties to display type 'Cube'.")

        return {'FINISHED'}
import bpy

from bpy.types      import Operator

from ..seut_errors  import seut_report


class SEUT_OT_FixPositioning(Operator):
    """Attempts to fix the positioning of an imported object and its children"""
    bl_idname = "object.fix_positioning"
    bl_label = "Attempt to Fix Positioning"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):
        """Attempts to fix the positioning of an imported object and its children"""

        obj = context.window.view_layer.objects.active

        parent_x = obj.location.x
        parent_y = obj.location.y
        parent_z = obj.location.z
            
        obj.location.x = 0
        obj.location.y = 0
        obj.location.z = 0

        children = set(obj.children)

        for child in obj.children:
            if child.type == 'EMPTY':
                child.location.x = child.location.x + parent_x / obj.scale.x
                child.location.y = child.location.y + parent_y / obj.scale.y
                child.location.z = child.location.z + parent_z / obj.scale.z
            else:
                bpy.context.window.view_layer.objects.active = child
                child.select_set(state=True, view_layer=bpy.context.window.view_layer)
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        obj.location.x = parent_x
        obj.location.y = parent_y
        obj.location.z = parent_z

        bpy.context.window.view_layer.objects.active = obj
        obj.select_set(state=True, view_layer=bpy.context.window.view_layer)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=True, properties=False)

        for child2 in children:
            child2.parent = obj

        obj.rotation_euler.x = 0
        obj.rotation_euler.y = 0
        obj.rotation_euler.z = 0

        seut_report(self, context, 'INFO', True, 'I013')

        return {'FINISHED'}
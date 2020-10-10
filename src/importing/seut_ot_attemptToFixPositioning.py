import bpy

from bpy.types      import Operator

class SEUT_OT_AttemptToFixPositioning(Operator):
    """Attempts to fix the positioning of an imported object and its children"""
    bl_idname = "object.attempt_to_fix_positioning"
    bl_label = "Attempt to Fix Positioning"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):

        obj = context.window.view_layer.objects.active

        parentX = obj.location.x
        parentY = obj.location.y
        parentZ = obj.location.z
            
        obj.location.x = 0
        obj.location.y = 0
        obj.location.z = 0

        children = set(obj.children)

        for child in obj.children:
            if child.type == 'EMPTY':
                child.location.x = child.location.x + parentX / obj.scale.x
                child.location.y = child.location.y + parentY / obj.scale.y
                child.location.z = child.location.z + parentZ / obj.scale.z
            else:
                bpy.context.window.view_layer.objects.active = child
                child.select_set(state=True, view_layer=bpy.context.window.view_layer)
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        obj.location.x = parentX
        obj.location.y = parentY
        obj.location.z = parentZ

        bpy.context.window.view_layer.objects.active = obj
        obj.select_set(state=True, view_layer=bpy.context.window.view_layer)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=True, properties=False)

        for child2 in children:
            child2.parent = obj

        obj.rotation_euler.x = 0
        obj.rotation_euler.y = 0
        obj.rotation_euler.z = 0

        return {'FINISHED'}
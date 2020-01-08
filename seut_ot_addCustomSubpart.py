import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

class SEUT_OT_AddCustomSubpart(Operator):
    """Adds a custom subpart"""
    bl_idname = "object.add_custom_subpart"
    bl_label = "Add Custom Subpart"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    prefix: StringProperty(
        name="Subpart Prefix",
        default="subpart_",
    )

    def execute(self, context):
        
        scene = context.scene
        targetObjects = bpy.context.view_layer.objects.selected
        
        if len(targetObjects) > 1:
            print("SEUT Error 009: Cannot create empties for more than one object at a time.")
            return {'CANCELLED'}
        
        # I need to figure out how I can get the first in the list but so far idk, this works
        for obj in targetObjects:
            targetObject = obj
            
        # Determine name strings.
        customPropName = "file"

        # Spawn empty
        location = bpy.data.objects[targetObject.name].location
        rotation = bpy.data.objects[targetObject.name].rotation_euler

        xD = bpy.data.objects[targetObject.name].dimensions.x
        yD = bpy.data.objects[targetObject.name].dimensions.y
        zD = bpy.data.objects[targetObject.name].dimensions.z

        bpy.ops.object.add(type='EMPTY', location=location, rotation=rotation)
        bpy.ops.transform.resize(value=(xD - 1, yD - 1, zD - 1))
        empty = bpy.context.view_layer.objects.active
        empty.scale = targetObject.scale

        empty.parent = targetObject.parent

        empty.empty_display_type = "CUBE"
        empty.name = self.prefix + targetObject.name

        bpy.data.objects[empty.name][customPropName] = targetObject.name

        return {'FINISHED'}
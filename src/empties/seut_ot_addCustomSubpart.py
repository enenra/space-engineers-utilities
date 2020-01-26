import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

class SEUT_OT_AddCustomSubpart(Operator):
    """Adds a custom subpart"""
    bl_idname = "object.add_custom_subpart"
    bl_label = "Add Custom Subpart"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: StringProperty(
        name="Subpart Prefix",
        description="The prefix with which to combine the selected object's name to create the name for the empty",
        default="subpart_",
    )

    def execute(self, context):
            
        # Determine name strings.
        customPropName = "file"

        # Spawn empty
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active

        empty.empty_display_type = "CUBE"

        bpy.data.objects[empty.name][customPropName] = ""
        
        self.report({'INFO'}, "SEUT: Subpart '%s' created for file: '%s'" % (empty.name,""))
        
        return {'FINISHED'}
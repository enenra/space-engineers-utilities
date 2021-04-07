import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report


class SEUT_OT_AddCustomSubpart(Operator):
    """Adds a custom subpart"""
    bl_idname = "scene.add_custom_subpart"
    bl_label = "Add Custom Subpart"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty(
        name="Subpart Name",
        description="The name of the custom subpart empty",
        default="subpart_",
    )


    def execute(self, context):
        scene = context.scene
            
        custom_prop_name = "file"
        selected_object = context.view_layer.objects.active

        bpy.ops.object.add(type='EMPTY')
        empty = context.view_layer.objects.active
        empty.name = self.name

        if not selected_object is None:
            empty.parent = selected_object

        empty.empty_display_type = 'ARROWS'
        bpy.data.objects[empty.name][custom_prop_name] = ""
        
        seut_report(self, context, 'INFO', True, 'I010', "Subpart", empty.name)
        
        return {'FINISHED'}
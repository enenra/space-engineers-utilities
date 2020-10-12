import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

from ..seut_ot_recreate_collections import get_collections
from ..seut_utils                   import getParentCollection
from ..seut_errors                  import report_error

class SEUT_OT_AddCustomSubpart(Operator):
    """Adds a custom subpart"""
    bl_idname = "object.add_custom_subpart"
    bl_label = "Add Custom Subpart"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(
        name="Subpart Name",
        description="The name of the custom subpart empty",
        default="subpart_",
    )

    def execute(self, context):
        scene = context.scene
            
        # Determine name strings.
        customPropName = "file"

        selectedObject = context.view_layer.objects.active

        # Spawn empty
        bpy.ops.object.add(type='EMPTY')
        empty = context.view_layer.objects.active
        empty.name = self.name

        if not selectedObject is None:
            empty.parent = selectedObject

        empty.empty_display_type = 'ARROWS'

        bpy.data.objects[empty.name][customPropName] = ""
        
        self.report({'INFO'}, "SEUT: Subpart '%s' created." % (empty.name))
        
        return {'FINISHED'}
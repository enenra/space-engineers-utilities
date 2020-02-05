import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections


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
        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)

        if collections['main'] is None:
            self.report({'ERROR'}, "SEUT: Cannot create empty without 'Main' collection existing. (024)")
            return {'CANCELLED'}
            
        # Determine name strings.
        customPropName = "file"

        # Spawn empty
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active
        empty.name = 'subpart_' + empty.name

        # If the empty is already part of the main collection, this yields a RuntimeError
        try:
            collections['main'].objects.link(empty)
        except RuntimeError:
            pass

        empty.empty_display_type = "CUBE"

        bpy.data.objects[empty.name][customPropName] = ""
        
        self.report({'INFO'}, "SEUT: Subpart '%s' created for file: '%s'" % (empty.name,""))
        
        return {'FINISHED'}
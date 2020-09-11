import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_utils                   import getParentCollection
from ..seut_errors                  import report_error

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
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        if collections['main'] is None:
            report_error(self, context, True, '024')
            return {'CANCELLED'}
            
        # Determine name strings.
        customPropName = "file"

        # Spawn empty
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active
        empty.name = 'subpart_' + empty.name

        parentCollection = getParentCollection(context, empty)

        if parentCollection != collections['main']:
            collections['main'].objects.link(empty)

            if parentCollection is None:
                scene.collection.objects.unlink(empty)
            else:
                parentCollection.objects.unlink(empty)


        empty.empty_display_type = 'ARROWS'

        bpy.data.objects[empty.name][customPropName] = ""
        
        self.report({'INFO'}, "SEUT: Subpart '%s' created." % (empty.name))
        
        return {'FINISHED'}
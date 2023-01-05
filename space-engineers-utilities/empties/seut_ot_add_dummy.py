import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from .seut_empties                  import empty_types
from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report
from ..seut_preferences             import empties


def items_detector_types(self, context):

    items = []
    for key, entry in empties['dummies'].items():   # NOTE: This will error after a reload of the addon.
        items.append((key, entry['name'], entry['description']))
    
    return items


class SEUT_OT_AddDummy(Operator):
    """Adds a Space Engineers dummy"""
    bl_idname = "scene.add_dummy"
    bl_label = "Add Dummy"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return 'SEUT' in scene.view_layers


    detector_type: EnumProperty(
        name='Dummy Type',
        items=items_detector_types,
        default=0
    )
    index: IntProperty(
        name='Dummy Type Index',
        default=1,
        min=1,
        max=100
    )


    def execute(self, context):
        scene = context.scene
        collections = get_collections(scene)

        if collections['main'][0] is None:
            seut_report(self, context, 'ERROR', True, 'E002', "'Main'")
            return {'CANCELLED'}
        
        # Determine name strings.
        display_type = 'CUBE'
        empty_name = self.detector_type
        uses_index = empties['dummies'][self.detector_type]['index']
        
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active

        for key in empty_types.keys():
            if self.detector_type == key:
                display_type = empty_types[key]
                break

        empty.empty_display_type = display_type

        if uses_index:
            empty.name = empty_name + str(self.index)
        else:
            empty.name = empty_name

        # Special case to allow for instancing of character in pose
        if self.detector_type == 'dummy_character':
            bpy.data.objects[empty.name]['file'] = ""

        parent_collection = get_parent_collection(context, empty)
        if parent_collection != collections['main'][0]:
            collections['main'][0].objects.link(empty)

            if parent_collection is None:
                try:
                    scene.collection.objects.unlink(empty)
                except:
                    pass
            else:
                parent_collection.objects.unlink(empty)
        
        seut_report(self, context, 'INFO', True, 'I010', "Dummy", empty.name)
        
        return {'FINISHED'}
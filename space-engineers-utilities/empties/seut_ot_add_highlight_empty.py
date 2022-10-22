import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)


from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report
from ..seut_preferences             import empties


def items_detector_types(self, context):

    items = []
    for key, entry in empties['highlight_empties'].items():   # NOTE: This will error after a reload of the addon.
        items.append((key, entry['name'], entry['description']))
    
    return items


class SEUT_OT_AddHighlightEmpty(Operator):
    """Add highlight empty to selected object. \n Note: You must have a reference object selected"""
    bl_idname = "object.add_highlight_empty"
    bl_label = "Add Highlight"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return len(context.selected_objects) != 0 and 'SEUT' in scene.view_layers


    detector_type: EnumProperty(
        name='Highlight Type',
        items=items_detector_types,
        default=0
    )
    index: IntProperty(
        name='Highlight Type Index',
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
        
        target_objects = bpy.context.view_layer.objects.selected
        
        if len(target_objects) > 1:
            seut_report(self, context, 'ERROR', True, 'E009')
            return {'CANCELLED'}
        
        target_object = target_objects[0]
        
        parent_collection = get_parent_collection(context, target_object)
        if parent_collection != collections['main'][0]:
            seut_report(self, context, 'ERROR', True, 'E025')
            return {'CANCELLED'}


        # Determine name strings.
        object_name_addition = "_section_"
        custom_prop_name = "highlight"
        empty_name = self.detector_type
        uses_index = empties['highlight_empties'][self.detector_type]['index']
        
        # Spawn empty on world origin
        # Ideally I'd move it to the geometry of the selected object, but I cannot figure out how to place it while considering the origin
        location = bpy.data.objects[target_object.name].location
        rotation = bpy.data.objects[target_object.name].rotation_euler

        context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children[collections['seut'][0].name].children[parent_collection.name]
        bpy.ops.object.add(type='EMPTY', location=location, rotation=rotation)
        empty = bpy.context.view_layer.objects.active
        empty.parent = target_object.parent
        empty.empty_display_type = 'CUBE'

        if uses_index:
            empty.name = empty_name + str(self.index)
            if target_object.name.find("_section") == -1 and target_object.name.find("subpart") == -1:
                target_object.name = target_object.name + object_name_addition + str(self.index)
        else:
            empty.name = empty_name

        bpy.data.objects[empty.name][custom_prop_name] = target_object.name
        entry = empty.seut.highlight_objects.add()
        entry.obj = target_object
        
        seut_report(self, context, 'INFO', True, 'I011', empty.name, target_object.name)
        
        return {'FINISHED'}
import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_errors                  import seut_report
from ..seut_preferences             import empties


def items_detector_types(context, scene):

    items = []
    for key, entry in empties['preset_subparts'].items():   # NOTE: This will error after a reload of the addon.
        items.append((key, entry['name'], entry['description']))
    
    return items


class SEUT_OT_AddPresetSubpart(Operator):
    """Adds a preset subpart"""
    bl_idname = "scene.add_preset_subpart"
    bl_label = "Add Preset Subpart"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return 'SEUT' in scene.view_layers


    detector_type: EnumProperty(
        name='Subpart Type',
        items=items_detector_types,
        default=0
    )
    index: IntProperty(
        name='Subpart Type Index',
        default=1,
        min=1,
        max=100
    )


    def execute(self, context):
        scene = context.scene

        target_object = None
        if 0 in context.selected_objects:
            target_object = context.selected_objects[0]

        # Determine name strings.
        custom_prop_name = "file"
        empty_name = self.detector_type
        uses_index = empties['highlight_empties'][self.detector_type]['index']

        bpy.ops.object.add(type='EMPTY')
        empty = context.view_layer.objects.active
        empty.empty_display_type = 'ARROWS'

        if uses_index:
            empty.name = empty_name + str(self.index)
        else:
            empty.name = empty_name
            
        if target_object != None:
            empty.parent = target_object
            if target_object.users_collection[0] != None:
                empty.users_collection[0].objects.unlink(empty)
                target_object.users_collection[0].objects.link(empty)

        bpy.data.objects[empty.name][custom_prop_name] = ""
        
        seut_report(self, context, 'INFO', True, 'I010', "Subpart", empty.name)
        
        return {'FINISHED'}
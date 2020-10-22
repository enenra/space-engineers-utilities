import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)


from ..seut_collections             import get_collections
from ..seut_utils                   import getParentCollection
from ..seut_errors                  import seut_report


class SEUT_OT_AddHighlightEmpty(Operator):
    """Add highlight empty to selected object"""
    bl_idname = "object.add_highlight_empty"
    bl_label = "Add Highlight"
    bl_options = {'REGISTER', 'UNDO'}


    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0


    detector_type: EnumProperty(
        name='Highlight Type',
        items=(
            ('conveyor', 'Conveyor', 'Defines large conveyor access point.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyor_small', 'Small Conveyor', 'Small Conveyor, Defines small conveyor access point.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('terminal', 'Terminal', 'Defines terminal access point'),
            ('textpanel', 'Text Panel', 'Defines access points for LCD Text Panels'),
            ('button', 'Button', 'Defines access points for single buttons'),
            ('cockpit', 'Cockpit', 'Defines access point to block that can be entered'),
            ('door', 'Door', 'Defines door access point'),
            ('advanceddoor', 'Advanced Door', 'Defines advanced door access point'),
            ('block', 'Medical Station', 'Defines access point to part of medical station that allows for health / o2 / h2 / energy regeneration'),
            ('wardrobe', 'Wardrobe', 'Defines access point to part of medical station that allows the switching of skins.\nNote: Moves player to within the empty and disables jetpack. May require geometry above and below so player does not fall due to gravity'),
            ('cryopod', 'Cryopod', 'Defines cryopod access point'),
            ('inventory', 'Inventory', 'Defines inventory access point (without conveyor functionality)')
            ),
        default='conveyor'
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

        if collections['main'] is None:
            seut_report(self, context, 'ERROR', True, 'E002', "'Main'")
            return {'CANCELLED'}
        
        target_objects = bpy.context.view_layer.objects.selected
        
        if len(target_objects) > 1:
            seut_report(self, context, 'ERROR', True, 'E009')
            return {'CANCELLED'}
        
        target_object = target_objects[0]
        
        parent_collection = getParentCollection(context, target_object)
        if parent_collection != collections['main']:
            seut_report(self, context, 'ERROR', True, 'E025')
            return {'CANCELLED'}


        # Determine name strings.
        empty_name = ""
        object_name_addition = "_section_"
        custom_prop_name = "highlight"
        uses_index = False
        
        if self.detector_type == 'conveyor':
            empty_name = "detector_conveyor_"
            uses_index = True
        elif self.detector_type == 'conveyor_small':
            empty_name = "detector_conveyor_small_"
            uses_index = True
        elif self.detector_type == 'terminal':
            empty_name = "detector_terminal_"
            uses_index = True
        elif self.detector_type == 'textpanel':
            empty_name = "detector_textpanel"
            uses_index = False
        elif self.detector_type == 'button':
            empty_name = "dummy_detector_panel_button_"
            uses_index = True
        elif self.detector_type == 'cockpit':
            empty_name = "detector_cockpit_"
            uses_index = True
        elif self.detector_type == 'door':
            empty_name = "detector_door_"
            uses_index = True
        elif self.detector_type == 'advanceddoor':
            empty_name = "detector_advanceddoor_"
            uses_index = True
        elif self.detector_type == 'block':
            empty_name = "detector_block_"
            uses_index = True
        elif self.detector_type == 'wardrobe':
            empty_name = "detector_wardrobe"
            uses_index = False
        elif self.detector_type == 'cryopod':
            empty_name = "detector_cryopod_"
            uses_index = True
        elif self.detector_type == 'inventory':
            empty_name = "detector_inventory_"
            uses_index = True
        
        # Spawn empty on world origin
        # Ideally I'd move it to the geometry of the selected object, but I cannot figure out how to place it while considering the origin
        location = bpy.data.objects[target_object.name].location
        rotation = bpy.data.objects[target_object.name].rotation_euler

        bpy.ops.object.add(type='EMPTY', location=location, rotation=rotation)
        empty = bpy.context.view_layer.objects.active
        empty.parent = target_object.parent

        parent_collection = getParentCollection(context, empty)
        if parent_collection != collections['main']:
            collections['main'].objects.link(empty)

            if parent_collection is None:
                scene.collection.objects.unlink(empty)
            else:
                parent_collection.objects.unlink(empty)

        empty.empty_display_type = 'CUBE'

        if uses_index:
            empty.name = empty_name + str(self.index)
            target_object.name = target_object.name + object_name_addition + str(self.index)
        else:
            empty.name = empty_name

        bpy.data.objects[empty.name][custom_prop_name] = target_object.name
        empty.seut.linkedObject = target_object
        
        seut_report(self, context, 'INFO', True, 'I011', empty.name, target_object.name)
        
        return {'FINISHED'}
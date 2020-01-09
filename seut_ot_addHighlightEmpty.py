import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

class SEUT_OT_AddHighlightEmpty(Operator):
    """Add highlight empty to selected object"""
    bl_idname = "object.add_highlight_empty"
    bl_label = "Add Highlight"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    detectorType: EnumProperty(
        name='Highlight Type',
        items=(
            ('conveyor', 'Conveyor', 'Defines large conveyor access point'),
            ('conveyor_small', 'Small Conveyor', 'Small Conveyor, Defines small conveyor access point'),
            ('terminal', 'Terminal', 'Defines terminal access point'),
            ('button', 'Button', 'Defines access points for single buttons'),
            ('cockpit', 'Cockpit', 'Defines access point to block that can be entered'),
            ('door', 'Door', 'Defines door access point'),
            ('advanceddoor', 'Advanced Door', 'Defines advanced door access point'),
            ('block', 'Medical Station', 'Defines access point to part of medical station that allows for health / o2 / h2 / energy regeneration'),
            ('wardrobe', 'Wardrobe', 'Defines access point to part of medical station that allows the switching of skins'),
            ('cryopod', 'Cryopod', 'Defines cryopod access point')
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
        targetObjects = bpy.context.view_layer.objects.selected
        
        if len(targetObjects) > 1:
            self.report({'ERROR'}, "SEUT: Cannot create empties for more than one object at a time. (009)")
            return {'CANCELLED'}
        
        # I need to figure out how I can get the first in the list but so far idk, this works
        for obj in targetObjects:
            targetObject = obj

        # Determine name strings.
        emptyName = ""
        objectNameAddition = "_section_"
        customPropName = "highlight"
        usesIndex = False

        if self.detectorType == 'conveyor':
            emptyName = "detector_conveyor_"
            usesIndex = True

        if self.detectorType == 'conveyor_small':
            emptyName = "detector_conveyor_small_"
            usesIndex = True

        if self.detectorType == 'terminal':
            emptyName = "detector_terminal_"
            usesIndex = True

        if self.detectorType == 'button':
            emptyName = "dummy_detector_panel_button_"
            usesIndex = True

        if self.detectorType == 'cockpit':
            emptyName = "detector_cockpit_"
            usesIndex = True

        if self.detectorType == 'door':
            emptyName = "detector_door_"
            usesIndex = True

        if self.detectorType == 'advanceddoor':
            emptyName = "detector_advanceddoor_"
            usesIndex = True

        if self.detectorType == 'block':
            emptyName = "detector_block_"
            usesIndex = True

        if self.detectorType == 'wardrobe':
            emptyName = "detector_wardrobe"
            usesIndex = False

        if self.detectorType == 'cryopod':
            emptyName = "detector_cryopod_"
            usesIndex = True
        
        # Spawn empty on world origin
        # Ideally I'd move it to the geometry of the selected object, but I cannot figure out how to place it while considering the origin
        location = bpy.data.objects[targetObject.name].location
        rotation = bpy.data.objects[targetObject.name].rotation_euler

        xD = bpy.data.objects[targetObject.name].dimensions.x
        yD = bpy.data.objects[targetObject.name].dimensions.y
        zD = bpy.data.objects[targetObject.name].dimensions.z

        bpy.ops.object.add(type='EMPTY', location=location, rotation=rotation)
        bpy.ops.transform.resize(value=(xD - 1, yD - 1, zD - 1))
        empty = bpy.context.view_layer.objects.active
        empty.parent = targetObject.parent

        empty.empty_display_type = "CUBE"

        if usesIndex:
            empty.name = emptyName + str(self.index)
            targetObject.name = targetObject.name + objectNameAddition + str(self.index)
        else:
            empty.name = emptyName

        bpy.data.objects[empty.name][customPropName] = targetObject.name
        
        self.report({'INFO'}, "SEUT: Highlight '%s' created for object: '%s'" % (empty.name,targetObject.name))

        return {'FINISHED'}
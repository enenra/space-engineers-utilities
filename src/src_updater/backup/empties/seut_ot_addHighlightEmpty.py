import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)


from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_utils                   import getParentCollection


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
            ('conveyor', 'Conveyor', 'Defines large conveyor access point.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyor_small', 'Small Conveyor', 'Small Conveyor, Defines small conveyor access point.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('terminal', 'Terminal', 'Defines terminal access point'),
            ('button', 'Button', 'Defines access points for single buttons'),
            ('cockpit', 'Cockpit', 'Defines access point to block that can be entered'),
            ('door', 'Door', 'Defines door access point'),
            ('advanceddoor', 'Advanced Door', 'Defines advanced door access point'),
            ('block', 'Medical Station', 'Defines access point to part of medical station that allows for health / o2 / h2 / energy regeneration'),
            ('wardrobe', 'Wardrobe', 'Defines access point to part of medical station that allows the switching of skins.\nNote: Moves player to within the empty and disables jetpack. May require geometry above and below so player does not fall due to gravity'),
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
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        if collections['main'] is None:
            self.report({'ERROR'}, "SEUT: Cannot create empty without 'Main' collection existing. (024)")
            return {'CANCELLED'}
        
        targetObjects = bpy.context.view_layer.objects.selected
        
        if len(targetObjects) > 1:
            self.report({'ERROR'}, "SEUT: Cannot create empties for more than one object at a time. (009)")
            return {'CANCELLED'}
        
        # I need to figure out how I can get the first in the list but so far idk, this works
        for obj in targetObjects:
            targetObject = obj
        
        parentCollection = getParentCollection(context, targetObject)
        if parentCollection != collections['main']:
            self.report({'ERROR'}, "SEUT: Cannot create highlight empty for object outside of 'Main' collection. (025)")
            return {'CANCELLED'}


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

        parentCollection = getParentCollection(context, empty)

        if parentCollection != collections['main']:
            collections['main'].objects.link(empty)

            if parentCollection is None:
                scene.collection.objects.unlink(empty)
            else:
                parentCollection.objects.unlink(empty)

        empty.empty_display_type = "CUBE"

        if usesIndex:
            empty.name = emptyName + str(self.index)
            targetObject.name = targetObject.name + objectNameAddition + str(self.index)
        else:
            empty.name = emptyName

        bpy.data.objects[empty.name][customPropName] = targetObject.name
        empty.seut.linkedObject = targetObject
        
        self.report({'INFO'}, "SEUT: Highlight '%s' created for object: '%s'" % (empty.name,targetObject.name))
        
        return {'FINISHED'}
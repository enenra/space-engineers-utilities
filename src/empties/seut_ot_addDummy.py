import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_utils                   import getParentCollection


class SEUT_OT_AddDummy(Operator):
    """Adds a Space Engineers dummy"""
    bl_idname = "object.add_dummy"
    bl_label = "Add Dummy"
    bl_options = {'REGISTER', 'UNDO'}

    # Some dummies aparently use different default rotations. Include in descriptions once I know which.
    detectorType: EnumProperty(
        name='Dummy Type',
        items=(
            ('conveyorline', 'Conveyorline', 'Conveyor connection point without direct access. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_small', 'Conveyorline Small', 'Small conveyor connection point without direct access. Deos not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_in', 'Conveyorline In', 'Conveyor connection point without direct access that only lets items pass into the block. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_out', 'Conveyorline Out', 'Conveyor connection point without direct access that only lets items pass out of the block. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('Connector', 'Connector', 'Adds connector functionality.\n Warning: Cannot be placed too far from block origin or the connector will only spin grids instead of connecting'),
            ('ejector', 'Ejector', 'Adds ejector functionality'),
            ('collector', 'Collector', 'Adds collector functionality'),
            ('merge', 'Merge Block', 'Adds merge block functionality'),
            ('thruster_flame', 'Thruster Flame', 'Determines the point where the thruster flame will appear.\nNotes: Empty size defines flame width. Flame length is controlled within the SBC definition. Flare will only appear on empty with lowest index.\nWarning: Thrust direction is always the Y+ axis'),
            ('muzzle_missile', 'Muzzle Missile', 'The point of origin for missiles shot by the block.\nNotes: Should be placed with some distance to mesh, otherwise missiles can collide with geometry of launcher.\nWarning: Shoot direction is always the Y+ axis'),
            ('muzzle_projectile', 'Muzzle Projectile', 'The point of origin for projectiles shot by the block.\nWarning: Shoot direction is always the Y+ axis'),
            ('respawn', 'Respawn Point', 'The location in which players will respawn. Tends to place player origin (feet) to middlepoint of empty'),
            ('light', 'Light', 'Point of origin for a light source. Does not cast shadows'),
            ('camera', 'Camera', 'Overrides default camera position at origin'),
            ('upgrade', 'Upgrade Module', 'Marks slots where upgrade modules can be placed'),
            ('vent', 'Air Vent', 'Adds air vent functionality'),
            ('gear_lock', 'Landing Gear', 'Adds landing gear functionality. Any geometry within the empty will be a valid lock target - not only near the point of origin'),
            ('shiptool', 'Ship Tool', 'The point of origin for ship tool effects (not visual)'),
            ('electric_motor', 'Electric Motor', 'The location onto which a rotor head or wheel will be placed'),
            ('character', 'Character', 'The location in which the character model will be placed. Point of origin is generally aligned with the butt of the character but this can depend on the pose'),
            ('particles1', 'Particles 1', 'Point of origin for particles (used in grinder and welder)'),
            ('particles2', 'Particles 2', 'Point of origin for particles (used in grinder)'),
            ('TopBlock', 'Piston Top', 'The top part of a piston'),
            ('wheel', 'Wheel', 'The position at which a wheel is connected to a suspension'),
            ('center', 'Center', 'Defines the center of a block')
            ),
        default='conveyorline'
    )
    index: IntProperty(
        name='Dummy Type Index',
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
        
        # Determine name strings.
        emptyName = ""
        usesIndex = False
        displayType = 'CUBE'

        if self.detectorType == 'conveyorline':
            emptyName = "dummy_detector_conveyorline_"
            usesIndex = True

        if self.detectorType == 'conveyorline_small':
            emptyName = "dummy_detector_conveyorline_small_"
            usesIndex = True

        if self.detectorType == 'conveyorline_in':
            emptyName = "dummy_detector_conveyorline_in_"
            usesIndex = True

        if self.detectorType == 'conveyorline_out':
            emptyName = "dummy_detector_conveyorline_out_"
            usesIndex = True

        if self.detectorType == 'Connector':
            emptyName = "dummy_detector_Connector_"
            usesIndex = True

        if self.detectorType == 'ejector':
            emptyName = "dummy_detector_ejector_"
            usesIndex = True

        if self.detectorType == 'collector':
            emptyName = "dummy_detector_collector_"
            usesIndex = True

        if self.detectorType == 'merge':
            emptyName = "detector_merge_"
            usesIndex = True

        if self.detectorType == 'thruster_flame':
            emptyName = "thruster_flame_"
            usesIndex = True

        if self.detectorType == 'muzzle_missile':
            emptyName = "muzzle_missile_"
            usesIndex = True
            displayType = 'CONE'

        if self.detectorType == 'muzzle_projectile':
            emptyName = "muzzle_projectile_"
            usesIndex = True
            displayType = 'CONE'

        if self.detectorType == 'respawn':
            emptyName = "dummy_detector_respawn"
            usesIndex = False

        if self.detectorType == 'light':
            emptyName = "light_"
            usesIndex = True

        if self.detectorType == 'camera':
            emptyName = "dummy_camera"
            usesIndex = False
            displayType = 'CONE'

        if self.detectorType == 'upgrade':
            emptyName = "detector_upgrade_"
            usesIndex = True

        if self.detectorType == 'vent':
            emptyName = "detector_merge_"
            usesIndex = True

        if self.detectorType == 'gear_lock':
            emptyName = "gear_lock_"
            usesIndex = True

        if self.detectorType == 'shiptool':
            emptyName = "dummy_detector_shiptool_"
            usesIndex = True

        if self.detectorType == 'electric_motor':
            emptyName = "dummy_electric_motor"
            usesIndex = False

        if self.detectorType == 'character':
            emptyName = "dummy_character"
            usesIndex = False

        if self.detectorType == 'particles1':
            emptyName = "dummy_particles1"
            usesIndex = False

        if self.detectorType == 'particles2':
            emptyName = "dummy_particles2"
            usesIndex = False

        if self.detectorType == 'TopBlock':
            emptyName = "dummy_TopBlock"
            usesIndex = False

        if self.detectorType == 'wheel':
            emptyName = "dummy_wheel"
            usesIndex = False

        if self.detectorType == 'center':
            emptyName = "Center"
            usesIndex = False
        
        # Spawn empty
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active

        empty.empty_display_type = displayType

        if usesIndex:
            empty.name = emptyName + str(self.index)
        else:
            empty.name = emptyName

        parentCollection = getParentCollection(context, empty)

        if parentCollection != collections['main']:
            collections['main'].objects.link(empty)

            if parentCollection is None:
                scene.collection.objects.unlink(empty)
            else:
                parentCollection.objects.unlink(empty)
        
        self.report({'INFO'}, "SEUT: Dummy '%s' created." % (empty.name))
        
        return {'FINISHED'}
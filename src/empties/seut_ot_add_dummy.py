import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from .seut_empties                  import empty_types
from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report


class SEUT_OT_AddDummy(Operator):
    """Adds a Space Engineers dummy"""
    bl_idname = "scene.add_dummy"
    bl_label = "Add Dummy"
    bl_options = {'REGISTER', 'UNDO'}


    detector_type: EnumProperty(
        name='Dummy Type',
        items=(
            ('conveyorline', 'Conveyorline', 'Conveyor connection point without direct access. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_small', 'Conveyorline Small', 'Small conveyor connection point without direct access. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_in', 'Conveyorline In', 'Conveyor connection point without direct access that only lets items pass into the block. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_out', 'Conveyorline Out', 'Conveyor connection point without direct access that only lets items pass out of the block. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('Connector', 'Connector', 'Adds connector functionality.\n Warning: Cannot be placed too far from block origin or the connector will only spin grids instead of connecting'),
            ('ejector', 'Ejector', 'Adds ejector functionality'),
            ('collector', 'Collector', 'Adds collector functionality'),
            ('merge', 'Merge Block', 'Adds merge block functionality'),
            ('thruster_flame', 'Thruster Flame', 'Determines the point where the thruster flame will appear.\nNotes: Empty size defines flame width. Flame length is controlled within the SBC definition. Flare will only appear on empty with lowest index.\nWarning: Thrust direction is always Y-'),
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
            ('center', 'Center', 'Defines the center of a block'),
            ('emitter', 'Emitter', 'Particle Emitter dummy used in exhaust-type blocks')
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
        collections = get_collections(scene)

        if collections['main'] is None:
            seut_report(self, context, 'ERROR', True, 'E002', "'Main'")
            return {'CANCELLED'}
        
        # Determine name strings.
        empty_name = ""
        uses_index = False
        display_type = 'CUBE'
        
        if self.detector_type == 'conveyorline':
            empty_name = "dummy_detector_conveyorline_"
            uses_index = True
        elif self.detector_type == 'conveyorline_small':
            empty_name = "dummy_detector_conveyorline_small_"
            uses_index = True
        elif self.detector_type == 'conveyorline_in':
            empty_name = "dummy_detector_conveyorline_in_"
            uses_index = True
        elif self.detector_type == 'conveyorline_out':
            empty_name = "dummy_detector_conveyorline_out_"
            uses_index = True
        elif self.detector_type == 'Connector':
            empty_name = "dummy_detector_Connector_"
            uses_index = True
        elif self.detector_type == 'ejector':
            empty_name = "dummy_detector_ejector_"
            uses_index = True
        elif self.detector_type == 'collector':
            empty_name = "dummy_detector_collector_"
            uses_index = True
        elif self.detector_type == 'merge':
            empty_name = "detector_merge_"
            uses_index = True
        elif self.detector_type == 'thruster_flame':
            empty_name = "thruster_flame_"
            uses_index = True
        elif self.detector_type == 'muzzle_missile':
            empty_name = "muzzle_missile_"
            uses_index = True
        elif self.detector_type == 'muzzle_projectile':
            empty_name = "muzzle_projectile_"
            uses_index = True
        elif self.detector_type == 'respawn':
            empty_name = "dummy_detector_respawn"
            uses_index = False
        elif self.detector_type == 'light':
            empty_name = "light_"
            uses_index = True
        elif self.detector_type == 'camera':
            empty_name = "dummy_camera"
            uses_index = False
        elif self.detector_type == 'upgrade':
            empty_name = "detector_upgrade_"
            uses_index = True
        elif self.detector_type == 'vent':
            empty_name = "vent_"
            uses_index = True
        elif self.detector_type == 'gear_lock':
            empty_name = "gear_lock_"
            uses_index = True
        elif self.detector_type == 'shiptool':
            empty_name = "dummy_detector_shiptool_"
            uses_index = True
        elif self.detector_type == 'electric_motor':
            empty_name = "dummy_electric_motor"
            uses_index = False
        elif self.detector_type == 'character':
            empty_name = "dummy_character"
            uses_index = False
        elif self.detector_type == 'particles1':
            empty_name = "dummy_particles1"
            uses_index = False
        elif self.detector_type == 'particles2':
            empty_name = "dummy_particles2"
            uses_index = False
        elif self.detector_type == 'TopBlock':
            empty_name = "dummy_TopBlock"
            uses_index = False
        elif self.detector_type == 'wheel':
            empty_name = "dummy_wheel"
            uses_index = False
        elif self.detector_type == 'center':
            empty_name = "Center"
            uses_index = False
        elif self.detector_type == 'emitter':
            empty_name = "emitter"
            uses_index = False
        
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

        parent_collection = get_parent_collection(context, empty)
        if parent_collection != collections['main']:
            collections['main'].objects.link(empty)

            if parent_collection is None:
                scene.collection.objects.unlink(empty)
            else:
                parent_collection.objects.unlink(empty)
        
        seut_report(self, context, 'INFO', True, 'I010', "Dummy", empty.name)
        
        return {'FINISHED'}
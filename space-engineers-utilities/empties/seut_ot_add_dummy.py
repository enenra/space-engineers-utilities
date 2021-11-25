import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from .seut_empties                  import empty_types
from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report


empties = {
    'conveyorline': {'name': "dummy_detector_conveyorline_", 'index': True},
    'conveyorline_small': {'name': "dummy_detector_conveyorline_small_", 'index': True},
    'conveyorline_in': {'name': "dummy_detector_conveyorline_in_", 'index': True},
    'conveyorline_out': {'name': "dummy_detector_conveyorline_out_", 'index': True},
    'conveyorline_small_in': {'name': "dummy_detector_conveyorline_small_in_", 'index': True},
    'conveyorline_small_out': {'name': "dummy_detector_conveyorline_small_out_", 'index': True},
    'Connector': {'name': "dummy_detector_Connector_", 'index': True},
    'ejector': {'name': "dummy_detector_ejector_", 'index': True},
    'collector': {'name': "dummy_detector_collector_", 'index': True},
    'merge': {'name': "detector_merge_", 'index': True},
    'thruster_flame': {'name': "thruster_flame_", 'index': True},
    'muzzle_missile': {'name': "muzzle_missile_", 'index': True},
    'muzzle_projectile': {'name': "muzzle_projectile_", 'index': True},
    'respawn': {'name': "dummy_detector_respawn", 'index': False},
    'light': {'name': "light_", 'index': True},
    'camera': {'name': "dummy_camera", 'index': False},
    'upgrade': {'name': "detector_upgrade_", 'index': True},
    'vent': {'name': "vent_", 'index': True},
    'gear_lock': {'name': "gear_lock_", 'index': True},
    'shiptool': {'name': "dummy_detector_shiptool_", 'index': True},
    'electric_motor': {'name': "dummy_electric_motor", 'index': False},
    'character': {'name': "dummy_character", 'index': False},
    'particles1': {'name': "dummy_particles1", 'index': False},
    'particles2': {'name': "dummy_particles2", 'index': False},
    'TopBlock': {'name': "dummy_TopBlock", 'index': False},
    'wheel': {'name': "dummy_wheel", 'index': False},
    'center': {'name': "Center", 'index': False},
    'emitter': {'name': "emitter", 'index': False}
    }


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
            ('conveyorline_small_in', 'Conveyorline Small In', 'Conveyor connection point for small grid without direct access that only lets items pass into the block. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
            ('conveyorline_small_out', 'Conveyorline Small Out', 'Conveyor connection point for small grid without direct access that only lets items pass out of the block. Does not highlight anything.\nNote: Conveyor empties in a block must overlap point of origin of conveyor empty in adjacent block to connect'),
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

        if collections['main'][0] is None:
            seut_report(self, context, 'ERROR', True, 'E002', "'Main'")
            return {'CANCELLED'}
        
        # Determine name strings.
        display_type = 'CUBE'
        empty_name = empties[self.detector_type]['name']
        uses_index = empties[self.detector_type]['index']
        
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
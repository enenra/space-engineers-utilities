import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

class SEUT_OT_AddDummy(Operator):
    """Add dummy to selected object"""
    bl_idname = "object.add_dummy"
    bl_label = "Add Dummy"
    bl_options = {'REGISTER', 'UNDO'}

    # Some dummies aparently use different default rotations. Include in descriptions once I know which.
    detectorType: EnumProperty(
        name='Dummy Type',
        items=(
            ('conveyorline', 'Conveyorline', 'Conveyor connection point without direct access'),
            ('conveyorline_small', 'Conveyorline Small', 'Small conveyor connection point without direct access'),
            ('Connector', 'Connector', 'Adds connector functionality'),
            ('merge', 'Merge Block', 'Adds merge block functionality'),
            ('thruster_flame', 'Thruster Flame', 'Determines the point where the thruster flame will appear'),
            ('muzzle_missile', 'Muzzle Missile', 'The point of origin for missiles shot by the block'),
            ('muzzle_projectile', 'Muzzle Projectile', 'The point of origin for projectiles shot by the block'),
            ('respawn', 'Respawn Point', 'The location in which players will respawn'),
            ('light', 'Light', 'Point of origin for a light source'),
            ('camera', 'Camera', 'Overrides default camera position at origin'),
            ('upgrade', 'Upgrade Module', 'Marks slots where upgrade modules can be placed'),
            ('vent', 'Air Vent', 'Adds air vent functionality'),
            ('gear_lock', 'Landing Gear', 'Adds landing gear functionality'),
            ('shiptool', 'Ship Tool', 'The point of origin for ship tool effects (not visual)'),
            ('electric_motor', 'Electric Motor', 'The location onto which a rotor head will be placed'),
            ('character', 'Character', 'The location in which the character model will be placed'),
            ('particles1', 'Particles 1', 'Point of origin for particles (used in grinder and welder)'),
            ('particles2', 'Particles 2', 'Point of origin for particles (used in grinder)'),
            ('TopBlock', 'Piston Top', 'The top part of a piston')
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

        # Determine name strings.
        emptyName = ""
        usesIndex = False

        if self.detectorType == 'conveyorline':
            emptyName = "dummy_detector_conveyorline_"
            usesIndex = True

        if self.detectorType == 'conveyorline_small':
            emptyName = "dummy_detector_conveyorline_small_"
            usesIndex = True

        if self.detectorType == 'Connector':
            emptyName = "dummy_detector_Connector_"
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

        if self.detectorType == 'muzzle_projectile':
            emptyName = "muzzle_projectile_"
            usesIndex = True

        if self.detectorType == 'respawn':
            emptyName = "dummy_detector_respawn"
            usesIndex = False

        if self.detectorType == 'light':
            emptyName = "light_"
            usesIndex = True

        if self.detectorType == 'camera':
            emptyName = "dummy_camera"
            usesIndex = False

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
        
        # Spawn empty
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active

        empty.empty_display_type = "CUBE"

        if usesIndex:
            empty.name = emptyName + str(self.index)
        else:
            empty.name = emptyName
        
        self.report({'INFO'}, "SEUT: Dummy '%s' created." % (empty.name))
        
        return {'FINISHED'}
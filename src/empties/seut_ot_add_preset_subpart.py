import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report


class SEUT_OT_AddPresetSubpart(Operator):
    """Adds a preset subpart"""
    bl_idname = "scene.add_preset_subpart"
    bl_label = "Add Preset Subpart"
    bl_options = {'REGISTER', 'UNDO'}


    # pistons probably missing, hangar doors too
    detector_type: EnumProperty(
        name='Subpart Type',
        items=(
            ('DoorLeft', 'Door Left', 'The subpart for the left side of a sliding door'),
            ('DoorRight', 'Door Right', 'The subpart for the right side of a sliding door'),
            ('DrillHead', 'Drill Head', 'The subpart for the ship tool drill head'),
            ('grinder1', 'Grinder 1', 'Subpart for a grinder blade'),
            ('grinder2', 'Grinder 2', 'Subpart for a grinder blade'),
            ('Propeller', 'Propeller', 'Subpart for the propeller on an atmospheric engine'),
            ('InteriorTurretBase1', 'Interior Turret Base 1', 'Subpart for the first rotating part on an interior turret'),
            ('InteriorTurretBase2', 'Interior Turret Base 2', 'Subpart for the second rotating part on an interior turret (mounted on the first)'),
            ('MissileTurretBase1', 'Missile Turret Base 1', 'Subpart for the first rotating part on a missile turret'),
            ('MissileTurretBarrels', 'Missile Turret Barrels', 'Subpart for the second rotating part on a missile turret (mounted on the first)'),
            ('GatlingTurretBase1', 'Gatling Turret Base 1', 'Subpart for the first rotating part on a gatling turret'),
            ('GatlingTurretBase2', 'Gatling Turret Base 2', 'Subpart for the second rotating part on a gatling turret (mounted on the first)'),
            ('GatlingBarrel', 'Gatling Barrel', 'Subpart for the third rotating part on a gatling turret (the rotating barrel)'),
            ('Barrel', 'Barrel', 'Subpart for the barrel of the fixed gatling gun. (the rotating barrel)'),
            ('PistonSubpart1', 'Piston Subpart 1', 'The piston subpart attached to its base.\nWarning: Empty must also be present in BS collections or game will CTD on placement!'),
            ('PistonSubpart2', 'Piston Subpart 2', 'The piston subpart attached to its first subpart.\nWarning: Empty must also be present in BS collections or game will CTD on placement!'),
            ('PistonSubpart3', 'Piston Subpart 3', 'The piston subpart attached to its second subpart.\nWarning: Empty must also be present in BS collections or game will CTD on placement!'),
            ('TurbineRotor', 'Wind Turbine Rotor', 'The subpart containing the rotating blades of a wind turbine'),
            ('HangarDoor', 'Hangar Door Part', 'Subpart for a hangar door section. \nSupports index, and all of these subparts are placed within its base'),
            ('LaserComTurret', 'Laser Antenna Targeter Azimuth', 'Subpart for a laser antenna turret'),
            ('LaserCom', 'Laser Antenna Targeter Elevation', 'Subpart for a laser antenna turret (attached to Laser Antenna azimuth subpart)'),
            ('RotatingLightDummy', 'Rotating Light', 'Subpart for the rotating light top part in a Rotating Light block')
            ),
        default='DoorLeft'
    )
    index: IntProperty(
        name='Subpart Type Index',
        default=1,
        min=1,
        max=100
    )


    def execute(self, context):
        scene = context.scene
        target_object = context.selected_objects[0]

        # Determine name strings.
        empty_name = ""
        custom_prop_name = "file"
        uses_index = False
        
        if self.detector_type == 'DoorLeft':
            empty_name = "subpart_DoorLeft"
            uses_index = False
        elif self.detector_type == 'DoorRight':
            empty_name = "subpart_DoorRight"
            uses_index = False
        elif self.detector_type == 'DrillHead':
            empty_name = "subpart_DrillHead"
            uses_index = False
        elif self.detector_type == 'grinder1':
            empty_name = "subpart_grinder1"
            uses_index = False
        elif self.detector_type == 'grinder2':
            empty_name = "subpart_grinder2"
            uses_index = False
        elif self.detector_type == 'Propeller':
            empty_name = "subpart_Propeller"
            uses_index = False
        elif self.detector_type == 'InteriorTurretBase1':
            empty_name = "subpart_InteriorTurretBase1"
            uses_index = False
        elif self.detector_type == 'InteriorTurretBase2':
            empty_name = "subpart_InteriorTurretBase2"
            uses_index = False
        elif self.detector_type == 'MissileTurretBase1':
            empty_name = "subpart_MissileTurretBase1"
            uses_index = False
        elif self.detector_type == 'MissileTurretBarrels':
            empty_name = "subpart_MissileTurretBarrels"
            uses_index = False
        elif self.detector_type == 'GatlingTurretBase1':
            empty_name = "subpart_GatlingTurretBase1"
            uses_index = False
        elif self.detector_type == 'GatlingTurretBase2':
            empty_name = "subpart_GatlingTurretBase2"
            uses_index = False
        elif self.detector_type == 'GatlingBarrel':
            empty_name = "subpart_GatlingBarrel"
            uses_index = False
        elif self.detector_type == 'Barrel':
            empty_name = "subpart_Barrel"
            uses_index = False
        elif self.detector_type == 'PistonSubpart1':
            empty_name = "subpart_PistonSubpart1"
            uses_index = False
        elif self.detector_type == 'PistonSubpart2':
            empty_name = "subpart_PistonSubpart2"
            uses_index = False
        elif self.detector_type == 'PistonSubpart3':
            empty_name = "subpart_PistonSubpart3"
            uses_index = False
        elif self.detector_type == 'HangarDoor':
            empty_name = "subpart_HangarDoor_door"
            uses_index = True
        elif self.detector_type == 'LaserComTurret':
            empty_name = "subpart_LaserComTurret"
            uses_index = False
        elif self.detector_type == 'LaserCom':
            empty_name = "subpart_LaserCom"
            uses_index = False
        elif self.detector_type == 'RotatingLightDummy':
            empty_name = "subpart_RotatingLightDummy"
            uses_index = False

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
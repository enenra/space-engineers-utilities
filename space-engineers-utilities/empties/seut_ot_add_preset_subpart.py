import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_collections             import get_collections
from ..seut_utils                   import get_parent_collection
from ..seut_errors                  import seut_report


empties = {
    'DoorLeft': {'name': "subpart_DoorLeft", 'index': False},
    'DoorRight': {'name': "subpart_DoorRight", 'index': False},
    'DrillHead': {'name': "subpart_DrillHead", 'index': False},
    'grinder1': {'name': "subpart_grinder1", 'index': False},
    'grinder2': {'name': "subpart_grinder2", 'index': False},
    'Propeller': {'name': "subpart_Propeller", 'index': False},
    'InteriorTurretBase1': {'name': "subpart_InteriorTurretBase1", 'index': False},
    'InteriorTurretBase2': {'name': "subpart_InteriorTurretBase2", 'index': False},
    'MissileTurretBase1': {'name': "subpart_MissileTurretBase1", 'index': False},
    'MissileTurretBarrels': {'name': "subpart_MissileTurretBarrels", 'index': False},
    'GatlingTurretBase1': {'name': "subpart_GatlingTurretBase1", 'index': False},
    'GatlingTurretBase2': {'name': "subpart_GatlingTurretBase2", 'index': False},
    'GatlingBarrel': {'name': "subpart_GatlingBarrel", 'index': False},
    'Barrel': {'name': "subpart_Barrel", 'index': False},
    'PistonSubpart1': {'name': "subpart_PistonSubpart1", 'index': False},
    'PistonSubpart2': {'name': "subpart_PistonSubpart2", 'index': False},
    'PistonSubpart3': {'name': "subpart_PistonSubpart3", 'index': False},
    'TurbineRotor': {'name': "subpart_TurbineRotor", 'index': False},
    'HangarDoor': {'name': "subpart_HangarDoor_door", 'index': True},
    'LaserComTurret': {'name': "subpart_LaserComTurret", 'index': False},
    'LaserCom': {'name': "subpart_LaserCom", 'index': False},
    'RotatingLightDummy': {'name': "subpart_RotatingLightDummy", 'index': False},
    'magazine': {'name': "subpart_magazine", 'index': False}
    }


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
            ('RotatingLightDummy', 'Rotating Light', 'Subpart for the rotating light top part in a Rotating Light block'),
            ('magazine', 'Magazine', 'Subpart for the magazine on a hand weapon')
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

        target_object = None
        if 0 in context.selected_objects:
            target_object = context.selected_objects[0]

        # Determine name strings.
        custom_prop_name = "file"
        empty_name = empties[self.detector_type]['name']
        uses_index = empties[self.detector_type]['index']

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
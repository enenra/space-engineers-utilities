import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_utils                   import getParentCollection


class SEUT_OT_AddPresetSubpart(Operator):
    """Adds a preset subpart"""
    bl_idname = "object.add_preset_subpart"
    bl_label = "Add Preset Subpart"
    bl_options = {'REGISTER', 'UNDO'}

    # pistons probably missing, hangar doors too
    detectorType: EnumProperty(
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
            ('PistonSubpart1', 'Piston Subpart 1', 'The piston subpart attached to its base'),
            ('PistonSubpart2', 'Piston Subpart 2', 'The piston subpart attached to its first subpart'),
            ('PistonSubpart3', 'Piston Subpart 3', 'The piston subpart attached to its second subpart'),
            ('TurbineRotor', 'Wind Turbine Rotor', 'The subpart containing the rotating blades of a wind turbine'),
            ('HangarDoor', 'Hangar Door Part', 'Subpart for a hangar door section. \nSupports index, and all of these subparts are placed within its base')
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
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        if collections['main'] is None:
            self.report({'ERROR'}, "SEUT: Cannot create empty without 'Main' collection existing. (024)")
            return {'CANCELLED'}

        # Determine name strings.
        emptyName = ""
        customPropName = "file"
        usesIndex = False

        if self.detectorType == 'DoorLeft':
            emptyName = "subpart_DoorLeft"
            usesIndex = False

        if self.detectorType == 'DoorRight':
            emptyName = "subpart_DoorRight"
            usesIndex = False

        if self.detectorType == 'DrillHead':
            emptyName = "subpart_DrillHead"
            usesIndex = False

        if self.detectorType == 'grinder1':
            emptyName = "subpart_grinder1"
            usesIndex = False

        if self.detectorType == 'grinder2':
            emptyName = "subpart_grinder2"
            usesIndex = False

        if self.detectorType == 'Propeller':
            emptyName = "subpart_Propeller"
            usesIndex = False

        if self.detectorType == 'InteriorTurretBase1':
            emptyName = "subpart_InteriorTurretBase1"
            usesIndex = False

        if self.detectorType == 'InteriorTurretBase2':
            emptyName = "subpart_InteriorTurretBase2"
            usesIndex = False

        if self.detectorType == 'MissileTurretBase1':
            emptyName = "subpart_MissileTurretBase1"
            usesIndex = False

        if self.detectorType == 'MissileTurretBarrels':
            emptyName = "subpart_MissileTurretBarrels"
            usesIndex = False

        if self.detectorType == 'GatlingTurretBase1':
            emptyName = "subpart_GatlingTurretBase1"
            usesIndex = False

        if self.detectorType == 'GatlingTurretBase2':
            emptyName = "subpart_GatlingTurretBase2"
            usesIndex = False

        if self.detectorType == 'GatlingBarrel':
            emptyName = "subpart_GatlingBarrel"
            usesIndex = False

        if self.detectorType == 'PistonSubpart1':
            emptyName = "subpart_PistonSubpart1"
            usesIndex = False

        if self.detectorType == 'PistonSubpart2':
            emptyName = "subpart_PistonSubpart2"
            usesIndex = False

        if self.detectorType == 'PistonSubpart3':
            emptyName = "subpart_PistonSubpart3"
            usesIndex = False

        if self.detectorType == 'HangarDoor':
            emptyName = "subpart_HangarDoor_door"
            usesIndex = True

        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active
        empty.empty_display_type = "CUBE"

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

        bpy.data.objects[empty.name][customPropName] = ""
        
        self.report({'INFO'}, "SEUT: Subpart '%s' created for file: '%s'" % (empty.name,""))
        
        return {'FINISHED'}
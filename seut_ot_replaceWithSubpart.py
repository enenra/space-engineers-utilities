import bpy

from bpy.types  import Operator
from bpy.props  import EnumProperty

class SEUT_OT_ReplaceWithSubpart(Operator):
    """Replaces selected mesh with subpart"""
    bl_idname = "object.replace_with_subpart"
    bl_label = "Replace with Subpart"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    detectorType: EnumProperty(
        name='Subpart Type',
        items=(
            ('DoorLeft', 'Door Left', ''),
            ('DoorRight', 'Door Right', ''),
            ('DrillHead', 'Drill Head', ''),
            ('InteriorTurretBase1', 'Interior Turret Base 1', ''),
            ('InteriorTurretBase2', 'Interior Turret Base 2', ''),
            ('MissileTurretBase1', 'Missile Turret Base 1', ''),
            ('MissileTurretBarrels', 'Missile Turret Barrels', ''),
            ('GatlingTurretBase1', 'Gatling Turret Base 1', ''),
            ('GatlingTurretBase2', 'Gatling Turret Base 2', ''),
            ('GatlingBarrel', 'Gatling Barrel', '')
            ),
        default='DoorLeft'
    )

    def execute(self, context):

        print("SEUT Debug: OT ReplaceWithSubpart")

        if self.detectorType == 'conveyor':
            print("Conveyor")

        if self.detectorType == 'terminal':
            print("Terminal")

        return {'FINISHED'}
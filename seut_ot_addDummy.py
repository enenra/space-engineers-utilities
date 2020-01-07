import bpy

from bpy.types  import Operator
from bpy.props  import EnumProperty

class SEUT_OT_AddDummy(Operator):
    """Add dummy to selected object"""
    bl_idname = "object.add_dummy"
    bl_label = "Add Dummy"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    detectorType: EnumProperty(
        name='Dummy Type',
        items=(
            ('Connector', 'Connector', ''),
            ('thruster_flame', 'Thruster Flame', ''),
            ('muzzle_missile', 'Muzzle Missile', ''),
            ('muzzle_projectile', 'Muzzle Projectile', ''),
            ('respawn', 'Respawn Point', ''),
            ('light', 'Light', ''),
            ('camera', 'Camera', ''),
            ('upgrade', 'Upgrade Module', ''),
            ('vent', 'Air Vent', ''),
            ('gear_lock', 'Landing Gear', ''),
            ('shiptool', 'Ship Tool', ''),
            ('electric_motor', 'Electric Motor', ''),
            ('character', 'Character', '')
            ),
        default='Connector'
    )

    def execute(self, context):

        print("SEUT Debug: OT AddDummy")

        if self.detectorType == 'conveyor':
            print("Conveyor")

        if self.detectorType == 'terminal':
            print("Terminal")

        return {'FINISHED'}
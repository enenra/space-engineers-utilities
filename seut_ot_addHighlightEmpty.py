import bpy

from bpy.types  import Operator
from bpy.props  import EnumProperty

class SEUT_OT_AddHighlightEmpty(Operator):
    """Add highlight empty to selected object"""
    bl_idname = "object.add_highlight_empty"
    bl_label = "Add Highlight Empty"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    detectorType: EnumProperty(
        name='Highlight Type',
        items=(
            ('conveyor', 'Conveyor', 'Defines large conveyor access point.'),
            ('conveyor_small', 'Small Conveyor', 'Small Conveyor, Defines small conveyor access point.'),
            ('terminal', 'Terminal', 'Defines terminal access point.'),
            ('button', 'Button', 'Defines access points for single buttons.'),
            ('cockpit', 'Cockpit', 'Defines access point to block that can be entered.'),
            ('door', 'Door', 'Defines door access point.'),
            ('advanceddoor', 'Advanced Door', 'Defines advanced door access point.'),
            ('block', 'Medical Station', 'Defines access point to part of medical station that allows for health / o2 / h2 / energy regeneration.'),
            ('wardrobe', 'Wardrobe', 'Defines access point to part of medical station that allows the switching of skins.')
            ),
        default='conveyor'
    )

    def execute(self, context):

        print("SEUT Debug: OT AddHighlightEmpty")

        if self.detectorType == 'conveyor':
            print("Conveyor")

        if self.detectorType == 'terminal':
            print("Terminal")

        return {'FINISHED'}
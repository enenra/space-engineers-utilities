import bpy

from bpy.types  import Operator, Menu


class SEUT_MT_ContextMenu(Menu):
    """Creates the 'Create Emtpy' context menu"""
    bl_idname = "SEUT_MT_ContextMenu"
    bl_label = "    Create Empty"

    def draw(self, context):
        layout = self.layout

        layout.operator('object.add_highlight_empty', text="Add Highlight Empty")
        layout.operator('object.add_dummy', text="Add Dummy")
        layout.operator('object.add_preset_subpart', text="Add Preset Subpart")
        layout.operator('object.add_custom_subpart', text="Add Custom Subpart")
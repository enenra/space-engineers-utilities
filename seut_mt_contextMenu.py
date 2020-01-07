import bpy

from bpy.types  import Operator, Menu


class SEUT_MT_ContextMenu(Menu):
    """Creates the SEUT context menu"""
    bl_idname = "SEUT_MT_ContextMenu"
    bl_label = "SEUT: Create Empty"

    def draw(self, context):
        layout = self.layout

        layout.operator('object.emptytocubetype', text="Display Empties as 'Cube'")
        layout.operator('object.remapmaterials', text="Remap Materials")
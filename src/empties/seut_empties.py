import bpy

from bpy.types  import Operator, Menu
from bpy.types  import Panel


empty_types = {
    'subpart_': 'ARROWS',
    'thruster_flame': 'CONE',
    'muzzle_missile': 'CONE',
    'muzzle_projectile': 'CONE',
    'camera': 'CONE',
}


class SEUT_MT_ContextMenu(Menu):
    """Creates the 'Create Emtpy' context menu"""
    bl_idname = "SEUT_MT_ContextMenu"
    bl_label = "    Create Empty"


    def draw(self, context):
        layout = self.layout

        layout.operator('object.add_highlight_empty', text="Add Highlight Empty")
        layout.operator('scene.add_dummy', text="Add Dummy")
        layout.operator('scene.add_preset_subpart', text="Add Preset Subpart")
        layout.operator('scene.add_custom_subpart', text="Add Custom Subpart")


class SEUT_PT_EmptyLink(Panel):
    """Creates the Empty Properties menu"""

    bl_idname = "SEUT_PT_EmptyLink"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'


    # Only display this panel if active object is of type empty and has either 'file' or 'highlight' as a custom property
    @classmethod
    def poll(cls, context):
        return bpy.context.view_layer.objects.active.type == 'EMPTY' and ('file' in bpy.context.view_layer.objects.active or 'highlight' in bpy.context.view_layer.objects.active)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        empty = context.view_layer.objects.active

        if 'file' in empty:
            layout.label(text="Subpart Scene:")
            split = layout.split(factor=0.92)
            split.prop(empty.seut, 'linkedScene', text="",)
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials'
            link.page = 'subparts'

        elif 'highlight' in empty:
            layout.label(text="Highlight Object:")
            split = layout.split(factor=0.92)
            split.prop(empty.seut, 'linkedObject', text="",)
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials'
            link.page = 'interaction-highlights'
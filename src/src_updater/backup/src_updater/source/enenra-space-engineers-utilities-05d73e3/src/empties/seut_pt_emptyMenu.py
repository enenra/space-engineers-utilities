import bpy

from bpy.types  import Panel

class SEUT_PT_EmptyLink(Panel):
    """Creates the Empty Properties menu"""
    bl_idname = "SEUT_PT_EmptyLink"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

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
            layout.prop(empty.seut, 'linkedScene', text="",)

        elif 'highlight' in empty:
            layout.label(text="Highlight Object:")
            layout.prop(empty.seut, 'linkedObject', text="",)

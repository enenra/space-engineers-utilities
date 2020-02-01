import bpy

from bpy.types      import Panel


class SEUT_PT_Panel_MatLib(Panel):
    """Creates the MatLib linking panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_MatLib"
    bl_label = "Space Engineers Utilities"
    bl_category = "Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        rows = 2
        row = layout.row()
        row.template_list('SEUT_UL_MatLib', "", wm , 'matlibs', wm , 'matlib_index', rows=rows)
        layout.operator('scene.refresh_matlibs', icon='FILE_REFRESH')
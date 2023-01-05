import bpy

from bpy.types  import Panel, UIList


class SEUT_UL_Animations(UIList):
    """Creates the Animations UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.85)
        row = split.row()
        row.label(text=item.ore_type, icon='TEXTURE_DATA')

        colors = context.scene.seut.ore_mappings_palette.colors
        for c in colors:
            if int(round(c.color[2] * 255, 0)) == item.value:
                split.prop(c, 'color', text="")
                break

    def invoke(self, context, event):
        pass


class SEUT_PT_Panel_Animation(Panel):
    """Creates the Animation menu"""
    bl_idname = "SEUT_PT_Panel_Animation"
    bl_label = "Animations"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['main', 'subpart'] and 'SEUT' in scene.view_layers


    def draw(self, context):
        scene = context.scene
        layout = self.layout

        
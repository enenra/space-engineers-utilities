import bpy
import json

from bpy.types  import Panel, UIList
from distutils.fancy_getopt import wrap_text

from ..utils.seut_patch_blend       import check_patch_needed
from ..seut_utils                   import get_seut_blend_data, get_preferences



class SEUT_UL_Animations(UIList):
    """Creates the Animation Sets UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, icon='SEQ_STRIP_META')

    def invoke(self, context, event):
        pass


class SEUT_UL_AnimationObjects(UIList):
    """Creates the Animation Objects UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon='DOT')
        row.prop(item, "obj", text="")

    def invoke(self, context, event):
        pass


class SEUT_PT_Panel_Animation(Panel):
    """Creates the Animation menu"""
    bl_idname = "SEUT_PT_Panel_Animation"
    bl_label = "Animation"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers and not check_patch_needed() and get_preferences().animation


    def draw(self, context):
        data = get_seut_blend_data()
        layout = self.layout

        # Animation Sets
        box = layout.box()
        box.label(text="Animation Sets", icon='SEQ_STRIP_META')

        row = box.row()
        row.template_list("SEUT_UL_Animations", "", data.seut, "animations", data.seut, "animations_index", rows=3)
        col = row.column(align=True)
        col.operator("animation.add_animation", icon='ADD', text="")
        col.operator("animation.remove_animation", icon='REMOVE', text="")

        if len(data.seut.animations) > 0:
            animation_set = data.seut.animations[data.seut.animations_index]

            if animation_set is not None:
                box2 = box.box()
                box2.label(text="Subpart Empties", icon='EMPTY_DATA')

                row = box2.row()
                row.template_list("SEUT_UL_AnimationObjects", "", animation_set, "subparts", animation_set, "subparts_index", rows=3)
                col = row.column(align=True)
                col.operator("animation.add_subpart_empty", icon='ADD', text="")
                col.operator("animation.remove_subpart_empty", icon='REMOVE', text="")

                if len(animation_set.subparts) > 0:
                    subpart_empty = animation_set.subparts[animation_set.subparts_index]
                    box2.template_ID(subpart_empty, "action", new="animation.add_action", unlink="animation.remove_action")


class SEUT_PT_Panel_Keyframes(Panel):
    """Creates the Animation menu"""
    bl_label = "Space Engineers Utilities"
    bl_category = "F-Curve"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        bezier = any(k.interpolation == 'BEZIER' for k in bpy.context.active_editable_fcurve.keyframe_points)
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers and bpy.context.active_editable_fcurve is not None and bezier and get_preferences().animation


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.alert = True
        ui_scale = context.preferences.system.ui_scale
        width = context.region.width
        row.label(text="Incompatible Interpolation", icon='ERROR')
        text = "One or more Keyframes use 'Bezier' interpolation, which is not supported by the Animation Engine and will be automatically changed to 'Linear' on export."
        box = layout.box()
        for l in wrap_text(text, int((width / ui_scale) / 6.75)):
            row = box.row()
            row.alert = True
            row.scale_y = 0.75
            row.label(text=l)

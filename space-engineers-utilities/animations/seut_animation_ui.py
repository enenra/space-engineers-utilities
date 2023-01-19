import bpy

from bpy.types  import Panel, UIList
from distutils.fancy_getopt import wrap_text

from ..utils.seut_patch_blend       import check_patch_needed
from ..seut_utils                   import get_seut_blend_data

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


class SEUT_UL_AnimationTriggers(UIList):
    """Creates the Animation Trigger UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon='DOT')
        row.prop(item, "trigger_type", text="")

    def invoke(self, context, event):
        pass


class SEUT_UL_AnimationFunctions(UIList):
    """Creates the Animation Function UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text="", icon='DOT')
        row.prop(item, "function_type", text="")

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
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers and not check_patch_needed()


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
                    
                box3 = box.box()
                box3.label(text="Animation Triggers", icon='STYLUS_PRESSURE')
                
                row = box3.row()
                row.template_list("SEUT_UL_AnimationTriggers", "", animation_set, "triggers", animation_set, "triggers_index", rows=3)
                col = row.column(align=True)
                col.operator("animation.add_trigger", icon='ADD', text="")
                col.operator("animation.remove_trigger", icon='REMOVE', text="")

                if len(animation_set.triggers) > 0:
                    trigger = animation_set.triggers[animation_set.triggers_index]

                    if trigger is not None:

                        if trigger.trigger_type in ['PressedOn', 'PressedOff', 'Pressed']:
                            box3.prop(trigger, "Pressed_empty", icon='EMPTY_DATA')

                        elif trigger.trigger_type in ['Arrive', 'Leave']:
                            box3.prop(trigger, "distance")
                            
                        elif trigger.trigger_type == 'Working':
                            row = box3.row(align=True)
                            row.prop(trigger, "Working_bool", icon='QUESTION')
                            row.prop(trigger, "Working_loop", icon='RECOVER_LAST')
                            
                        elif trigger.trigger_type == 'Producing':
                            row = box3.row(align=True)
                            row.prop(trigger, "Producing_bool", icon='QUESTION')
                            row.prop(trigger, "Producing_loop", icon='RECOVER_LAST')


class SEUT_PT_Panel_Keyframes(Panel):
    """Creates the Animation menu"""
    bl_label = "Space Engineers Utilities"
    bl_category = "F-Curve"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers and bpy.context.active_editable_fcurve is not None


    def draw(self, context):
        fcurve = bpy.context.active_editable_fcurve
        keyframes = fcurve.keyframe_points
        layout = self.layout

        bezier = any(k.interpolation == 'BEZIER' for k in keyframes)
        if bezier:
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

        count = 0
        for k in keyframes:
            if k.select_control_point == True:
                count += 1
                keyframe = k

        if count <= 1:
            action = context.active_object.animation_data.action
            active_keyframe = next(
                (k for k in fcurve.keyframe_points if k.select_control_point == True), None
            )

            seut_kf = next(
                (k for k in action.seut.keyframes if k.name == str(active_keyframe)), None
            )
            if seut_kf is None:
                layout.operator("animation.add_function", icon='ADD')
                return

            if len(seut_kf.functions) <= 0:
                layout.operator("animation.add_function", icon='ADD')

            else:
                box = layout.box()
                box.label(text="Functions", icon='CONSOLE')

                row = box.row()
                row.template_list("SEUT_UL_AnimationFunctions", "", seut_kf, "functions", seut_kf, "functions_index", rows=3)
                col = row.column(align=True)
                col.operator("animation.add_function", icon='ADD', text="")
                col.operator("animation.remove_function", icon='REMOVE', text="")

                kf_function = seut_kf.functions[seut_kf.functions_index]
                if kf_function is not None:
                    
                    if kf_function.function_type == 'setVisible':
                        box.prop(kf_function, 'setVisible_bool', icon='HIDE_OFF')
                        box.prop(kf_function, 'setVisible_empty')

                    elif kf_function.function_type == 'setEmissiveColor':
                        box.prop(kf_function, 'setEmissiveColor_material')
                        box.prop(kf_function, 'setEmissiveColor_rgb', text="")
                        box.prop(kf_function, 'setEmissiveColor_brightness')

                    elif kf_function.function_type == 'playParticle':
                        box.prop(kf_function, 'playParticle_empty')
                        box.prop(kf_function, 'playParticle_subtypeid')

                    elif kf_function.function_type == 'stopParticle':
                        box.prop(kf_function, 'stopParticle_empty')
                        box.prop(kf_function, 'stopParticle_subtypeid')

                    elif kf_function.function_type == 'playSound':
                        box.prop(kf_function, 'playSound_subtypeid')

                    elif kf_function.function_type == 'stopSound':
                        box.prop(kf_function, 'stopSound_subtypeid')

                    elif kf_function.function_type == 'setLightColor':
                        box.prop(kf_function, 'setLightColor_empty')
                        box.prop(kf_function, 'setLightColor_rgb', text="")

                    elif kf_function.function_type in ['lightOn', 'lightOff', 'toggleLight']:
                        box.prop(kf_function, 'light_empty')
import bpy
import os

from bpy.types              import Operator
from bpy.props              import (EnumProperty,
                                    FloatProperty,
                                    FloatVectorProperty,
                                    IntProperty,
                                    StringProperty,
                                    BoolProperty,
                                    PointerProperty,
                                    CollectionProperty
                                    )
from bpy_extras.io_utils    import ImportHelper

from ..seut_preferences import get_preferences
from ..seut_collections import get_collections
from ..seut_errors      import get_abs_path, seut_report

from .seut_animation_utils  import *


class SEUT_OT_Animation_Add(Operator):
    """Adds an Animation to the Animation UL"""
    bl_idname = "animation.add_animation"
    bl_label = "Add Animation"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        wm = context.window_manager
    
        item = wm.seut.animations.add()
        item.name = "Animation Set"

        return {'FINISHED'}


class SEUT_OT_Animation_Remove(Operator):
    """Removes an Animation to the Animation UL"""
    bl_idname = "animation.remove_animation"
    bl_label = "Remove Animation"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        wm = context.window_manager

        wm.seut.animations.remove(wm.seut.animations_index)
        wm.seut.animations_index = min(max(0, wm.seut.animations_index - 1), len(wm.seut.animations) - 1)

        return {'FINISHED'}


class SEUT_OT_Animation_SubpartEmpty_Add(Operator):
    """Adds a slot to the Subpart Empty UL"""
    bl_idname = "animation.add_subpart_empty"
    bl_label = "Add Subpart Empty"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        wm = context.window_manager
        animation_set = wm.seut.animations[wm.seut.animations_index]

        item = animation_set.subparts.add()

        return {'FINISHED'}


class SEUT_OT_Animation_SubpartEmpty_Remove(Operator):
    """Removes a slot from the Subpart Empty UL"""
    bl_idname = "animation.remove_subpart_empty"
    bl_label = "Remove Subpart Empty"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        wm = context.window_manager
        animation_set = wm.seut.animations[wm.seut.animations_index]

        animation_set.subparts.remove(animation_set.subparts_index)
        animation_set.subparts_index = min(max(0, animation_set.subparts_index - 1), len(animation_set.subparts) - 1)

        return {'FINISHED'}


class SEUT_OT_Animation_Trigger_Add(Operator):
    """Adds a slot to the Animation Trigger UL"""
    bl_idname = "animation.add_trigger"
    bl_label = "Add Animation Trigger"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        wm = context.window_manager
        animation_set = wm.seut.animations[wm.seut.animations_index]

        item = animation_set.triggers.add()
        item.name = item.trigger_type

        return {'FINISHED'}


class SEUT_OT_Animation_Trigger_Remove(Operator):
    """Removes a slot from the Animation Trigger UL"""
    bl_idname = "animation.remove_trigger"
    bl_label = "Remove Animation Trigger"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        wm = context.window_manager
        animation_set = wm.seut.animations[wm.seut.animations_index]

        animation_set.triggers.remove(animation_set.triggers_index)
        animation_set.triggers_index = min(max(0, animation_set.triggers_index - 1), len(animation_set.triggers) - 1)

        return {'FINISHED'}


class SEUT_OT_Animation_Function_Add(Operator):
    """Associates the selected Keyframe with a function"""
    bl_idname = "animation.add_function"
    bl_label = "Add Animation Function"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        action = context.active_object.animation_data.action
        active_fcurve = bpy.context.active_editable_fcurve
        active_keyframe = next(
            (k for k in active_fcurve.keyframe_points if k.select_control_point == True), None
        )

        seut_kf = get_or_create_prop(action.seut.keyframes, active_keyframe)

        item = seut_kf.functions.add()
        item.name = item.function_type

        collection_property_cleanup(action.seut.keyframes)

        return {'FINISHED'}


class SEUT_OT_Animation_Function_Remove(Operator):
    """Removes a function from the selected Keyframe"""
    bl_idname = "animation.remove_function"
    bl_label = "Remove Animation Function"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        action = context.active_object.animation_data.action
        active_fcurve = bpy.context.active_editable_fcurve
        active_keyframe = next(
            (k for k in active_fcurve.keyframe_points if k.select_control_point == True), None
        )
        seut_kf = next(
            (k for k in action.seut.keyframes if k.name == str(active_keyframe)), None
        )

        seut_kf.functions.remove(seut_kf.functions_index)
        seut_kf.functions_index = min(max(0, seut_kf.functions_index - 1), len(seut_kf.functions) - 1)
        
        collection_property_cleanup(action.seut.keyframes)

        return {'FINISHED'}
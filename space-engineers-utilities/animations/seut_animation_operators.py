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

from ..seut_errors      import get_abs_path
from ..seut_utils       import get_seut_blend_data

from .seut_animation_io     import *


class SEUT_OT_Animation_Export(Operator):
    """Exports all Animation Sets to the Mod Folder"""
    bl_idname = "animation.export"
    bl_label = "Export Animation Sets"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        data = get_seut_blend_data()
        scene = context.scene

        if scene.seut.sceneType != 'mainScene':
            Operator.poll_message_set("Animations can only be exported from main scenes.")
            return False
        elif 'SEUT' in scene.view_layers:
            if not os.path.exists(get_abs_path(scene.seut.mod_path)):
                Operator.poll_message_set("Mod must first be defined.")
                return False
            elif len(data.seut.animations) < 1:
                Operator.poll_message_set("There are no Animation Sets in this BLEND file.")
                return False
            return True


    def execute(self, context):

        result = export_animation_xml(self, context)

        return result


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
        data = get_seut_blend_data()
    
        item = data.seut.animations.add()
        item.name = "Animation Set"

        if len(data.seut.animations) > 1:
            idx = 2
            while f"Animation Set {idx}" in data.seut.animations:
                idx += 1
            item.name = f"Animation Set {idx}"

        return {'FINISHED'}


class SEUT_OT_Animation_Remove(Operator):
    """Removes an Animation from the Animation UL"""
    bl_idname = "animation.remove_animation"
    bl_label = "Remove Animation"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        data = get_seut_blend_data()

        data.seut.animations.remove(data.seut.animations_index)
        data.seut.animations_index = min(max(0, data.seut.animations_index - 1), len(data.seut.animations) - 1)

        return {'FINISHED'}


class SEUT_OT_Animation_Update(Operator):
    """Propagates the changes to the Animation Set to all subparts"""
    bl_idname = "animation.update_animation"
    bl_label = "Propagate Changes"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        from ..seut_text import update_animations_index
        update_animations_index(self, context)

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
        data = get_seut_blend_data()

        animation_set = data.seut.animations[data.seut.animations_index]
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
        data = get_seut_blend_data()
        animation_set = data.seut.animations[data.seut.animations_index]

        animation_set.subparts.remove(animation_set.subparts_index)
        animation_set.subparts_index = min(max(0, animation_set.subparts_index - 1), len(animation_set.subparts) - 1)

        return {'FINISHED'}


class SEUT_OT_Animation_Action_Add(Operator):
    """Adds an action to the subpart empty"""
    bl_idname = "animation.add_action"
    bl_label = "Add Action"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        data = get_seut_blend_data()
        animation_set = data.seut.animations[data.seut.animations_index]
        subpart_empty = animation_set.subparts[animation_set.subparts_index]

        subpart_empty.obj.animation_data_create()
        action = bpy.data.actions.new("Action")
        subpart_empty.obj.animation_data.action = action
        subpart_empty.action = action

        return {'FINISHED'}


class SEUT_OT_Animation_Action_Remove(Operator):
    """Removes an action from the subpart empty"""
    bl_idname = "animation.remove_action"
    bl_label = "Remove Action"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart'] and 'SEUT' in scene.view_layers


    def execute(self, context):
        data = get_seut_blend_data()
        animation_set = data.seut.animations[data.seut.animations_index]
        subpart_empty = animation_set.subparts[animation_set.subparts_index]
        
        subpart_empty.obj.animation_data.action = None
        subpart_empty.action = None

        return {'FINISHED'}
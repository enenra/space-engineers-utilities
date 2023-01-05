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


class SEUT_OT_Animation_Add(Operator):
    """Adds an Animation to the Animation UL"""
    bl_idname = "animation.add_animation"
    bl_label = "Add Animation"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        
        add_material_group(context)

        return {'FINISHED'}


class SEUT_OT_Animation_Remove(Operator):
    """Removes an Animation to the Animation UL"""
    bl_idname = "animation.remove_animation"
    bl_label = "Remove Animation"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        scene.seut.material_groups.remove(scene.seut.material_groups_index)
        
        for c in scene.seut.material_groups_palette.colors:
            found = False
            for mg in scene.seut.material_groups:
                if mg.value == int(round(c.color[0] * 255)) and c.color[1] == 0 and c.color[2] == 0:
                    found = True
            if not found:
                scene.seut.material_groups_palette.colors.remove(c)


        return {'FINISHED'}
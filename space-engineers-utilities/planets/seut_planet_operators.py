import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty,
                        CollectionProperty
                        )


class SEUT_OT_Planet_MaterialGroup_Add(Operator):
    """Adds a Material Group to a Planet"""
    bl_idname = "planet.add_material_group"
    bl_label = "Add Material Group"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):

        return {'FINISHED'}


class SEUT_OT_Planet_MaterialGroup_Remove(Operator):
    """Removes a Material Group from a Planet"""
    bl_idname = "planet.remove_material_group"
    bl_label = "Remove Material Group"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):

        return {'FINISHED'}
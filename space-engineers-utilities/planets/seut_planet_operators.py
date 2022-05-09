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
        scene = context.scene
        
        item = scene.seut.material_groups.add()
        item.name = "MaterialGroup"

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
        scene = context.scene

        scene.seut.material_groups.remove(scene.seut.material_groups_index)

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRule_Add(Operator):
    """Adds a Distribution Rule"""
    bl_idname = "planet.add_distribution_rule"
    bl_label = "Add Distribution Rule"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        item = rule_type.rules.add()
        item.name = "Rule " + str(len(rule_type.rules))

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRule_Remove(Operator):
    """Removes a Distribution Rule"""
    bl_idname = "planet.remove_distribution_rule"
    bl_label = "Remove Distribution Rule"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        rule_type.rules.remove(rule_type.rules_index)

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRuleLayer_Add(Operator):
    """Adds a Distribution Rule Layer"""
    bl_idname = "planet.add_distribution_rule_layer"
    bl_label = "Add Distribution Rule Layer"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        rule = rule_type.rules[rule_type.rules_index]

        item = rule.layers.add()
        item.material = "LayerMaterial"

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRuleLayer_Remove(Operator):
    """Removes a Distribution Rule Layer"""
    bl_idname = "planet.remove_distribution_rule_layer"
    bl_label = "Remove Distribution Rule Layer"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        rule = rule_type.rules[rule_type.rules_index]

        rule.layers.remove(rule.layers_index)

        return {'FINISHED'}


class SEUT_OT_Planet_EnvironmentItem_Add(Operator):
    """Adds an Environment Item"""
    bl_idname = "planet.add_environment_item"
    bl_label = "Add Environment Item"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        item = scene.seut.environment_items.add()
        item.name = "EnvironmentItem"

        return {'FINISHED'}


class SEUT_OT_Planet_EnvironmentItem_Remove(Operator):
    """Removes an Environment Item"""
    bl_idname = "planet.remove_environment_item"
    bl_label = "Remove Environment Item"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        scene.seut.environment_items.remove(scene.seut.environment_items_index)

        return {'FINISHED'}


class SEUT_OT_Planet_Biome_Add(Operator):
    """Adds a Biome"""
    bl_idname = "planet.add_biome"
    bl_label = "Add Biome"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        item = environment_item.biomes.add()
        item.value = len(environment_item.biomes)

        return {'FINISHED'}


class SEUT_OT_Planet_Biome_Remove(Operator):
    """Removes a Biome"""
    bl_idname = "planet.remove_biome"
    bl_label = "Remove Biome"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        environment_item.biomes.remove(environment_item.biomes_index)

        return {'FINISHED'}


class SEUT_OT_Planet_Material_Add(Operator):
    """Adds a Material"""
    bl_idname = "planet.add_material"
    bl_label = "Add Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        item = environment_item.materials.add()
        item.name = "VoxelMaterial"

        return {'FINISHED'}


class SEUT_OT_Planet_Material_Remove(Operator):
    """Removes a Material"""
    bl_idname = "planet.remove_material"
    bl_label = "Remove Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        environment_item.materials.remove(environment_item.materials_index)

        return {'FINISHED'}


class SEUT_OT_Planet_OreMappings_Add(Operator):
    """Adds an Ore Mapping to a Planet"""
    bl_idname = "planet.add_ore_mapping"
    bl_label = "Add Ore Mapping"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        item = scene.seut.ore_mappings.add()
        item.value = len(scene.seut.ore_mappings)

        return {'FINISHED'}


class SEUT_OT_Planet_OreMappings_Remove(Operator):
    """Removes an Ore Mapping from a Planet"""
    bl_idname = "planet.remove_ore_mapping"
    bl_label = "Remove Ore Mapping"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        scene.seut.ore_mappings.remove(scene.seut.ore_mappings_index)

        return {'FINISHED'}
from ast import Index
from msilib.schema import Icon
import bpy

from bpy.types  import Panel, UIList


class SEUT_UL_PlanetDistributionRulesLayers(UIList):
    """Creates the Planet Distribution Rules Layers UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.material}", icon='LAYER_ACTIVE')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetDistributionRules(UIList):
    """Creates the Planet Distribution Rules UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.name}", icon='SYSTEM')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetMaterialGroups(UIList):
    """Creates the Planet Material Groups UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.name} ({str(item.value)})", icon='MATERIAL_DATA')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetBiomes(UIList):
    """Creates the Planet Biomes UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=str(item.value), icon='WORLD_DATA')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetMaterials(UIList):
    """Creates the Planet Materials UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=item.name, icon='MATERIAL')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetEnvironmentItems(UIList):
    """Creates the Planet Environment Items UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.name}", icon='SCENE_DATA')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetOreMappings(UIList):
    """Creates the Planet Ore Mappings UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.value} ({str(item.ore_type)})", icon='PROPERTIES')

    def invoke(self, context, event):
        pass


class SEUT_PT_Panel_Planet(Panel):
    """Creates the Planet menu"""
    bl_idname = "SEUT_PT_Panel_Planet"
    bl_label = "Planet"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout


class SEUT_PT_Panel_PlanetComplexMaterials(Panel):
    """Creates the Planet Complex Materials menu"""
    bl_idname = "SEUT_PT_Panel_PlanetComplexMaterials"
    bl_label = "Complex Materials"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="Material Groups", icon='MATERIAL_DATA')
        row = box.row()
        row.template_list("SEUT_UL_PlanetMaterialGroups", "", scene.seut, "material_groups", scene.seut, "material_groups_index", rows=3)

        col = row.column(align=True)
        col.operator("planet.add_material_group", icon='ADD', text="")
        col.operator("planet.remove_material_group", icon='REMOVE', text="")

        if len(scene.seut.material_groups) > 0:
            try:
                material_group = scene.seut.material_groups[scene.seut.material_groups_index]
                box.prop(material_group, 'name')
                box.prop(material_group, 'value')
                box.separator()

                if material_group is not None:
                    box2 = box.box()
                    box2.label(text="Distribution Rules", icon='SYSTEM')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetDistributionRules", "", material_group, "rules", material_group, "rules_index", rows=3)

                    col = row.column(align=True)
                    op = col.operator("planet.add_distribution_rule", icon='ADD', text="")
                    op.rule_type = 'material_group'
                    op = col.operator("planet.remove_distribution_rule", icon='REMOVE', text="")
                    op.rule_type = 'material_group'

                    if len(material_group.rules) > 0:
                        try:
                            rule = material_group.rules[material_group.rules_index]
                            box2.prop(rule, 'name')
                            box2.prop(rule, 'height_min')
                            box2.prop(rule, 'height_max')
                            box2.prop(rule, 'latitude_min')
                            box2.prop(rule, 'latitude_max')
                            box2.prop(rule, 'slope_min')
                            box2.prop(rule, 'slope_max')
                            box2.separator()

                            if rule is not None:
                                box3 = box2.box()
                                box3.label(text="Layers", icon='LAYER_ACTIVE')
                                row = box3.row()
                                row.template_list("SEUT_UL_PlanetDistributionRulesLayers", "", rule, "layers", rule, "layers_index", rows=3)

                                col = row.column(align=True)
                                op = col.operator("planet.add_distribution_rule_layer", icon='ADD', text="")
                                op.rule_type = 'material_group'
                                op = col.operator("planet.remove_distribution_rule_layer", icon='REMOVE', text="")
                                op.rule_type = 'material_group'

                                if len(rule.layers) > 0:
                                    try:
                                        layer = rule.layers[rule.layers_index]
                                        box3.prop(layer, 'material')
                                        box3.prop(layer, 'depth')
                                    except IndexError:
                                        pass
                        
                        except IndexError:
                            pass

            except IndexError:
                pass


class SEUT_PT_Panel_PlanetEnvironmentItems(Panel):
    """Creates the Planet Environment Items menu"""
    bl_idname = "SEUT_PT_Panel_PlanetEnvironmentItems"
    bl_label = "Environment Items"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene


        box = layout.box()
        box.label(text="Environment Items", icon='SCENE_DATA')
        row = box.row()
        row.template_list("SEUT_UL_PlanetEnvironmentItems", "", scene.seut, "environment_items", scene.seut, "environment_items_index", rows=3)

        col = row.column(align=True)
        col.operator("planet.add_environment_item", icon='ADD', text="")
        col.operator("planet.remove_environment_item", icon='REMOVE', text="")

        if len(scene.seut.environment_items) > 0:
            try:
                environment_item = scene.seut.environment_items[scene.seut.environment_items_index]
                box.prop(environment_item, 'name')

                if environment_item is not None:
                    box2 = box.box()
                    box2.label(text="Biomes", icon='WORLD_DATA')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetBiomes", "", environment_item, "biomes", environment_item, "biomes_index", rows=3)

                    col = row.column(align=True)
                    col.operator("planet.add_biome", icon='ADD', text="")
                    col.operator("planet.remove_biome", icon='REMOVE', text="")

                    if len(environment_item.biomes) > 0:
                        try:
                            biome = environment_item.biomes[environment_item.biomes_index]
                            box2.prop(biome, 'value')
                        except IndexError:
                            pass

                    box2 = box.box()
                    box2.label(text="Materials", icon='MATERIAL')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetMaterials", "", environment_item, "materials", environment_item, "materials_index", rows=3)

                    col = row.column(align=True)
                    col.operator("planet.add_material", icon='ADD', text="")
                    col.operator("planet.remove_material", icon='REMOVE', text="")

                    if len(environment_item.materials) > 0:
                        try:
                            material = environment_item.materials[environment_item.materials_index]
                            box2.prop(material, 'name')
                        except IndexError:
                            pass
                    
                    box2 = box.box()
                    box2.label(text="Distribution Rules", icon='SYSTEM')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetDistributionRules", "", environment_item, "rules", environment_item, "rules_index", rows=3)

                    col = row.column(align=True)
                    op = col.operator("planet.add_distribution_rule", icon='ADD', text="")
                    op.rule_type = 'environment_item'
                    op = col.operator("planet.remove_distribution_rule", icon='REMOVE', text="")
                    op.rule_type = 'environment_item'

                    if len(environment_item.rules) > 0:
                        try:
                            rule = environment_item.rules[environment_item.rules_index]

                            box2.prop(rule, 'name')
                            box2.prop(rule, 'height_min')
                            box2.prop(rule, 'height_max')
                            box2.prop(rule, 'latitude_min')
                            box2.prop(rule, 'latitude_max')
                            box2.prop(rule, 'slope_min')
                            box2.prop(rule, 'slope_max')
                            box2.separator()

                            if rule is not None:
                                box3 = box2.box()
                                box3.label(text="Layers", icon='LAYER_ACTIVE')
                                row = box3.row()
                                row.template_list("SEUT_UL_PlanetDistributionRulesLayers", "", rule, "layers", rule, "layers_index", rows=3)

                                col = row.column(align=True)
                                op = col.operator("planet.add_distribution_rule_layer", icon='ADD', text="")
                                op.rule_type = 'environment_item'
                                op = col.operator("planet.remove_distribution_rule_layer", icon='REMOVE', text="")
                                op.rule_type = 'environment_item'

                                if len(rule.layers) > 0:
                                    try:
                                        layer = rule.layers[rule.layers_index]
                                        box3.prop(layer, 'material')
                                        box3.prop(layer, 'depth')
                                    except IndexError:
                                        pass

                        except IndexError:
                            pass

            except IndexError:
                pass


class SEUT_PT_Panel_PlanetOreMappings(Panel):
    """Creates the Planet Ore Mappings menu"""
    bl_idname = "SEUT_PT_Panel_PlanetOreMappings"
    bl_label = "Ore Mappings"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
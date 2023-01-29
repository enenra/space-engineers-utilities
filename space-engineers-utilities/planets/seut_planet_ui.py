import bpy

from bpy.types  import Panel, UIList


class SEUT_UL_PlanetDistributionRulesLayers(UIList):
    """Creates the Planet Distribution Rules Layers UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.65)
        row = split.row()
        row.label(text="", icon='ANCHOR_TOP')
        row.prop(item, 'material', text="")
        split.prop(item, 'depth', text="")

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetDistributionRules(UIList):
    """Creates the Planet Distribution Rules UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        row = layout.row()
        row.label(text="", icon='SYSTEM')
        row.prop(item, 'name', text="", emboss=False)

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetMaterialGroups(UIList):
    """Creates the Planet Material Groups UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.85)
        row = split.row()
        row.label(text="", icon='MATERIAL_DATA')
        row.prop(item, 'name', text="", emboss=False)

        colors = context.scene.seut.material_groups_palette.colors
        for c in colors:
            if int(round(c.color[0] * 255, 0)) == item.value:
                split.prop(c, 'color', text="")
                break

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetBiomes(UIList):
    """Creates the Planet Biomes UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.85)
        row = split.row()
        row.label(text="", icon='WORLD_DATA')
        row.prop(item, 'value', text="")
        
        colors = context.scene.seut.biomes_palette.colors
        for c in colors:
            if int(round(c.color[1] * 255, 0)) == item.value:
                split.prop(c, 'color', text="")
                break

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetMaterials(UIList):
    """Creates the Planet Materials UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        row = layout.row()
        row.label(text="", icon='MATERIAL')
        row.prop(item, 'material', text="")

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetItems(UIList):
    """Creates the Planet Items UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        name = ""
        if item.subtype_id != "":
            name = item.subtype_id
        elif item.group_id != "":
            name = item.group_id
        layout.label(text=name, icon='RNA')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetEnvironmentItems(UIList):
    """Creates the Planet Environment Items UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        row = layout.row()
        row.label(text="", icon='SCENE_DATA')
        row.prop(item, 'name', text="", emboss=False)

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetOreMappings(UIList):
    """Creates the Planet Ore Mappings UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.85)
        row = split.row()
        row.label(text="", icon='TEXTURE_DATA')
        row.prop(item, 'ore_type', text="")

        colors = context.scene.seut.ore_mappings_palette.colors
        for c in colors:
            if int(round(c.color[2] * 255, 0)) == item.value:
                split.prop(c, 'color', text="")
                break

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
        scene = context.scene
        layout = self.layout

        row = layout.row()
        row.scale_y = 2.0
        row.operator('planet.recreate_setup', icon='MATSPHERE')

        layout.separator()

        box = layout.box()
        box.label(text="Surface Detail", icon='OUTLINER_DATA_LIGHTPROBE')
        box.prop(scene.seut, "sd_texture")
        box.prop(scene.seut, "sd_size")
        box.prop(scene.seut, "sd_scale")
        col = box.column(align=True)
        col.prop(scene.seut, "sd_slope_min")
        col.prop(scene.seut, "sd_slope_max")
        box.prop(scene.seut, "sd_transition")

        box = layout.box()
        box.label(text="Hill Parameters", icon='IPO_ELASTIC')
        col = box.column(align=True)
        col.prop(scene.seut, "hill_params_min", text="Minimum")
        col.prop(scene.seut, "hill_params_max", text="Maximum")

        # Voxel Defaults
        box = layout.box()
        box.label(text="Voxel Defaults", icon='FORCE_TEXTURE')
        box.prop(scene.seut, "default_surface_material", text="Surface")
        box.prop(scene.seut, "default_surface_material_max")
        box.prop(scene.seut, "default_subsurface_material", text="Subsurface")

        box.prop(scene.seut, "min_surface_layer_depth")

        # Atmosphere Settings
        box = layout.box()
        box.label(text="Atmosphere Settings", icon='PROP_OFF')
        
        box.prop(scene.seut, "default_surface_temperature", text="Temperature")

        col = box.column(align=True)
        col.prop(scene.seut, "surface_gravity")
        col.prop(scene.seut, "gravity_falloff_power")
        
        col = box.column(align=True)
        col.prop(scene.seut, "has_atmosphere", icon='PROP_CON')
        if scene.seut.has_atmosphere:
            col.prop(scene.seut, "atm_oxygen_density")
            col.prop(scene.seut, "atm_breathable", icon='FORCE_WIND')
            col.prop(scene.seut, "atm_density")
            col.prop(scene.seut, "atm_limit_altitude")
            col.prop(scene.seut, "atm_max_wind_speed")


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

        # Material Groups
        if len(scene.seut.material_groups) > 0:
            try:
                material_group = scene.seut.material_groups[scene.seut.material_groups_index]
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

                    # Distribution Rules
                    if len(material_group.rules) > 0:
                        try:
                            rule = material_group.rules[material_group.rules_index]

                            split = box2.split(factor=0.20)
                            split.label(text="Height:")
                            row = split.row(align=True)
                            row.prop(rule, 'height_min', text="Min")
                            row.prop(rule, 'height_max', text="Max")

                            split = box2.split(factor=0.20)
                            split.label(text="Latitude:")
                            row = split.row(align=True)
                            row.prop(rule, 'latitude_min', text="Min")
                            row.prop(rule, 'latitude_max', text="Max")

                            split = box2.split(factor=0.20)
                            split.label(text="Slope:")
                            row = split.row(align=True)
                            row.prop(rule, 'slope_min', text="Min")
                            row.prop(rule, 'slope_max', text="Max")

                            box2.separator()

                            if rule is not None:
                                box3 = box2.box()
                                box3.label(text="Voxel Layers", icon='ANCHOR_TOP')
                                row = box3.row()
                                row.template_list("SEUT_UL_PlanetDistributionRulesLayers", "", rule, "layers", rule, "layers_index", rows=3)

                                col = row.column(align=True)
                                op = col.operator("planet.add_distribution_rule_layer", icon='ADD', text="")
                                op.rule_type = 'material_group'
                                op = col.operator("planet.remove_distribution_rule_layer", icon='REMOVE', text="")
                                op.rule_type = 'material_group'
                        
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

        # Environment Items
        if len(scene.seut.environment_items) > 0:
            try:
                environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

                if environment_item is not None:
                    box2 = box.box()
                    box2.label(text="Biomes", icon='WORLD_DATA')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetBiomes", "", environment_item, "biomes", environment_item, "biomes_index", rows=3)

                    col = row.column(align=True)
                    col.operator("planet.add_biome", icon='ADD', text="")
                    col.operator("planet.remove_biome", icon='REMOVE', text="")

                    box2 = box.box()
                    box2.label(text="Voxels", icon='MATERIAL')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetMaterials", "", environment_item, "materials", environment_item, "materials_index", rows=3)

                    col = row.column(align=True)
                    col.operator("planet.add_material", icon='ADD', text="")
                    col.operator("planet.remove_material", icon='REMOVE', text="")

                    box2 = box.box()
                    box2.label(text="Items", icon='RNA')
                    row = box2.row()
                    row.template_list("SEUT_UL_PlanetItems", "", environment_item, "items", environment_item, "items_index", rows=3)

                    col = row.column(align=True)
                    col.operator("planet.add_item", icon='ADD', text="")
                    col.operator("planet.remove_item", icon='REMOVE', text="")

                    # Items
                    if len(environment_item.items) > 0:
                        try:
                            item = environment_item.items[environment_item.items_index]
                            box2.prop(item, 'type_id')
                            box2.prop(item, 'subtype_id')
                            box2.prop(item, 'group_id')
                            box2.prop(item, 'modifier_id')
                            box2.prop(item, 'density')
                        except IndexError:
                            pass
                    
                    # Distribution Rules
                    box2 = box.box()
                    box2.label(text="Distribution Rule", icon='SYSTEM')
                    
                    if len(environment_item.rules) > 0:
                        try:
                            rule = environment_item.rules[environment_item.rules_index]

                            split = box2.split(factor=0.20)
                            split.label(text="Height:")
                            row = split.row(align=True)
                            row.prop(rule, 'height_min', text="Min")
                            row.prop(rule, 'height_max', text="Max")

                            split = box2.split(factor=0.20)
                            split.label(text="Latitude:")
                            row = split.row(align=True)
                            row.prop(rule, 'latitude_min', text="Min")
                            row.prop(rule, 'latitude_max', text="Max")

                            split = box2.split(factor=0.20)
                            split.label(text="Slope:")
                            row = split.row(align=True)
                            row.prop(rule, 'slope_min', text="Min")
                            row.prop(rule, 'slope_max', text="Max")

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
        scene = context.scene

        box = layout.box()
        box.label(text="Ore Mappings", icon='TEXTURE_DATA')
        row = box.row()
        row.template_list("SEUT_UL_PlanetOreMappings", "", scene.seut, "ore_mappings", scene.seut, "ore_mappings_index", rows=3)

        col = row.column(align=True)
        col.operator("planet.add_ore_mapping", icon='ADD', text="")
        col.operator("planet.remove_ore_mapping", icon='REMOVE', text="")

        # Ore Mappings
        if len(scene.seut.ore_mappings) > 0:
            try:
                ore_mapping = scene.seut.ore_mappings[scene.seut.ore_mappings_index]
                box.prop(ore_mapping, 'value')
                col = box.column(align=True)
                col.prop(ore_mapping, 'start')
                col.prop(ore_mapping, 'depth')
                box.prop(ore_mapping, 'target_color')
            
            except IndexError:
                pass


class SEUT_PT_Panel_PlanetExport(Panel):
    """Creates the planet export panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_PlanetExport"
    bl_label = "Export & Bake"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export
        row = layout.row()
        row.scale_y = 2.0
        row.operator('planet.export_all', icon='EXPORT')

        # Options
        box = layout.box()
        box.label(text="Options", icon='SETTINGS')

        row = box.row()
        row.prop(scene.seut, "export_sbc_type", expand=True)

        row = box.row(align=True)
        row.prop(scene.seut, "export_map_height", text="Height", icon='BOIDS')
        row.prop(scene.seut, "export_map_biome", text="Biome", icon='WORLD_DATA')
        row.prop(scene.seut, "export_map_spots", text="Ore Spots", icon='OUTLINER_OB_POINTCLOUD')
        
        box.prop(scene.seut, "mod_path", text="Mod")

        layout.separator()

        # Bake
        row = layout.row()
        row.scale_y = 1.1
        row.operator('planet.bake', icon='OUTPUT')

        # Options
        box = layout.box()
        box.label(text="Options", icon='SETTINGS')
        
        row = box.row()
        row.prop(scene.seut, "bake_type", expand=True)
        split = box.split(factor=0.40)
        split.label(text="Resolution:")
        split.prop(scene.seut, "bake_resolution", text="")


class SEUT_PT_Panel_PlanetImport(Panel):
    """Creates the planet import panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_PlanetImport"
    bl_label = "Import"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 2.0
        row.operator('planet.import_sbc', icon='IMPORT')
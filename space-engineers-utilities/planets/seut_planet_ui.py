import bpy

from bpy.types  import Panel, UIList


class SEUT_UL_PlanetMaterialGroups(UIList):
    """Creates the Planet Material Groups UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.name} ({str(item.value)})", icon='PROPERTIES')

    def invoke(self, context, event):
        pass


class SEUT_UL_PlanetEnvironmentItems(UIList):
    """Creates the Planet Environment Items UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=f"{item.name}", icon='PROPERTIES')

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

        layout.label(text="Material Groups")
        row = layout.row()
        row.template_list("SEUT_UL_PlanetMaterialGroups", "", scene.seut, "material_groups", scene.seut, "material_groups_index", rows=3)

        col = row.column(align=True)
        col.operator("planet.add_material_group", icon='ADD', text="")
        col.operator("planet.remove_material_group", icon='REMOVE', text="")

        layout.separator()


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
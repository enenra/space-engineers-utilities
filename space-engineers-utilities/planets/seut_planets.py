import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty,
                        CollectionProperty
                        )


def update_material_groups_value(self, context):
    scene = context.scene
    palette = scene.seut.material_groups_palette

    for c in palette.colors:
        found = False
        for mg in scene.seut.material_groups:
            if round(mg.value / 255, 3) == round(c.color[0], 3) and c.color[1] == 0 and c.color[2] == 0:
                found = True
        if not found:
            palette.colors.remove(c)
    
    color = palette.colors.new()
    color.color[0] = round(self.value / 255, 3)
    color.color[1] = 0
    color.color[2] = 0


def update_biomes_value(self, context):
    scene = context.scene
    palette = scene.seut.biomes_palette

    for c in palette.colors:
        found = False
        for ei in scene.seut.environment_items:
            for biome in ei.biomes:
                if round(biome.value / 255, 3) == round(c.color[1], 3) and c.color[0] == 0 and c.color[2] == 0:
                    found = True
        if not found:
            palette.colors.remove(c)
    
    color = palette.colors.new()
    color.color[0] = 0
    color.color[1] = round(self.value / 255, 3)
    color.color[2] = 0


def update_ore_mappings_value(self, context):
    scene = context.scene
    palette = scene.seut.ore_mappings_palette

    for c in palette.colors:
        found = False
        for om in scene.seut.ore_mappings:
            if round(om.value / 255, 3) == round(c.color[2], 3) and c.color[0] == 0 and c.color[1] == 0:
                found = True
        if not found:
            palette.colors.remove(c)
    
    color = palette.colors.new()
    color.color[0] = 0
    color.color[1] = 0
    color.color[2] = round(self.value / 255, 3)


class SEUT_PlanetPropertiesDistributionRulesLayers(PropertyGroup):
    """Layer definitions of Material Group placement rules"""
    
    name: StringProperty()

    material: StringProperty(
        name="Material"
    )
    depth: IntProperty(
        name="Depth",
        default=0,
        min=1
    )


class SEUT_PlanetPropertiesDistributionRules(PropertyGroup):
    """Placement rules of Material Groups"""
    
    name: StringProperty(
        name="Name"
    )
    layers: CollectionProperty(
        type=SEUT_PlanetPropertiesDistributionRulesLayers
    )
    layers_index: IntProperty(
        default=0
    )
    height_min: FloatProperty(
        name="Height Min",
        default=0,
        min=0,
        max=1
    )
    height_max: FloatProperty(
        name="Height Max",
        default=0,
        min=0,
        max=1
    )
    latitude_min: FloatProperty(
        name="Latitude Min",
        default=0,
        min=-90,
        max=90
    )
    latitude_max: FloatProperty(
        name="Latitude Max",
        default=0,
        min=-90,
        max=90
    )
    slope_min: FloatProperty(
        name="Slope Min",
        default=0,
        min=0,
        max=90
    )
    slope_max: FloatProperty(
        name="Slope Max",
        default=0,
        min=0,
        max=90
    )


class SEUT_PlanetPropertiesMaterialGroups(PropertyGroup):
    """Material Groups of Complex Materials"""

    name: StringProperty(
        name="Name"
    )
    value: IntProperty(
        name="Value",
        default=0,
        min=0,
        max=255,
        update=update_material_groups_value
    )
    rules: CollectionProperty(
        type=SEUT_PlanetPropertiesDistributionRules
    )
    rules_index: IntProperty(
        default=0
    )


class SEUT_PlanetPropertiesBiomes(PropertyGroup):
    """Biomes of Environment Items"""

    name: StringProperty()

    value: IntProperty(
        name="Value",
        default=0,
        min=0,
        max=255,
        update=update_biomes_value
    )


class SEUT_PlanetPropertiesMaterials(PropertyGroup):
    """Materials of Environment Items"""

    name: StringProperty(
        name="Voxel Material"
    )


class SEUT_PlanetPropertiesItems(PropertyGroup):
    """Items defined for Environment Item entries"""

    name: StringProperty()

    type_id: StringProperty(
        name="TypeId"
    )
    subtype_id: StringProperty(
        name="SubtypeId"
    )
    density: FloatProperty(
        name="Density",
        min=0.01,
        max=1.00
    )


class SEUT_PlanetPropertiesEnvironmentItems(PropertyGroup):
    """Environment Item Entries"""
    
    name: StringProperty(
        name="Name"
    )
    biomes: CollectionProperty(
        type=SEUT_PlanetPropertiesBiomes
    )
    biomes_index: IntProperty(
        default=0
    )
    materials: CollectionProperty(
        type=SEUT_PlanetPropertiesMaterials
    )
    materials_index: IntProperty(
        default=0
    )
    items: CollectionProperty(
        type=SEUT_PlanetPropertiesItems
    )
    items_index: IntProperty(
        default=0
    )
    rules: CollectionProperty(
        type=SEUT_PlanetPropertiesDistributionRules
    )
    rules_index: IntProperty(
        default=0
    )


class SEUT_PlanetPropertiesOreMappings(PropertyGroup):
    """Ore Mapping Entries"""
    
    name: StringProperty()

    value: IntProperty(
        name="Value",
        default=0,
        min=0,
        max=255,
        update=update_ore_mappings_value
    )
    ore_type: StringProperty(
        name="Ore Type"
    )
    start: IntProperty(
        name="Start",
        default=0,
        min=0
    )
    depth: IntProperty(
        name="Depth",
        default=1,
        min=1
    )
    target_color: StringProperty(
        name="Target Color"
    )
    color_influence: IntProperty(
        name="Color Influence",
        default=0,
        min=0
    )
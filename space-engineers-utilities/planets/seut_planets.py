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


class SEUT_PlanetPropertiesDistributionRulesLayers(PropertyGroup):
    """Layer definitions of Material Group placement rules"""
    
    name: StringProperty()

    material: StringProperty(
        name="Material"
    )
    depth: IntProperty(
        name="Depth"
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
    height_min: IntProperty(
        name="Height Min"
    )
    height_max: IntProperty(
        name="Height Max"
    )
    latitude_min: IntProperty(
        name="Latitude Min"
    )
    latitude_max: IntProperty(
        name="Latitude Max"
    )
    slope_min: IntProperty(
        name="Slope Min"
    )
    slope_max: IntProperty(
        name="Slope Max"
    )


class SEUT_PlanetPropertiesMaterialGroups(PropertyGroup):
    """Material Groups of Complex Materials"""

    name: StringProperty(
        name="Name"
    )
    value: IntProperty(
        name="Value"
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
        min=0
    )


class SEUT_PlanetPropertiesMaterials(PropertyGroup):
    """Materials of Environment Items"""

    name: StringProperty(
        name="Value"
    )


class SEUT_PlanetPropertiesItems(PropertyGroup):
    """Items defined for Environment Item entries"""

    name: StringProperty()

    type_id: StringProperty(
        name="Value"
    )
    subtype_id: StringProperty(
        name="Value"
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
        min=0
    )
    ore_type: StringProperty(
        name="Ore Type"
    )
    start: IntProperty(
        name="Start",
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
        min=0
    )
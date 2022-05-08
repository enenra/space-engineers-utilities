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
    
    name: StringProperty()

    layers: CollectionProperty(
        type=SEUT_PlanetPropertiesDistributionRulesLayers
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


class SEUT_PlanetPropertiesBiomes(PropertyGroup):
    """Biomes of Environment Items"""

    name: StringProperty()

    value: IntProperty(
        name="Value"
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
    
    name: StringProperty()

    biomes: CollectionProperty(
        type=SEUT_PlanetPropertiesBiomes
    )
    materials: CollectionProperty(
        type=SEUT_PlanetPropertiesMaterials
    )
    items: CollectionProperty(
        type=SEUT_PlanetPropertiesItems
    )
    rules: CollectionProperty(
        type=SEUT_PlanetPropertiesDistributionRules
    )


class SEUT_PlanetPropertiesOreMappings(PropertyGroup):
    """Ore Mapping Entries"""
    
    name: StringProperty()

    value: IntProperty(
        name="Value"
    )
    ore_type: StringProperty(
        name="Type"
    )
    start: IntProperty(
        name="Start",
        min=0
    )
    depth: IntProperty(
        name="Depth",
        min=1
    )
    target_color: StringProperty(
        name="Target Color"
    )
    color_influence: IntProperty(
        name="Color Influence",
        min=0
    )


class SEUT_PlanetProperties(PropertyGroup):
    """Holder for planet properties"""

    name: StringProperty()

    voxel_materials: CollectionProperty(
        type=SEUT_PlanetPropertiesMaterialGroups
    )
    environment_items: CollectionProperty(
        type=SEUT_PlanetPropertiesEnvironmentItems
    )
    ore_mappings: CollectionProperty(
        type=SEUT_PlanetPropertiesOreMappings
    )
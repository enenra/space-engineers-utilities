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


def update_distribution_rules_name(self, context):
    scene = context.scene

    if self.name == self.name_prev:
        return
    
    # In case the rule belongs to an environment item and no material groups exist
    if scene.seut.material_groups_index > 0:
        for r in scene.seut.material_groups[scene.seut.material_groups_index].rules:
            if self != r and r.name == self.name:
                self.name = self.name_prev
                return
    
    self.name_prev = self.name


def update_material_groups_name(self, context):
    scene = context.scene

    if self.name == self.name_prev:
        return
    
    for mg in scene.seut.material_groups:
        if self != mg and mg.name == self.name:
            self.name = self.name_prev
            return
    
    self.name_prev = self.name


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


def update_environment_items_name(self, context):
    scene = context.scene

    if self.name == self.name_prev:
        return
    
    for ei in scene.seut.environment_items:
        if self != ei and ei.name == self.name:
            self.name = self.name_prev
            return
    
    self.name_prev = self.name


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

    
def poll_voxelmaterials(self, object):
    if object.asset_data is None:
        return False
    if 'voxel' not in object.asset_data.tags:
        return False
    if 'far1' in object.asset_data.tags or 'far2' in object.asset_data.tags:
        return False

    return True

class SEUT_PlanetPropertiesDistributionRulesLayers(PropertyGroup):
    """Layer definitions of Material Group placement rules"""
    
    name: StringProperty()

    material: PointerProperty(
        name="Material",
        description="The Voxel Material the layer consists of",
        type=bpy.types.Material,
        poll=poll_voxelmaterials
    )
    depth: FloatProperty(
        name="Depth",
        description="The thickness of this layer of voxels",
        default=0,
        min=0
    )


class SEUT_PlanetPropertiesDistributionRules(PropertyGroup):
    """Placement rules of Material Groups"""
    
    name: StringProperty(
        name="Name",
        description="The name of the distribution rule",
        update=update_distribution_rules_name
    )
    name_prev: StringProperty()
    layers: CollectionProperty(
        type=SEUT_PlanetPropertiesDistributionRulesLayers
    )
    layers_index: IntProperty(
        default=0
    )
    height_min: FloatProperty(
        name="Height Min",
        description="The minimum height at which this material group should appear.\nNote: The maximum possible height (1.0) is always 6% of the spawned planets diameter in km. Ex.: the maximum height of a 120km diameter planet is 7.2km",
        default=0,
        min=0,
        max=1
    )
    height_max: FloatProperty(
        name="Height Max",
        description="The maximum height at which this material group should appear.\nNote: The maximum possible height (1.0) is always 6% of the spawned planets diameter in km. Ex.: the maximum height of a 120km diameter planet is 7.2km",
        default=0,
        min=0,
        max=1
    )
    latitude_min: FloatProperty(
        name="Latitude Min",
        description="The minimum latitude in degrees at which the material group should spawn",
        default=0,
        min=-90,
        max=90
    )
    latitude_max: FloatProperty(
        name="Latitude Max",
        description="The maximum latitude in degrees at which the material group should spawn",
        default=0,
        min=-90,
        max=90
    )
    slope_min: FloatProperty(
        name="Slope Min",
        description="The minimum slope / angle in degrees on which this material group should be placed",
        default=0,
        min=0,
        max=90
    )
    slope_max: FloatProperty(
        name="Slope Max",
        description="The maximum slope / angle in degrees on which this material group should be placed",
        default=0,
        min=0,
        max=90
    )


class SEUT_PlanetPropertiesMaterialGroups(PropertyGroup):
    """Material Groups of Complex Materials"""

    name: StringProperty(
        name="Name",
        description="The name of the Complex Materials group",
        update=update_material_groups_name
    )
    name_prev: StringProperty()
    value: IntProperty(
        name="Value",
        description="The luminosity value of the color in the Red channel onto which this material group should be placed",
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
        description="The luminosity value of the color in the Green channel onto which these Environment Items should be placed",
        default=0,
        min=0,
        max=255,
        update=update_biomes_value
    )


class SEUT_PlanetPropertiesMaterials(PropertyGroup):
    """Materials of Environment Items"""

    name: StringProperty()

    material: PointerProperty(
        name="Voxel Material",
        description="The SubtypeId of the Voxel Material",
        type=bpy.types.Material,
        poll=poll_voxelmaterials
    )


class SEUT_PlanetPropertiesItems(PropertyGroup):
    """Items defined for Environment Item entries"""

    name: StringProperty()

    type_id: StringProperty(
        name="TypeId",
        description="The TypeId of the environment object"
    )
    subtype_id: StringProperty(
        name="SubtypeId",
        description="The SubtypeId of the environment object"
    )
    group_id: StringProperty(
        name="GroupId",
        description="The GroupId of the environment object"
    )
    modifier_id: StringProperty(
        name="ModifierId",
        description="The ModifierId of the environment object"
    )
    density: FloatProperty(
        name="Density",
        description="The density in which this environment item should be placed",
        min=0.01,
        max=1.00
    )


class SEUT_PlanetPropertiesEnvironmentItems(PropertyGroup):
    """Environment Item Entries"""
    
    name: StringProperty(
        name="Name",
        description="The name of this environment items entry",
        update=update_environment_items_name
    )
    name_prev: StringProperty()
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
        description="The luminosity value of the color in the Blue channel onto which the Ore Mapping should be placed",
        default=0,
        min=0,
        max=255,
        update=update_ore_mappings_value
    )
    ore_type: PointerProperty(
        name="Ore Type",
        description="The SubtypeId of the voxel material to place",
        type=bpy.types.Material,
        poll=poll_voxelmaterials
    )
    start: IntProperty(
        name="Start",
        description="The depth in meters below ground at which the deposit should start",
        default=0,
        min=0
    )
    depth: IntProperty(
        name="Depth",
        description="The thickness of the ore deposit",
        default=1,
        min=1
    )
    target_color: FloatVectorProperty(
        name="Target Color",
        description="The color that is applied to the ore spots above this ore deposit.\nNote: Due to Blender weirdness, the color shown here is not the exact same color the game will use",
        subtype='COLOR',
        size=3,
        min=0,
        max=1.0
    )
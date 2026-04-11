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

    if self.name.startswith(" "):
        self.sub_item = True
    else:
        self.sub_item = False

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
    color.color[0] = self.value / 255
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
    color.color[1] = self.value / 255
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
    color.color[2] = self.value / 255


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
        default=1,
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
        default=90,
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
        default=90,
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
    enabled: BoolProperty(
        name="Enabled",
        description="Enable or disable this entry from being exported to SBC",
        default=True
    )
    sub_item: BoolProperty(
        default=False
    )
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

    type_id: EnumProperty(
        name="TypeId",
        description="The TypeId of the environment object",
        items=(
            ('MyObjectBuilder_DestroyableItems', 'Destroyable Item', ''),
            ('MyObjectBuilder_Trees', 'Tree', ''),
            ('MyObjectBuilder_Forageable', 'Forageable', ''),
            ('MyObjectBuilder_VoxelMapStorageDefinition', 'Voxel Map', ''),
            ),
        default='MyObjectBuilder_DestroyableItems'
    )
    subtype_id: StringProperty(
        name="SubtypeId",
        description="The SubtypeId of the environment object"
    )
    group_id: StringProperty(
        name="GroupId",
        description="The GroupId of the voxel map. Only used if no SubtypeId is set"
    )
    modifier_id: StringProperty(
        name="ModifierId",
        description="The ModifierId of the voxel map. Only used if no SubtypeId is set"
    )
    density: FloatProperty(
        name="Density",
        description="The density in which this environment item should be placed",
        min=0.0001,
        max=1000.00
    )


class SEUT_PlanetPropertiesEnvironmentItems(PropertyGroup):
    """Environment Item Entries"""

    name: StringProperty(
        name="Name",
        description="The name of this environment items entry",
        update=update_environment_items_name
    )
    name_prev: StringProperty()
    enabled: BoolProperty(
        name="Enabled",
        description="Enable or disable this entry from being exported to SBC",
        default=True
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
    enabled: BoolProperty(
        name="Enabled",
        description="Enable or disable this entry from being exported to SBC",
        default=True
    )
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


class SEUT_PlanetPropertiesWeatherGeneratorsWeathers(PropertyGroup):
    """Planet Weathers"""

    name: StringProperty(
        name="SubtypeId",
        description="The SubtypeId of the Weather Definition"
    )
    weight: IntProperty(
        name="Weight",
        description="Higher numbers increase the chance for this weather to be picked, but the exact chance depends on the other weathers in this list",
        default=0,
        min=0
    )
    min_length: IntProperty(
        name="Minimum Length",
        description="Randomly picked duration between this and Maximum Length, in seconds",
        default=0
    )
    max_length: IntProperty(
        name="Maximum Length",
        description="Randomly picked duration between this and Minimum Length, in seconds",
        default=0
    )
    spawn_offset: IntProperty(
        name="Spawn Offset",
        description="Generate the weather this many meters away from the player",
        default=0
    )


class SEUT_PlanetPropertiesWeatherGenerators(PropertyGroup):
    """Planet Weather Generators"""

    name: StringProperty(
        name="Name",
        description="The name of the Weather Generator"
    )
    enabled: BoolProperty(
        name="Enabled",
        description="Enable or disable this entry from being exported to SBC",
        default=True
    )
    voxel: StringProperty(
        name="Material Type",
        description="The MaterialTypeName of a voxel material where the following list of weathers are allowed to spawn"
    )
    weathers: CollectionProperty(
        type=SEUT_PlanetPropertiesWeatherGeneratorsWeathers
    )
    weathers_index: IntProperty(
        default=0
    )


class SEUT_PlanetPropertiesCloudLayersTextures(PropertyGroup):
    """Planet Cloud Layers"""

    name: StringProperty(
        name="Name",
        description="The name of the Texture"
    )
    texture: StringProperty(
        name="Texture",
        description="The game needs 2 textures, a _cm and an _alphamask. To point this definition to them you must write only one entry (it will ignore subsequent entries) and that path must be one of the files but with the _cm or _alphamask removed from the name. This does mean it will point to a file that does not exist, but this is fine because the game will automatically look for 2 files where it inserts the _cm and _alphamask before the .dds extension of your given path",
        subtype="FILE_PATH",
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )

class SEUT_PlanetPropertiesCloudLayers(PropertyGroup):
    """Planet Cloud Layers"""

    name: StringProperty(
        name="Name",
        description="The name of the Cloud Layer"
    )
    enabled: BoolProperty(
        name="Enabled",
        description="Enable or disable this entry from being exported to SBC",
        default=True
    )
    model: StringProperty(
        name="Model",
        description="The model used for this cloud layer",
        subtype="FILE_PATH",
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )
    textures: CollectionProperty(
        type=SEUT_PlanetPropertiesCloudLayersTextures
    )
    textures_index: IntProperty(
        default=0
    )
    relative_altitude: FloatProperty(
        name="Relative Altitude",
        description="Affects the resulting altitude of the cloud layer",
        default=0
    )
    scaling_enabled: BoolProperty(
        name="Scaling Enabled",
        description="If set to true, this affects the Altitude: If the camera distance to center of the planet is farther than 95% of the Altitude, then the Altitude is multiplied in some way",
        default=False
    )
    initial_rotation: FloatProperty(
        name="Initial Rotation",
        description="Starting rotation angle in radians",
        default=0
    )
    angular_velocity: FloatProperty(
        name="Angular Velocity",
        description="Rotation speed in radians per 10 ticks probably. Can be negative to spin the other way",
        default=0
    )
    rotation_axis: FloatVectorProperty(
        name="Rotation Axis",
        description="Axis around which this cloud layer is spinning. Gets automatically normalized therefore can input whatever scale you wish. If set to 0,0,0 it will default to 0,1,0 again",
        size=3,
        min=-1.0,
        max=1.0
    )
    fade_out_relative_altitude_start: FloatProperty(
        name="Fade Out Relative Altitude Start",
        description="From the camera perspective, relative altitude at which this cloud layer starts fading out (less transparency). The Fade Out Relative Altitude End decides where the completion of that fade out is",
        default=0
    )
    fade_out_relative_altitude_end: FloatProperty(
        name="Fade Out Relative Altitude End",
        description="From the camera perspective, relative altitude at which this cloud layer is completely invisible. This supports being either smaller or larger than <FadeOutRelativeAltitudeStart> and it will have different behaviors in each case. If equal to Fade Out Relative Altitude Start then they will do nothing",
        default=0
    )
    color: FloatVectorProperty(
        name="Color",
        description="Color multiplier. If Alpha/W is 0 then this layer is skipped",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1.0
    )

class SEUT_PlanetPropertiesSoundRules(PropertyGroup):
    """Sound Rules"""

    name: StringProperty(
        name="Name",
        description="The name of the Sound Rule"
    )
    height_min: FloatProperty(
        name="Height Min",
        description="The minimum height at which this sound rule should be used.\nNote: The maximum possible height (1.0) is always 6% of the spawned planets diameter in km. Ex.: the maximum height of a 120km diameter planet is 7.2km",
        default=0,
        min=0,
        max=1
    )
    height_max: FloatProperty(
        name="Height Max",
        description="The maximum height at which this sound rule should be used.\nNote: The maximum possible height (1.0) is always 6% of the spawned planets diameter in km. Ex.: the maximum height of a 120km diameter planet is 7.2km",
        default=1,
        min=0,
        max=1
    )
    latitude_min: FloatProperty(
        name="Latitude Min",
        description="The minimum latitude in degrees at which the sound rule should be used",
        default=0,
        min=-90,
        max=90
    )
    latitude_max: FloatProperty(
        name="Latitude Max",
        description="The maximum latitude in degrees at which the sound rule should be used",
        default=90,
        min=-90,
        max=90
    )
    sun_angle_min: FloatProperty(
        name="Sun Angle Min",
        description="The minimum angle in degrees from the zenith at which the sound rule should be used",
        default=0,
        min=0,
        max=180
    )
    sun_angle_max: FloatProperty(
        name="Sun Angle Max",
        description="The maximum angle in degrees from the zenith at which the sound rule should be used",
        default=180,
        min=0,
        max=180
    )
    environment_sound: StringProperty(
        name="Environment Sound",
        description="The SubtypeId of the sound to be used"
    )
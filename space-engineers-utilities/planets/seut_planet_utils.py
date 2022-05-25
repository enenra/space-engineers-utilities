import bpy


def add_material_group(context):
    scene = context.scene
    
    if scene.seut.material_groups_palette is None:
        palette = bpy.data.palettes.new(f"MaterialGroups")
        palette.use_fake_user = True
        scene.seut.material_groups_palette = palette
    
    item = scene.seut.material_groups.add()
    item.name = "MaterialGroup"
    item.value = 0

    return item


def add_biome(context, ei = None):
    scene = context.scene

    if ei is None:
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]
    else:
        environment_item = ei
    
    if scene.seut.biomes_palette is None:
        palette = bpy.data.palettes.new(f"Biomes")
        palette.use_fake_user = True
        scene.seut.biomes_palette = palette

    item = environment_item.biomes.add()
    item.value = len(environment_item.biomes)

    return item


def add_ore_mapping(context):
    scene = context.scene
    
    if scene.seut.ore_mappings_palette is None:
        palette = bpy.data.palettes.new(f"OreMappings")
        palette.use_fake_user = True
        scene.seut.ore_mappings_palette = palette
    
    item = scene.seut.ore_mappings.add()
    item.value = len(scene.seut.ore_mappings)

    return item
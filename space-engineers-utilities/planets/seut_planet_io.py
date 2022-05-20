import bpy
import os

from ..seut_utils   import get_abs_path


def export_planet_sbc(scene: bpy.types.Scene):
    """"""

    return {'FINISHED'}


def export_planet_maps(scene: bpy.types.Scene):
    """Saves the baked images saved in the BLEND file to the mod folder"""

    sides = ['front', 'back', 'left', 'right', 'top', 'bottom']

    for img in bpy.data.images:
        for side in sides:
            if img.name == side and scene.seut.export_map_height:
                img.filepath = os.path.join(get_abs_path(scene.seut.mod_path), 'Data', 'PlanetDataFiles', scene.seut.subtypeId, img.name + '.png')
                img.file_format = 'PNG'
                img.save()

            elif img.name == side + '_mat' and scene.seut.export_map_biome:
                img.filepath = os.path.join(get_abs_path(scene.seut.mod_path), 'Data', 'PlanetDataFiles', scene.seut.subtypeId, img.name + '.png')
                img.file_format = 'PNG'
                img.save()

            elif img.name == side + '_add' and scene.seut.export_map_spots:
                img.filepath = os.path.join(get_abs_path(scene.seut.mod_path), 'Data', 'PlanetDataFiles', scene.seut.subtypeId, img.name + '.png')
                img.file_format = 'PNG'
                img.save()

    return {'FINISHED'}


def bake_planet_map(context: bpy.types.Context):
    """Bakes the bake source to the bake target"""

    scene = context.scene

    bake_type = scene.seut.bake_type
    bake_resolution = int(scene.seut.bake_resolution)
    bake_target = scene.seut.bake_target
    bake_source = scene.seut.bake_source

    engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    scene.render.bake.use_selected_to_active = True

    def create_image(name: str, resolution: int) -> bpy.types.Image:
        if name in bpy.data.images:
            img = bpy.data.images[name]
            bpy.data.images.remove(img)

        img = bpy.data.images.new(
            name=name,
            width=resolution,
            height=resolution, 
            alpha=False,
            float_buffer=False,
            is_data=True,
            tiled=False
        )

        return img
    
    mats = []
    for slot in bake_target.material_slots:
        mats.append(slot.material)

    if bake_type == 'height':
        suffix = None
        scene.render.bake.image_settings.color_depth = 16
        scene.render.bake.image_settings.color_mode = 'BW'
    elif bake_type == 'biome':
        suffix = "_mat"
        scene.render.bake.image_settings.color_depth = 32
        scene.render.bake.image_settings.color_mode = 'RGB'
    else:
        scene.render.bake.image_settings.color_depth = 32
        scene.render.bake.image_settings.color_mode = 'RGB'
        suffix = "_add"

    for mat in mats:
        node = mat.node_tree.nodes['IMAGE']
        node.image = create_image(mat.name + suffix, bake_resolution)
        node.select = True

    bake_source.hide_viewport = False
    bake_source.select_set(True)
    bake_source.hide_set(False)

    bake_target.hide_viewport = False
    bake_target.select_set(True)
    bake_target.hide_set(False)
    context.window.view_layer.objects.active = bake_target

    bpy.ops.object.bake(type='COMBINED')

    scene.render.engine = engine

    return {'FINISHED'}


def import_planet_sbc(path: os.path):
    """"""

    # offer options for what parts should be imported? tickboxes.

    return {'FINISHED'}
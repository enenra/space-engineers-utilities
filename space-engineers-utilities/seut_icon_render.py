import bpy
import os

from math           import pi
from bpy.types      import Operator

from .materials.seut_ot_texture_conversion  import convert_texture
from .seut_collections                      import get_collections, create_seut_collection
from .seut_errors                           import check_collection, check_collection_excluded, seut_report, get_abs_path
from .seut_utils                            import to_radians, clear_selection, prep_context, seut_report, get_seut_blend_data, link_node_tree


def setup_icon_render(self, context):
    """Sets up render utilities"""

    scene = context.scene
    collections = get_collections(scene)
    current_area = prep_context(context)

    result = check_collection(self, context, scene, collections['seut'][0], False)
    if not result == {'CONTINUE'}:
        scene.seut.mirroringToggle = 'off'
        return

    collection = create_seut_collection(scene, 'render')

    # Spawn holder empty
    bpy.ops.object.add(type='EMPTY', location=scene.seut.renderEmptyLocation, rotation=scene.seut.renderEmptyRotation)
    empty = bpy.context.view_layer.objects.active
    empty.scale.x = scene.seut.renderDistance
    empty.scale.y = scene.seut.renderDistance
    empty.scale.z = scene.seut.renderDistance
    empty.name = 'Icon Render'
    empty.empty_display_type = 'SPHERE'

    # Spawn camera
    bpy.ops.object.camera_add(location=(0.0, -15, 0.0), rotation=(to_radians(90), 0.0, 0.0))
    camera = bpy.context.view_layer.objects.active
    camera.parent = empty
    scene.camera = camera
    camera.name = 'ICON'
    camera.data.name = 'ICON'
    camera.data.lens = scene.seut.renderZoom

    # Spawn lights
    bpy.ops.object.light_add(type='POINT', location=(-12.5, -12.5, 5.0), rotation=(0.0, 0.0, 0.0))
    key_light = bpy.context.view_layer.objects.active
    key_light.parent = empty
    key_light.name = 'Key Light'
    key_light.data.energy = 7500.0 * scene.seut.renderDistance

    bpy.ops.object.light_add(type='POINT', location=(10.0, -10.0, -2.5), rotation=(0.0, 0.0, 0.0))
    fill_light = bpy.context.view_layer.objects.active
    fill_light.parent = empty
    fill_light.name = 'Fill Light'
    fill_light.data.energy = 5000.0 * scene.seut.renderDistance

    bpy.ops.object.light_add(type='SPOT', location=(0.0, 15.0, 0.0), rotation=(to_radians(-90), 0.0, 0.0))
    rim_light = bpy.context.view_layer.objects.active
    rim_light.parent = empty
    rim_light.name = 'Rim Light'
    rim_light.data.energy = 10000.0 * scene.seut.renderDistance

    parent_collection = empty.users_collection[0]
    if parent_collection != collection:
        collection.objects.link(empty)
        collection.objects.link(camera)
        collection.objects.link(key_light)
        collection.objects.link(fill_light)
        collection.objects.link(rim_light)

        if parent_collection is None:
            scene.collection.objects.unlink(empty)
            scene.collection.objects.unlink(camera)
            scene.collection.objects.unlink(key_light)
            scene.collection.objects.unlink(fill_light)
            scene.collection.objects.unlink(rim_light)
        else:
            parent_collection.objects.unlink(empty)
            parent_collection.objects.unlink(camera)
            parent_collection.objects.unlink(key_light)
            parent_collection.objects.unlink(fill_light)
            parent_collection.objects.unlink(rim_light)

    # Spawn compositor node tree
    if scene.compositing_node_group is None or scene.compositing_node_group.name != "Icon Render":
        scene.compositing_node_group = link_node_tree("Icon Render", None, True)

    # Force update render resolution
    scene.seut.renderResolution = scene.seut.renderResolution
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = True

    clear_selection(context)
    context.area.type = current_area


def clean_icon_render(self, context):
    """Clean up render utilities"""

    scene = context.scene
    current_area = prep_context(context)

    tag = ' (' + scene.seut.subtypeId + ')'

    # Delete objects
    for obj in scene.objects:
        if obj is not None and obj.type == 'EMPTY':
            if obj.name == 'Icon Render':
                for child in obj.children:
                    if child.data is not None:
                        if child.type == 'CAMERA':
                            bpy.data.cameras.remove(child.data)
                        elif child.type == 'LIGHT':
                            bpy.data.lights.remove(child.data)

                clear_selection(context)
                bpy.data.objects.remove(obj)

    # Delete collection
    if 'Render' + tag in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections['Render' + tag])

    context.area.type = current_area


class SEUT_OT_IconRenderPreview(Operator):
    """Shows a render preview window"""
    bl_idname = "scene.icon_render_preview"
    bl_label = "Render"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        if context.scene.render.filepath == '/tmp\\':
            Operator.poll_message_set("A render folder must first be defined.")
            return False

        return context.scene.seut.renderToggle == 'on'


    def execute(self, context):

        scene = context.scene
        data = get_seut_blend_data()

        if not os.path.isdir(get_abs_path(scene.render.filepath)):
            os.makedirs(get_abs_path(scene.render.filepath))

        clear_selection(context)

        scene.render.use_compositing = True
        scene.render.use_sequencer = True

        simple_nav = data.seut.simple_navigation
        data.seut.simple_navigation = False

        collections = get_collections(scene)

        # This is done in two steps so that objects which are in the main collection as well as other collections are guaranteed to be visible.

        hide_status = {}

        for key, value in collections.items():
            if value is None:
                continue

            if key in ['hkt', 'bs', 'lod']:
                for sub_col in value:
                    for obj in sub_col.objects:
                        if obj is None:
                            continue

                        hide_status[obj.name] = []
                        hide_status[obj.name].append(obj.hide_render)
                        hide_status[obj.name].append(obj.hide_viewport)
                        obj.hide_render = True
                        obj.hide_viewport = True

        for obj in collections['render'][0].objects:
            obj.hide_render = False
            obj.hide_viewport = False

        # This path juggling is to prevent Blender from saving the default render output
        path = scene.render.filepath
        file_format = scene.seut.render_output_type.lower()
        if file_format == 'dds':
            file_format = 'png'
        scene.render.filepath = get_abs_path(scene.render.filepath) + "\\" + scene.seut.subtypeId + '.' + file_format

        bpy.ops.render.render()
        bpy.ops.render.view_show('INVOKE_DEFAULT')
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        image = area.spaces.active.image
        area.spaces.active.image = bpy.data.images['Viewer Node']
        bpy.data.images['Viewer Node'].save_render(scene.render.filepath)

        if scene.seut.render_output_type.lower() == 'dds':
            result = convert_texture(scene.render.filepath, path, 'icon', [])
            os.remove(scene.render.filepath)
            os.rename(os.path.join(get_abs_path(path), scene.seut.subtypeId + '.DDS'), os.path.splitext(scene.render.filepath)[0] + '.dds')

        for key, value in collections.items():
            if value is None:
                continue

            if key in ['hkt', 'bs', 'lod']:
                for sub_col in value:
                    for obj in sub_col.objects:
                        if obj is None:
                            continue

                        if obj.name in hide_status:
                            obj.hide_render = hide_status[obj.name][0]
                            obj.hide_viewport = hide_status[obj.name][1]
                        else:
                            obj.hide_render = False
                            obj.hide_viewport = False

        data.seut.simple_navigation = simple_nav

        scene.render.filepath = path

        seut_report(self, context, 'INFO', True, 'I018', os.path.join(get_abs_path(scene.render.filepath), scene.seut.subtypeId + '.' + scene.seut.render_output_type.lower()))

        return {'FINISHED'}


class SEUT_OT_CopyRenderOptions(Operator):
    """Copies the icon render options of the current scene to all other scenes"""
    bl_idname = "scene.copy_render_options"
    bl_label = "Copy Icon Render Options"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if os.path.isfile(get_abs_path(scene.render.filepath)):
            os.path.dirname(get_abs_path(scene.render.filepath))

        if not os.path.exists(get_abs_path(scene.render.filepath)):
            os.makedirs(get_abs_path(scene.render.filepath))

        for scn in bpy.data.scenes:
            scn.render.filepath = scene.render.filepath
            scn.seut.renderColorOverlay = scene.seut.renderColorOverlay
            scn.seut.renderResolution = scene.seut.renderResolution
            scn.seut.render_output_type = scene.seut.render_output_type

        seut_report(self, context, 'INFO', True, 'I006', "Icon Render")

        return {'FINISHED'}


class SEUT_OT_CopyRenderOffset(Operator):
    """Copies the icon render offset of the current scene to all other scenes"""
    bl_idname = "scene.copy_render_offset"
    bl_label = "Copy Icon Render Offset"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        for scn in bpy.data.scenes:
            scn.seut.renderZoom = scene.seut.renderZoom
            scn.seut.renderDistance = scene.seut.renderDistance
            scn.seut.renderEmptyLocation = scene.seut.renderEmptyLocation
            scn.seut.renderEmptyRotation = scene.seut.renderEmptyRotation

        seut_report(self, context, 'INFO', True, 'I006', "Icon Render")

        return {'FINISHED'}
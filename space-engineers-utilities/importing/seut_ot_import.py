import bpy
import os
import addon_utils

import mathutils as mu

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

from bpy.types                  import Operator

from .seut_ot_import_materials              import import_materials
from ..utils.seut_tool_utils                import *
from ..empties.seut_empties                 import empty_types
from ..materials.seut_ot_remap_materials    import remap_materials
from ..seut_errors                          import seut_report
from ..seut_utils                           import create_relative_path, get_preferences, get_seut_blend_data, to_radians


class SEUT_OT_Import(Operator):
    """Import FBX files and remap materials"""
    bl_idname = "scene.import"
    bl_label = "Import FBX"
    bl_options = {'REGISTER', 'UNDO'}


    filter_glob: StringProperty(
        default='*.fbx',
        options={'HIDDEN'}
        )

    filepath: StringProperty(
        subtype="FILE_PATH"
        )


    @classmethod
    def poll(cls, context):
        return context.scene is not None


    def execute(self, context):

        result = import_fbx(self, context, self.filepath)
        remap_materials(self, context)

        return result


    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}


def import_gltf(self, context, filepath):
    scene = context.scene
    preferences = get_preferences()

    existing_objects = set(scene.objects)
    glb_path = os.path.splitext(filepath)[0] + '.glb'

    if not os.path.exists(glb_path) or os.path.getmtime(filepath) > os.path.getmtime(glb_path):
        if os.path.exists(glb_path):
            os.remove(glb_path)

        args = [os.path.join(get_tool_dir(), 'FBX2glTF-windows-x64.exe'), '-b', '--user-properties', '-i', filepath, '-o', glb_path]

        result = call_tool(args)
        if result[1] is not None:
            result[1] = result[1].decode("utf-8", "ignore")
        else:
            result[1] = "None"

    bpy.ops.import_scene.gltf(filepath=glb_path)

    new_objects = set(scene.objects)
    imported_objects = new_objects.copy()

    for new in new_objects:
        for existing in existing_objects:
            if new == existing:
                imported_objects.remove(new)

    root = None
    for obj in imported_objects:
        if obj.parent is None and obj.type == 'EMPTY' and obj.name.startswith("RootNode"):
            if obj.children is None or len(obj.children) < 1:
                bpy.data.objects.remove(obj)
                return {'FINISHED'}

            root = obj.children[0]
            imported_objects.remove(obj)
            bpy.data.objects.remove(obj)
            break

    root.rotation_mode = 'XYZ'

    root_rotation = root.rotation_euler
    root_vec_rotation = mu.Vector(root_rotation)
    root_eul_rotation = mu.Euler(root_rotation)
    root_mat_rotation = root_eul_rotation.to_matrix()

    for obj in imported_objects:
        if obj is None:
            continue

        obj.rotation_mode = 'XYZ'
        obj.select_set(False)

        if bpy.app.version < (4, 5, 0) and context.collection != scene.collection:
            context.collection.objects.link(obj)
            scene.collection.objects.unlink(obj)

        if obj.type == 'EMPTY':
            if obj.parent is None:
                continue

            obj_vec_rotation = mu.Vector(obj.rotation_euler)
            obj.rotation_euler = obj_vec_rotation - root_vec_rotation

            s = mu.Matrix.Diagonal(obj.scale)
            s = root_mat_rotation @ s
            s = s.col[0] + s.col[1] + s.col[2]
            s = ( abs(s[0]), abs(s[1]), abs(s[2]) )
            obj.scale = s

            obj.empty_display_size = 0.5
            obj.empty_display_type = next(
                (
                    empty_types[key]
                    for key in empty_types.keys()
                    if obj.name[: len(key)] == key
                ),
                'CUBE',
            )
            if scene.seut.sceneType not in ['character']:
                obj.scale.x *= 0.01
                obj.scale.y *= 0.01
                obj.scale.z *= 0.01

            custom_props = obj.get("fromFBX")
            if custom_props:
                custom_props = dict(custom_props)

                for item in custom_props["userProperties"]:
                    if item != "fromFBX":
                        obj[item] = custom_props['userProperties'][item]['value']

                if 'file' in obj and obj['file'] in bpy.data.scenes:
                    obj.seut.linkedScene = bpy.data.scenes[obj['file']]

                if 'highlight' in obj:
                    if obj['highlight'].find(";") == -1:
                        if obj['highlight'] in bpy.data.objects:
                            new = obj.seut.highlight_objects.add()
                            new.obj = bpy.data.objects[obj['highlight']]
                    else:
                        split = obj['highlight'].split(";")
                        for entry in split:
                            if entry in bpy.data.objects:
                                new = obj.seut.highlight_objects.add()
                                new.obj = bpy.data.objects[entry]

    for obj in imported_objects:
        if obj.parent is None:
            context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            if scene.seut.sceneType == 'mainScene':
                obj.rotation_euler[2] += to_radians(180)
            break

    xml_path = f'{os.path.splitext(filepath)[0]}.xml'
    if os.path.exists(xml_path):
        import_materials(self, context, xml_path)

    if not preferences.keep_glb:
        os.remove(glb_path)

    seut_report(self, context, 'INFO', True, 'I014', filepath)

    return {'FINISHED'}


def import_fbx(self, context, filepath):
    """Imports FBX and adjusts them for use in SEUT"""

    data = get_seut_blend_data()
    scene = context.scene
    existing_objects = set(scene.objects)

    try:
        if scene.seut.sceneType == ['character_animation'] or (
            scene.seut.sceneType != ['character'] and
            create_relative_path(filepath, 'Characters') != False and
            create_relative_path(filepath, 'Animations') != False
            ):

            scene.seut.sceneType = 'character_animation'

            bpy.ops.import_scene.fbx(
                filepath=filepath,
                global_scale=1.0,
                decal_offset=0.0,
                bake_space_transform=False,
                use_prepost_rot=True,
                use_manual_orientation=False,
                use_anim=True,
                ignore_leaf_bones=False,
                force_connect_children=False,
                automatic_bone_orientation=False,
                primary_bone_axis='X',
                secondary_bone_axis='Y'
                )

        elif scene.seut.sceneType == ['character'] or (
            scene.seut.sceneType != ['character_animation'] and
            create_relative_path(filepath, 'Characters') != False and
            create_relative_path(filepath, 'Animations') == False
            ):

            scene.seut.sceneType = 'character'

            bpy.ops.import_scene.fbx(
                filepath=filepath,
                global_scale=1.0,
                decal_offset=0.0,
                bake_space_transform=False,
                use_prepost_rot=True,
                use_manual_orientation=False,
                use_anim=False,
                ignore_leaf_bones=False,
                force_connect_children=False,
                automatic_bone_orientation=False,
                primary_bone_axis='X',
                secondary_bone_axis='Y'
                )

        else:
            if data.seut.use_alt_importer:
                bpy.ops.import_scene.fbx(
                    filepath=filepath,
                    use_manual_orientation=True,
                    axis_forward='Z',
                    axis_up='Y'
                    )

            else:
                return import_gltf(self, context, filepath)

    except RuntimeError as error:
        seut_report(self, context, 'ERROR', True, 'E036', str(error))
        return {'CANCELLED'}

    new_objects = set(scene.objects)
    imported_objects = new_objects.copy()

    for new in new_objects:
        for existing in existing_objects:
            if new == existing:
                imported_objects.remove(new)

    # Sanity check to catch import failure
    if imported_objects is None:
        seut_report(self, context, 'ERROR', True, 'E001')
        return {'CANCELLED'}

    for obj in imported_objects:
        if obj.type == 'EMPTY':
            obj.empty_display_type = next(
                (
                    empty_types[key]
                    for key in empty_types.keys()
                    if obj.name[: len(key)] == key
                ),
                'CUBE',
            )

    xml_path = f'{os.path.splitext(filepath)[0]}.xml'
    if os.path.exists(xml_path):
        import_materials(self, context, xml_path)

    seut_report(self, context, 'INFO', True, 'I014', filepath)

    return {'FINISHED'}
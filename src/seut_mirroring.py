import bpy

from math           import pi
from bpy.types      import Operator
from collections    import OrderedDict

from .seut_collections              import get_collections
from .seut_errors                   import check_collection, check_collection_excluded, seut_report
from .seut_utils                    import link_subpart_scene, unlink_subpart_scene, prep_context, to_radians, clear_selection, create_seut_collection


mirroring_presets = OrderedDict([
    ('None', (0.0, 0.0, 0.0)),
    ('X', (180.0, 0.0, 0.0)),
    ('Y', (0.0, 0.0, 180.0)),
    ('Z', (0.0, 180.0, 0.0)),
    ('HalfX', (90.0, 0.0, 0.0)),
    ('HalfY', (0.0, 0.0, -90.0)),
    ('HalfZ', (0.0, -90.0, 0.0)),
    ('MinusHalfX', (-90.0, 0.0, 0.0)),
    ('MinusHalfY', (0.0, 0.0, 90.0)),
    ('MinusHalfZ', (0.0, 90.0, 0.0)),
    ('XHalfY', (180.0, 0.0, -90.0)),
    ('XHalfZ', (180.0, 90.0, 0.0)),
    ('YHalfX', (90.0, 0.0, 180.0)),
    ('YHalfZ', (0.0, -90.0, 180.0)),
    ('ZHalfX', (-90.0, 0.0, 180.0)),
    ('ZHalfY', (0.0, 180.0, -90.0)),
    ('UnsupportedXY1', (90.0, 0.0, 90.0)),
    ('UnsupportedXY2', (-90.0, 0.0, 90.0)),
    ('UnsupportedXY3', (90.0, 0.0, -90.0)),
    ('UnsupportedXY4', (-90.0, 0.0, -90.0)),
    ('UnsupportedXZ1', (90.0, 90.0, 0.0)),
    ('UnsupportedXZ2', (-90.0, 90.0, 0.0)),
    ('UnsupportedXZ3', (90.0, -90.0, 0.0)),
    ('UnsupportedXZ4', (-90.0, -90.0, 0.0)),
])


def setup_mirroring(self, context):
    """Sets up mirroring utilities"""

    scene = context.scene
    collections = get_collections(scene)
    current_area = prep_context(context)

    result = check_collection(self, context, scene, collections['seut'], False)
    if not result == {'CONTINUE'}:
        scene.seut.mirroringToggle = 'off'
        return

    result = check_collection(self, context, scene, collections['main'], False)
    if not result == {'CONTINUE'}:
        scene.seut.mirroringToggle = 'off'
        return

    mats = 0
    for mat in bpy.data.materials:
        if mat.name == 'SMAT_Mirror_X':
            smat_x = mat
            mats += 1
        elif mat.name == 'SMAT_Mirror_Y':
            smat_y = mat
            mats += 1
        elif mat.name == 'SMAT_Mirror_Z':
            smat_z = mat
            mats += 1
    
    if mats != 3:
        seut_report(self, context, 'ERROR', False, 'E026', "Mirror Axis Materials")
        scene.seut.mirroringToggle = 'off'
        return
        
    tag = ' (' + scene.seut.subtypeId + ')'

    collection = create_seut_collection(collections['seut'], 'Mirroring' + tag)
    
    # Compile rotation / position / size information
    empty_x_rot_raw = mirroring_presets[scene.seut.mirroring_X]
    empty_y_rot_raw = mirroring_presets[scene.seut.mirroring_Y]
    empty_z_rot_raw = mirroring_presets[scene.seut.mirroring_Z]
    empty_x_rotation = (to_radians(empty_x_rot_raw[0]), to_radians(empty_x_rot_raw[1]), to_radians(empty_x_rot_raw[2]))
    empty_y_rotation = (to_radians(empty_y_rot_raw[0]), to_radians(empty_y_rot_raw[1]), to_radians(empty_y_rot_raw[2]))
    empty_z_rotation = (to_radians(empty_z_rot_raw[0]), to_radians(empty_z_rot_raw[1]), to_radians(empty_z_rot_raw[2]))

    factor = 1
    if scene.seut.gridScale == 'large': factor = 2.5
    if scene.seut.gridScale == 'small': factor = 0.5

    size = 1
    if scene.seut.bBox_X > size: size = scene.seut.bBox_X
    if scene.seut.bBox_Y > size: size = scene.seut.bBox_Y
    if scene.seut.bBox_Z > size: size = scene.seut.bBox_Z
    empty_size = size * factor

    offset = (size * 2 + size / 2) * factor

    # Create empties (using property rotation info) with certain distance from bounding box
    bpy.ops.object.add(type='EMPTY', location=(offset, 0.0, 0.0), rotation=empty_x_rotation)
    empty_x = bpy.context.view_layer.objects.active
    empty_x.name = 'Mirror LeftRight'
    empty_x.empty_display_type = 'ARROWS'
    empty_x.empty_display_size = empty_size
    bpy.ops.mesh.primitive_plane_add(size=empty_size * 2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(offset / 2, 0.0, 0.0), rotation=(0.0, to_radians(90), 0.0))
    plane_x = bpy.context.view_layer.objects.active
    plane_x.name = 'X Axis Mirror Plane'
    plane_x.active_material = smat_x

    bpy.ops.object.add(type='EMPTY', location=(0.0, offset, 0.0), rotation=empty_y_rotation)
    empty_y = bpy.context.view_layer.objects.active
    empty_y.name = 'Mirror FrontBack'
    empty_y.empty_display_type = 'ARROWS'
    empty_y.empty_display_size = empty_size
    bpy.ops.mesh.primitive_plane_add(size=empty_size * 2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, offset / 2, 0.0), rotation=(to_radians(90), 0.0, 0.0))
    plane_y = bpy.context.view_layer.objects.active
    plane_y.name = 'Y Axis Mirror Plane'
    plane_y.active_material = smat_y

    bpy.ops.object.add(type='EMPTY', location=(0.0, 0.0, offset), rotation=empty_z_rotation)
    empty_z = bpy.context.view_layer.objects.active
    empty_z.name = 'Mirror TopBottom'
    empty_z.empty_display_type = 'ARROWS'
    empty_z.empty_display_size = empty_size
    bpy.ops.mesh.primitive_plane_add(size=empty_size * 2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, offset / 2), rotation=(0.0, 0.0, to_radians(90)))
    plane_z = bpy.context.view_layer.objects.active
    plane_z.name = 'Z Axis Mirror Plane'
    plane_z.active_material = smat_z

    parentCollection = empty_x.users_collection[0]
    if parentCollection != collection:
        collection.objects.link(empty_x)
        collection.objects.link(empty_y)
        collection.objects.link(empty_z)
        collection.objects.link(plane_x)
        collection.objects.link(plane_y)
        collection.objects.link(plane_z)

        if parentCollection is None:
            scene.collection.objects.unlink(empty_x)
            scene.collection.objects.unlink(empty_y)
            scene.collection.objects.unlink(empty_z)
            scene.collection.objects.unlink(plane_x)
            scene.collection.objects.unlink(plane_y)
            scene.collection.objects.unlink(plane_z)
        else:
            parentCollection.objects.unlink(empty_x)
            parentCollection.objects.unlink(empty_y)
            parentCollection.objects.unlink(empty_z)
            parentCollection.objects.unlink(plane_x)
            parentCollection.objects.unlink(plane_y)
            parentCollection.objects.unlink(plane_z)

    # Instance main collection or mirroringScene main collection under empties
    source_scene = scene
    if scene.seut.mirroringScene is not None:
        source_scene = scene.seut.mirroringScene
    
    empty_x.seut.linkedScene = source_scene
    link_subpart_scene(self, scene, empty_x, collection)
    empty_y.seut.linkedScene = source_scene
    link_subpart_scene(self, scene, empty_y, collection)
    empty_z.seut.linkedScene = source_scene
    link_subpart_scene(self, scene, empty_z, collection)

    clear_selection(context)
    context.area.type = current_area


def clean_mirroring(self, context):
    """Cleans up mirroring utilities"""

    scene = context.scene
    collections = get_collections(scene)
    current_area = prep_context(context)

    tag = ' (' + scene.seut.subtypeId + ')'

    # Save empty rotation values to properties, delete children instances, remove empty
    for obj in scene.objects:
        if obj is not None and obj.type == 'EMPTY' and (obj.name == 'Mirror LeftRight' or obj.name == 'Mirror FrontBack' or obj.name == 'Mirror TopBottom'):

            save_rotation(self, context, obj)

            if len(obj.children) > 0:
                unlink_subpart_scene(obj)

            obj.select_set(state=False, view_layer=context.window.view_layer)
            bpy.data.objects.remove(obj)

        elif obj.name == 'X Axis Mirror Plane' or obj.name == 'Y Axis Mirror Plane' or obj.name == 'Z Axis Mirror Plane':

            obj.select_set(state=False, view_layer=context.window.view_layer)
            bpy.data.objects.remove(obj)

    # Delete collection
    if 'Mirroring' + tag in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections['Mirroring' + tag])

    context.area.type = current_area


def save_rotation(self, context, empty):
    """Saves the current rotation values of an empty to the scene properties"""

    scene = context.scene
    rotation = bpy.data.objects[empty.name].rotation_euler
    rot_x = sanitize_rotation(round(rotation[0] * 180 / pi))
    rot_y = sanitize_rotation(round(rotation[1] * 180 / pi))
    rot_z = sanitize_rotation(round(rotation[2] * 180 / pi))

    rot_converted = (rot_x, rot_y, rot_z)

    found = False
    for key, value in mirroring_presets.items():

        if value == rot_converted:
            found = True

            if empty.name.find("Mirror LeftRight") != -1:
                scene.seut.mirroring_X = key

            elif empty.name.find("Mirror FrontBack") != -1:
                scene.seut.mirroring_Y = key

            elif empty.name.find("Mirror TopBottom") != -1:
                scene.seut.mirroring_Z = key
            
            seut_report(self, context, 'INFO', False, 'I016', empty.name, str(rot_converted), str(key))
    
    if not found:
        seut_report(self, context, 'ERROR', False, 'E023', empty.name, str(rot_converted))


def sanitize_rotation(rotation: int) -> int:
    """Returns compatible equivalent rotation values"""

    if rotation == -180:
        return 180
    elif rotation == 270:
        return -90
    elif rotation == -270:
        return 90
    elif rotation == -0:
        return 0
    else:
        return rotation
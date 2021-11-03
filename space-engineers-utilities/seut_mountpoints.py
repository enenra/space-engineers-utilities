import bpy

from math           import pi
from bpy.types      import Operator
from bpy.props      import EnumProperty

from .materials.seut_materials      import create_internal_material
from .seut_collections              import get_collections, colors
from .seut_errors                   import check_collection, check_collection_excluded, seut_report
from .seut_utils                    import prep_context, to_radians, clear_selection, create_seut_collection, lock_object


valid_masks = ['0:0', '0:1', '0:2', '1:2', '3:3']


def setup_mountpoints(self, context):
    """Sets up mountpoint utilities"""

    scene = context.scene
    collections = get_collections(scene)
    current_area = prep_context(context)

    result = check_collection(self, context, scene, collections['seut'], False)
    if not result == {'CONTINUE'}:
        scene.seut.mirroringToggle = 'off'
        return

    smat_mp = None
    for mat in bpy.data.materials:
        if mat.name == 'SMAT_Mountpoint':
            smat_mp = mat
            break
    
    if smat_mp is None:
        smat_mp = create_internal_material(context, 'MOUNTPOINT')
        
    tag = ' (' + scene.seut.subtypeId + ')'

    collection = create_seut_collection(collections['seut'], 'Mountpoints' + tag)
    collection.seut.col_type = 'mountpoints'
    collection.seut.scene = scene
    if bpy.app.version >= (2, 91, 0):
        collection.color_tag = colors[collection.seut.col_type]

    # Create empty tree for sides
    if scene.seut.gridScale == 'small':
        scale = 0.5
    else:
        scale = 2.5

    bbox_x = scene.seut.bBox_X * scale
    bbox_y = scene.seut.bBox_Y * scale
    bbox_z = scene.seut.bBox_Z * scale

    # The 3D cursor is used as the origin. If it's not on center, everything is misaligned ingame.
    cursor_location = scene.cursor.location.copy()
    scene.cursor.location = (0.0, 0.0, 0.0)

    # Create and position side empties
    empty_front = create_mp_empty(context, 'Mountpoints Front', collection, None)
    empty_front.empty_display_type = 'SINGLE_ARROW'
    empty_front.rotation_euler.x = to_radians(-90)
    empty_front.rotation_euler.z = to_radians(-180)
    empty_front.location.y = -(bbox_y / 2 * 1.05)
    lock_object(empty_front)

    empty_back = create_mp_empty(context, 'Mountpoints Back', collection, None)
    empty_back.empty_display_type = 'SINGLE_ARROW'
    empty_back.rotation_euler.x = to_radians(-90)
    empty_back.location.y = bbox_y / 2 * 1.05
    lock_object(empty_back)

    empty_left = create_mp_empty(context, 'Mountpoints Left', collection, None)
    empty_left.empty_display_type = 'SINGLE_ARROW'
    empty_left.rotation_euler.x = to_radians(-90)
    empty_left.rotation_euler.z = to_radians(270)
    empty_left.location.x = bbox_x / 2 * 1.05
    lock_object(empty_left)

    empty_right = create_mp_empty(context, 'Mountpoints Right', collection, None)
    empty_right.empty_display_type = 'SINGLE_ARROW'
    empty_right.rotation_euler.x = to_radians(-90)
    empty_right.rotation_euler.z = to_radians(-270)
    empty_right.location.x = -(bbox_x / 2 * 1.05)
    lock_object(empty_right)

    empty_top = create_mp_empty(context, 'Mountpoints Top', collection, None)
    empty_top.empty_display_type = 'SINGLE_ARROW'
    empty_top.location.z = bbox_z / 2 * 1.05
    lock_object(empty_top)

    empty_bottom = create_mp_empty(context, 'Mountpoints Bottom', collection, None)
    empty_bottom.empty_display_type = 'SINGLE_ARROW'
    empty_bottom.rotation_euler.x = to_radians(180)
    empty_bottom.location.z = -(bbox_z / 2 * 1.05)
    lock_object(empty_bottom)

    # Create default mountpoint areas
    if len(scene.seut.mountpointAreas) == 0:
        plane = create_mp_area(context, 'Mountpoint Area Front', scale, scene.seut.bBox_X, scene.seut.bBox_Z, None, None, collection, empty_front)
        plane.active_material = smat_mp
        plane = create_mp_area(context, 'Mountpoint Area Back', scale, scene.seut.bBox_X, scene.seut.bBox_Z, None, None, collection, empty_back)
        plane.active_material = smat_mp
        plane = create_mp_area(context, 'Mountpoint Area Left', scale, scene.seut.bBox_Y, scene.seut.bBox_Z, None, None, collection, empty_left)
        plane.active_material = smat_mp
        plane = create_mp_area(context, 'Mountpoint Area Right', scale, scene.seut.bBox_Y, scene.seut.bBox_Z, None, None, collection, empty_right)
        plane.active_material = smat_mp
        plane = create_mp_area(context, 'Mountpoint Area Top', scale, scene.seut.bBox_X, scene.seut.bBox_Y, None, None, collection, empty_top)
        plane.active_material = smat_mp
        plane = create_mp_area(context, 'Mountpoint Area Bottom', scale, scene.seut.bBox_X, scene.seut.bBox_Y, None, None, collection, empty_bottom)
        plane.active_material = smat_mp

    # If there are already mountpoint areas saved, recreate them
    else:
        for area in scene.seut.mountpointAreas:
            plane = create_mp_area(context, 'Mountpoint Area ' + area.side.capitalize(), scale, None, None, area.xDim, area.yDim, collection, bpy.data.objects['Mountpoints ' + area.side.capitalize()])
            plane.active_material = smat_mp
            plane.location.x = area.x
            plane.location.y = area.y
            plane.seut.default = area.default
            plane.seut.pressurized = area.pressurized
            plane.seut.enabled = area.enabled
            plane.seut.exclusion_mask = area.exclusion_mask
            plane.seut.properties_mask = area.properties_mask

            mask = str(area.exclusion_mask) + ":" + str(area.properties_mask)
            if mask in valid_masks:
                plane.seut.mask_preset = mask

    clear_selection(context)
    scene.cursor.location = cursor_location
    context.area.type = current_area


def create_mp_empty(context, name, collection, parent):
    """Creates empty with given name, links it to specified collection and assigns it to a parent, if available"""

    scene = context.scene

    bpy.ops.object.add(type='EMPTY')
    empty = context.view_layer.objects.active
    empty.name = name

    parent_collection = empty.users_collection[0]
    if parent_collection != collection:
        collection.objects.link(empty)

        if parent_collection is None:
            scene.collection.objects.unlink(empty)
        else:
            parent_collection.objects.unlink(empty)
    
    if parent is not None:
        empty.parent = parent

    return empty


def create_mp_area(context, name, size, x, y, xDim, yDim, collection, parent):
    """Creates plane with given name, location, dimensions, links it to specified collection and assigns it to a parent, if available"""

    scene = context.scene
    current_area = prep_context(context)

    bpy.ops.mesh.primitive_plane_add(size=size, calc_uvs=True, enter_editmode=False, align='WORLD')
    area = bpy.context.view_layer.objects.active
    area.name = name

    if x is not None:
        area.scale.x = x
    if y is not None:
        area.scale.y = y
    if xDim is not None and yDim is not None:
        area.dimensions = (xDim, yDim, 0)

    parent_collection = area.users_collection[0]
    if parent_collection != collection:
        collection.objects.link(area)

        if parent_collection is None:
            scene.collection.objects.unlink(area)
        else:
            parent_collection.objects.unlink(area)
    
    if parent is not None:
        area.parent = parent

    context.area.type = current_area

    return area


def save_mountpoint(self, context, collection):
    """Saves mountpoint areas to an internal collection property"""

    scene = context.scene

    areas = scene.seut.mountpointAreas
    areas.clear()

    for empty in collection.objects:

        if empty is None:
            continue

        elif empty.type == 'EMPTY' and empty.name.find('Mountpoints ') != -1 and empty.children is not None:
            side = empty.name[12:]

            for child in empty.children:                    
                item = areas.add()
                item.side = side.lower()
                item.x = child.location.x
                item.y = child.location.y
                item.xDim = child.dimensions.x
                item.yDim = child.dimensions.y
                item.default = child.seut.default
                item.pressurized = child.seut.pressurized
                item.enabled = child.seut.enabled
                item.exclusion_mask = child.seut.exclusion_mask
                item.properties_mask = child.seut.properties_mask

    for area in areas:
        seut_report(self, context, 'INFO', False, 'I017', area.side, "Location x: " + str(area.x) + " Location y: " + str(area.y) + " Dimension x: " + str(area.xDim) + " Dimension y: " + str(area.yDim), "Default: " + str(area.default) + " PressurizedWhenOpen: " + str(area.pressurized) + " Enabled: " + str(area.enabled) + " ExclusionMask: " + str(area.exclusion_mask) + " PropertiesMask: " + str(area.properties_mask))


def clean_mountpoints(self, context):
    """Cleans up mountpoint utilities"""

    scene = context.scene
    current_area = prep_context(context)

    # The 3D cursor is used as the origin. If it's not on center, everything is misaligned ingame.
    cursor_location = scene.cursor.location.copy()
    scene.cursor.location = (0.0, 0.0, 0.0)

    tag = ' (' + scene.seut.subtypeId + ')'

    if 'Mountpoints' + tag in bpy.data.collections:
        save_mountpoint(self, context, bpy.data.collections['Mountpoints' + tag])

    # Save empty rotation values to properties, delete children instances, remove empty
    for obj in scene.objects:
        if obj is not None and obj.type == 'EMPTY':
            if obj.name == 'Mountpoints Front' or obj.name == 'Mountpoints Back' or obj.name == 'Mountpoints Left' or obj.name == 'Mountpoints Right' or obj.name == 'Mountpoints Top' or obj.name == 'Mountpoints Bottom':

                for child in obj.children:
                    bpy.data.objects.remove(child)

                obj.select_set(state=False, view_layer=context.window.view_layer)
                bpy.data.objects.remove(obj)

    # Delete collection
    if 'Mountpoints' + tag in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections['Mountpoints' + tag])

    scene.cursor.location = cursor_location
    context.area.type = current_area


class SEUT_OT_AddMountpointArea(Operator):
    """Adds an area to a mountpoint side"""
    bl_idname = "scene.add_mountpoint_area"
    bl_label = "Add Area"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) > 0:
            selected_object = context.selected_objects[0]
            return context.scene.seut.mountpointToggle == 'on' and (selected_object.type == 'EMPTY' and selected_object.name.find("Mountpoints ") != -1) or (selected_object.parent.type =='EMPTY' and selected_object.parent.name.find("Mountpoints ") != -1)


    def execute(self, context):

        scene = context.scene
        wm = context.window_manager

        smat_mp = None
        for mat in bpy.data.materials:
            if mat.name == 'SMAT_Mountpoint':
                smat_mp = mat
        
        if smat_mp is None:
            smat_mp = create_internal_material(context, 'MOUNTPOINT')

        # The 3D cursor is used as the origin. If it's not on center, everything is misaligned ingame.
        cursor_location = scene.cursor.location.copy()
        scene.cursor.location = (0.0, 0.0, 0.0)

        sides = ['front', 'back', 'left', 'right', 'top', 'bottom']

        selected_object = context.selected_objects[0]

        # In case a plane under the empty is selected, use the empty still.
        if selected_object.type != 'EMPTY':
            selected_object = selected_object.parent

        string = selected_object.name[len("Mountpoints "):].lower()

        if string in sides:
            side = string
        else:
            return {'CANCELLED'}

        if scene.seut.gridScale == 'small':
            scale = 0.5
        else:
            scale = 2.5

        tag = ' (' + scene.seut.subtypeId + ')'

        # Ensure MP collection still exists
        try:
            collection = bpy.data.collections['Mountpoints' + tag]
        except KeyError:
            seut_report(self, context, 'ERROR', True, 'E024')
            return {'CANCELLED'}

        if side == 'front' or side == 'back':
            x = scene.seut.bBox_X
            y = scene.seut.bBox_Z
        elif side == 'left' or side == 'right':
            x = scene.seut.bBox_Y
            y = scene.seut.bBox_Z
        elif side == 'top' or side == 'bottom':
            x = scene.seut.bBox_X
            y = scene.seut.bBox_Y

        # Ensure empty still exists
        try:
            area = create_mp_area(context, 'Mountpoint Area ' + side.capitalize(), 1, scale, scale, None, None, collection, bpy.data.objects['Mountpoints ' + side.capitalize()])
        except KeyError:
            seut_report(self, context, 'ERROR', True, 'E027', side.capitalize())
            return {'CANCELLED'}

        area.active_material = smat_mp

        scene.cursor.location = cursor_location

        return {'FINISHED'}
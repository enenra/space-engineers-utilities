import bpy
import re

from bpy.types  import Operator
from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty)

from .materials.seut_ot_create_material import create_material


names = {
    'seut': 'SEUT',
    'main': 'Main',
    'hkt': 'Collision',
    'lod': 'LOD',
    'bs': 'BS',
    'bs_lod': 'BS_LOD',
    'mountpoints': 'Mountpoints',
    'mirroring': 'Mirroring',
    'render': 'Render'
}

colors = {
    'seut': 'COLOR_02',
    'main': 'COLOR_04',
    'hkt': 'COLOR_08',
    'lod': 'COLOR_01',
    'bs': 'COLOR_05',
    'bs_lod': 'COLOR_06',
    'mountpoints': 'COLOR_03',
    'mirroring': 'COLOR_03',
    'render': 'COLOR_03'
}

# TODO: Need to adjust all places that use collections['lod1'], 2, 3 etc. and same for BS
# also everywhere that deals with hkt or bs_lod
# also structure conversion

def update_ref_col(self, context):
    scene = context.scene
    rename_collections(scene)


def poll_ref_col(self, object):
    collections = get_collections(self.scene)

    has_hkt = []

    for col in collections['hkt']:
        if not col.seut is self and not col.seut.ref_col is None:
            has_hkt.append(col.seut.ref_col)

    return self.scene == object.seut.scene and not object.seut.col_type is 'none' and object not in has_hkt and self.col_type == 'hkt' and (object.seut.col_type == 'main' or object.seut.col_type == 'bs')


def update_lod_distance(self, context):
    scene = context.scene
    collections = get_collections(scene)

    if not collections[self.col_type] is None:
        # This is to avoid a non-critical error where Blender expects a string for the contains check only in this particular instance. For reasons beyond human understanding.
        try:
            if self.type_index - 1 in collections[self.col_type]:
                if self.lod_distance <= collections[self.col_type][self.type_index - 1].seut.lod_distance:
                    self.lod_distance = collections[self.col_type][self.type_index - 1].seut.lod_distance + 1

            if self.type_index + 1 in collections[self.col_type]:
                if self.lod_distance >= collections[self.col_type][self.type_index + 1].seut.lod_distance:
                    collections[self.col_type][self.type_index + 1].seut.lod_distance = self.lod_distance + 1
        except TypeError:
            pass


class SEUT_Collection(PropertyGroup):
    """Holder for the varios collection properties"""
    
    scene: PointerProperty(
        type = bpy.types.Scene
    )
    
    col_type: EnumProperty(
        items=(
            ('none', 'None', ''),
            ('seut', 'SEUT', ''),
            ('main', 'Main', ''),
            ('hkt', 'Collision', ''),
            ('lod', 'LOD', ''),
            ('bs', 'BS', ''),
            ('bs_lod', 'BS_LOD', ''),
            ('mountpoints', 'Mountpoints', ''),
            ('mirroring', 'Mirroring', ''),
            ('render', 'Render', ''),
            )
    )

    ref_col: PointerProperty(
        name = "Reference",
        description = "The collection this collection is associated with",
        type = bpy.types.Collection,
        update = update_ref_col,
        poll = poll_ref_col
    )

    type_index: IntProperty(
        default = 0
    )

    lod_distance: IntProperty(
        name = "LOD Distance",
        description = "From what distance this LOD should display",
        default = 25,
        min = 0,
        update = update_lod_distance
    )


class SEUT_OT_RecreateCollections(Operator):
    """Recreates the collections"""
    bl_idname = "scene.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if not 'SEUT' in scene.view_layers:
            scene.view_layers[0].name = 'SEUT'

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
            scene.seut.subtypeBefore = scene.name
        
        for scn in bpy.data.scenes:
            if scene.seut.subtypeId == scn.seut.subtypeId:
                scene.seut.subtypeId = scene.name
                scene.seut.subtypeBefore = scene.name
                break
    
        if not 'SEUT Node Group' in bpy.data.node_groups or bpy.data.node_groups['SEUT Node Group'].library != None:
            temp_mat = create_material()
            bpy.data.materials.remove(temp_mat)

        create_collections(context)

        tag = ' (' + scene.seut.subtypeId + ')'
        context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children['Main' + tag]

        return {'FINISHED'}


class SEUT_OT_CreateCollection(Operator):
    """Creates a specific collection"""
    bl_idname = "scene.create_collection"
    bl_label = "Create Collection"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return 'SEUT' in context.scene.view_layers


    col_type: EnumProperty(
        items = (
            ('hkt', 'Collision', 'A collection containing collision objects, assigned to another collection in the scene'),
            ('lod', 'LOD', 'A Level of Detail (LOD) collection'),
            ('bs', 'BS', 'A Build Stage (BS) collection'),
            ('bs_lod', 'BS_LOD', 'A Build Stage Level of Detail (BS_LOD) collection'),
            ),
        name = "Collection Type"
    )


    def execute(self, context):

        scene = context.scene
        tag = ' (' + scene.seut.subtypeId + ')'
        collections = get_collections(scene)

        if self.col_type == 'lod' or self.col_type == 'bs' or self.col_type == 'bs_lod':

            # This handles the case in which collections are missing from the standard 3
            if 1 not in collections[self.col_type]:
                index = 1
            elif 2 not in collections[self.col_type]:
                index = 2
            elif 3 not in collections[self.col_type]:
                index = 3
            else:
                if len(collections[self.col_type]) + 1 in collections[self.col_type]:
                    temp_key = 4
                    while temp_key in collections[self.col_type]:
                        temp_key += 1
                    index = temp_key
                else:
                    index = len(collections[self.col_type]) + 1

            collection = bpy.data.collections.new(names[self.col_type] + str(index) + tag)
            collection.seut.type_index = index

            if index - 1 in collections[self.col_type]:
                collection.seut.lod_distance = collections[self.col_type][index - 1].seut.lod_distance + 1
        
        elif self.col_type == 'hkt':
            ref_col = context.view_layer.active_layer_collection.collection

            if ref_col.seut is None or ref_col.seut.col_type == 'hkt':
                ref_col = None

            for col in collections['hkt']:
                if col.seut.ref_col == ref_col:
                    ref_col = None
                    break

            if ref_col is None:
                collection = bpy.data.collections.new(names[self.col_type] + " - None" + tag)
            else:

                if ref_col.seut.col_type == 'lod' or ref_col.seut.col_type == 'bs' or ref_col.seut.col_type == 'bs_lod':
                    collection = bpy.data.collections.new(names[self.col_type] + " - " + names[ref_col.seut.col_type] + str(ref_col.seut.type_index) + tag)
                else:
                    collection = bpy.data.collections.new(names[self.col_type] + " - " + names[ref_col.seut.col_type] + tag)

                collection.seut.ref_col = ref_col

        collection.seut.col_type = self.col_type
        collection.seut.scene = scene
        if bpy.app.version >= (2, 91, 0):
            collection.color_tag = colors[self.col_type]
        collections['seut'].children.link(collection)

        return {'FINISHED'}


def get_collections(scene):
    """Scans existing collections to find the SEUT ones"""

    # Use the keys of names to create a new dict
    collections = {}
    for key in names.keys():
        collections[key] = None

    for col in bpy.data.collections:
        if col is None:
            continue
        if not col.seut.scene is scene:
            continue
        
        if col.seut.col_type is 'none':
            continue

        elif col.seut.col_type == 'hkt':
            if collections[col.seut.col_type] is None:
                collections[col.seut.col_type] = []

            collections[col.seut.col_type].append(col)

        elif col.seut.col_type == 'lod' or col.seut.col_type == 'bs' or col.seut.col_type == 'bs_lod':
            if collections[col.seut.col_type] is None:
                collections[col.seut.col_type] = {}

            collections[col.seut.col_type][col.seut.type_index] = col

        else:
            collections[col.seut.col_type] = col
    
    return collections


def rename_collections(scene):
    """Scans existing collections to find the SEUT ones and renames them if the tag has changed"""

    tag = ' (' + scene.seut.subtypeId + ')'
    
    # This ensures that after a full copy of a scene, the collections are reassigned to the new scene
    if scene.view_layers['SEUT'].layer_collection.children[0].collection.name.startswith("SEUT "):
        scene.view_layers['SEUT'].layer_collection.children[0].collection.seut.scene = scene
        for vl_col in scene.view_layers['SEUT'].layer_collection.children[0].children:
            if not vl_col.collection.seut.scene is scene:
                vl_col.collection.seut.scene = scene

    for col in bpy.data.collections:
        if col is None:
            continue
        if not col.seut.scene is scene:
            continue

        if col.seut.col_type == 'none':
            continue
        
        elif col.seut.col_type == 'lod' or col.seut.col_type == 'bs' or col.seut.col_type == 'bs_lod':
            col.name = names[col.seut.col_type] + str(col.seut.type_index) + " (" + col.seut.scene.seut.subtypeId + ")"

        elif col.seut.col_type == 'hkt':

            if col.seut.ref_col is None:
                col.name = names[col.seut.col_type] + " - None" + " (" + col.seut.scene.seut.subtypeId + ")"

            else:
                if col.seut.ref_col.seut.col_type == 'lod' or col.seut.ref_col.seut.col_type == 'bs' or col.seut.ref_col.seut.col_type == 'bs_lod':
                    col.name = names[col.seut.col_type] + " - " + names[col.seut.ref_col.seut.col_type] + str(col.seut.ref_col.seut.type_index) + " (" + col.seut.scene.seut.subtypeId + ")"
                else:
                    col.name = names[col.seut.col_type] + " - " + names[col.seut.ref_col.seut.col_type] + " (" + col.seut.scene.seut.subtypeId + ")"
        
        else:
            col.name = names[col.seut.col_type] + " (" + col.seut.scene.seut.subtypeId + ")"


def create_collections(context):
    """Recreates the collections SEUT requires"""

    scene = context.scene
    tag = ' (' + scene.seut.subtypeId + ')'
    collections = get_collections(scene)

    for key in collections.keys():
        if collections[key] == None:

            if key == 'seut':

                collections[key] = bpy.data.collections.new(names[key] + tag)
                collections[key].seut.scene = scene
                collections[key].seut.col_type = key
                if bpy.app.version >= (2, 91, 0):
                    collections[key].color_tag = colors[key]
                scene.collection.children.link(collections[key])

            elif key == 'main':
                collections[key] = bpy.data.collections.new(names[key] + tag)
                collections[key].seut.scene = scene
                collections[key].seut.col_type = key
                if bpy.app.version >= (2, 91, 0):
                    collections[key].color_tag = colors[key]
                collections['seut'].children.link(collections[key])

            elif key == 'lod' or key == 'bs':

                collections[key] = {}

                # Keeping ['0'] for LOD0 support I may add in the future
                collections[key][1] = bpy.data.collections.new(names[key] + '1' + tag)
                collections[key][1].seut.scene = scene
                collections[key][1].seut.col_type = key
                collections[key][1].seut.type_index = 1
                if bpy.app.version >= (2, 91, 0):
                    collections[key][1].color_tag = colors[key]
                collections['seut'].children.link(collections[key][1])

                collections[key][2] = bpy.data.collections.new(names[key] + '2' + tag)
                collections[key][2].seut.scene = scene
                collections[key][2].seut.col_type = key
                collections[key][2].seut.type_index = 2
                if bpy.app.version >= (2, 91, 0):
                    collections[key][2].color_tag = colors[key]
                collections['seut'].children.link(collections[key][2])

                collections[key][3] = bpy.data.collections.new(names[key] + '3' + tag)
                collections[key][3].seut.scene = scene
                collections[key][3].seut.col_type = key
                collections[key][3].seut.type_index = 3
                if bpy.app.version >= (2, 91, 0):
                    collections[key][3].color_tag = colors[key]
                collections['seut'].children.link(collections[key][3])

                if key == 'lod':
                    collections[key][1].seut.lod_distance = 25
                    collections[key][2].seut.lod_distance = 50
                    collections[key][3].seut.lod_distance = 150

            elif key == 'hkt':
                temp_col = bpy.data.collections.new(names[key] + " - Main" + tag)
                collections[key] = []
                collections[key].append(temp_col)
                temp_col.seut.scene = scene
                temp_col.seut.col_type = key
                if bpy.app.version >= (2, 91, 0):
                    temp_col.color_tag = colors[key]
                collections['seut'].children.link(temp_col)

            elif key == 'bs_lod':
                collections[key] = {}
                collections[key][1] = bpy.data.collections.new(names[key] + '1' + tag)
                collections[key][1].seut.scene = scene
                collections[key][1].seut.col_type = key
                collections[key][1].seut.type_index = 1
                collections[key][1].seut.lod_distance = 50
                if bpy.app.version >= (2, 91, 0):
                    collections[key][1].color_tag = colors[key]
                collections['seut'].children.link(collections[key][1])
    
    # This needs to be separate because else it can cause issues if main doesn't exist yet.
    for col in bpy.data.collections:
        if col is None:
            continue
        if col.seut.scene is None:
            continue

        tag = ' (' + col.seut.scene.seut.subtypeId + ')'
        if col.seut.col_type == 'hkt' and 'Main' + tag in bpy.data.collections:
            col.seut.ref_col = bpy.data.collections['Main' + tag]

    return collections
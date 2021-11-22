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

seut_collections = {
    'mainScene':{
        'main': {
            'name': 'Main',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
        'hkt': {
            'name': 'Collision',
            'schema': 'Collision - {ref_col_name}{ref_col_type_index} ({subtpye_id})',
            'color': 'COLOR_08'
            },
        'lod': {
            'name': 'LOD',
            'schema': 'LOD{type_index} ({subtpye_id})',
            'color': 'COLOR_01'
            },
        'bs': {
            'name': 'BS',
            'schema': 'BS{type_index} ({subtpye_id})',
            'color': 'COLOR_05'
            },
        'mountpoints': {
            'name': 'Mountpoints',
            'schema': 'Mountpoints ({subtpye_id})',
            'color': 'COLOR_03'
            },
        'mirroring': {
            'name': 'Mirroring',
            'schema': 'Mirroring ({subtpye_id})',
            'color': 'COLOR_03'
            },
        'render': {
            'name': 'Render',
            'schema': 'Render ({subtpye_id})',
            'color': 'COLOR_03'
            }
    },
    'subpart': {
        'main': {
            'name': 'Main',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
        'hkt': {
            'name': 'Collision',
            'schema': 'Collision - {ref_col_name}{ref_col_type_index} ({subtpye_id})',
            'color': 'COLOR_08'
            },
        'lod': {
            'name': 'LOD',
            'schema': 'LOD{type_index} ({subtpye_id})',
            'color': 'COLOR_01'
            },
        'bs': {
            'name': 'BS',
            'schema': 'BS{type_index} ({subtpye_id})',
            'color': 'COLOR_05'
            }
    },
    'character': {
        'main': {
            'name': 'Main',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
        'hkt': {
            'name': 'Collision',
            'schema': 'Collision - {ref_col_name}{ref_col_type_index} ({subtpye_id})',
            'color': 'COLOR_08'
            },
        'lod': {
            'name': 'LOD',
            'schema': 'LOD{type_index} ({subtpye_id})',
            'color': 'COLOR_01'
            },
    },
    'character_animation': {
        'main': {
            'name': 'Main',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
    },
    'particle_effect': {
        'main': {
            'name': 'Main',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
    }
}


def update_ref_col(self, context):
    scene = context.scene
    rename_collections(scene)


def poll_ref_col(self, object):
    collections = get_collections(self.scene)

    check = self.scene == object.seut.scene and object.seut.col_type != 'none' and object.seut.col_type in ['main', 'bs']

    if self.col_type == 'hkt':
        return check and get_rev_ref_col(collections, self.ref_col, 'hkt') is None
    
    elif self.col_type == 'lod':
        return check


def update_lod_distance(self, context):
    scene = context.scene

    if self.col_type is None or self.col_type == 'none':
        return

    ref_col = None
    if self.ref_col is not None:
        ref_col = self.ref_col
    cols = get_cols_by_type(scene, self.col_type, ref_col.seut.col_type)

    if cols != {}:
        # This is to avoid a non-critical error where Blender expects a string for the contains check only in this particular instance. For reasons beyond human understanding.
        try:
            if self.type_index - 1 in cols:
                if self.lod_distance <= cols[self.type_index - 1].seut.lod_distance:
                    self.lod_distance = cols[self.type_index - 1].seut.lod_distance + 1

            if self.type_index + 1 in cols:
                if self.lod_distance >= cols[self.type_index + 1].seut.lod_distance:
                    cols[self.type_index + 1].seut.lod_distance = self.lod_distance + 1
        except TypeError:
            pass


class SEUT_Collection(PropertyGroup):
    """Holder for the varios collection properties"""

    version: IntProperty(
        name="SEUT Collection Version",
        description="Used as a reference to patch the SEUT collection properties to newer versions",
        default=1
    )
    
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
            scene.eevee.use_bloom = True

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
            ),
        name = "Collection Type"
    )


    def execute(self, context):

        scene = context.scene
        collections = get_collections(scene)
        
        if self.col_type == 'none':
            return {'CANCELLED'}

        index = None
        ref_col = None

        if scene.seut.sceneType == 'mainScene':
                
            if self.col_type == 'hkt':
                ref_col = context.view_layer.active_layer_collection.collection

                if ref_col.seut is None or ref_col.seut.col_type in ['hkt', 'lod']:
                    ref_col = None
                
                if get_rev_ref_col(collections, ref_col, 'hkt') is not None:
                    return {'FINISHED'}
            
            elif self.col_type == 'lod':
                ref_col = context.view_layer.active_layer_collection.collection

                if ref_col.seut is None or ref_col.seut.col_type in ['hkt', 'lod']:
                    ref_col = None

                index = get_first_free_index(get_cols_by_type(scene, self.col_type))
            
            else:
                index = get_first_free_index(get_cols_by_type(scene, self.col_type))

        create_seut_collection(context, self.col_type, index, ref_col)

        return {'FINISHED'}


def get_collections(scene: object) -> dict:
    """Scans the existing collections of a scene to find the SEUT ones."""

    collections = {}
    for key in seut_collections[scene.seut.sceneType].keys():
        collections[key] = None

    for col in bpy.data.collections:
        if col is None:
            continue
        if not col.seut.scene is scene:
            continue
        
        if col.seut.col_type == 'none':
            continue
        else:
            if collections[col.seut.col_type] is None:
                collections[col.seut.col_type] = []
            collections[col.seut.col_type].append(col)
    
    return collections


def rename_collections(scene: object):
    """Scans existing collections to find the SEUT ones and renames them if the tag has changed."""
    
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

        name = seut_collections[scene.seut.sceneType][col.seut.col_type]['schema']
        color = seut_collections[scene.seut.sceneType][col.seut.col_type]['color']

        type_index = ""
        if col.seut.type_index != 0:
            type_index = col.seut.type_index

        ref_col = None
        if col.seut.ref_col is not None:
            ref_col = col.seut.ref_col
            ref_col_type = ref_col.seut.col_type
            ref_col_name = seut_collections[scene.seut.sceneType][ref_col_type]['name']

        if col.seut.col_type == 'lod':
            if col.seut.ref_col.seut.col_type != 'main':
                name = f"{ref_col_name}{ref_col.seut.type_index}_{seut_collections[scene.seut.sceneType]['lod']['name']}{type_index} ({scene.seut.subtypeId})"
                color = 'COLOR_06'
        
        col.name = name.format(subtpye_id=scene.seut.subtypeId, ref_col_name=ref_col.seut.col_type, ref_col_type_index=ref_col.seut.type_index, type_index=type_index)
        if bpy.app.version >= (2, 91, 0):
            col.color_tag = color


def create_collections(context):
    """Recreates the collections SEUT requires"""

    scene = context.scene
    collections = get_collections(scene)

    for key in collections.keys():
        if collections[key] == None:

            if key == 'seut':

                collections['seut'] = bpy.data.collections.new(f"SEUT ({scene.seut.subtypeId})")
                collections['seut'].seut.scene = scene
                collections['seut'].seut.col_type = 'seut'
                if bpy.app.version >= (2, 91, 0):
                    collections['seut'].color_tag = 'COLOR_02'
                scene.collection.children.link(collections['seut'])
            
            elif key == 'main':
                collections['main'].append([create_seut_collection(context, 'main')])
            elif key == 'bs':
                collections['bs'].append([
                        create_seut_collection(context, 'bs', 1),
                        create_seut_collection(context, 'bs', 2),
                        create_seut_collection(context, 'bs', 3)
                    ])

    # In two loops to ensure the cols that are referenced exist.
    for key in collections.keys():
        if collections[key] == None:

            if key == 'hkt':
                collections['hkt'].append([create_seut_collection(context, 'hkt', ref_col=get_seut_collection(scene, 'main'))])

            elif key == 'lod':
                collections['lod'].append([
                        create_seut_collection(context, 'lod', 1, collections['main']),
                        create_seut_collection(context, 'lod', 2, collections['main']),
                        create_seut_collection(context, 'lod', 3, collections['main']),
                        create_seut_collection(context, 'lod', 1, get_seut_collection(scene, 'bs', type_index=1))
                    ])

    sort_collections(context)

    return collections


def create_seut_collection(context, col_type: str, type_index=None, ref_col=None):
    """Creates a SEUT collection with the specified characteristics."""

    scene = context.scene
    collections = get_collections(scene)

    name = seut_collections[scene.seut.sceneType][col_type]['schema']
    color = seut_collections[scene.seut.sceneType][col_type]['color']
    lod_distance = 0
    ref_col_name = ""
    ref_col_type_index = ""
    
    if 'seut' not in collections or col_type not in collections:
        collections = create_collections(context)

    if scene.seut.subtypeId == 'mainScene':

        # Main
        if col_type == 'main':
            pass

        # HKT
        elif col_type == 'hkt':
            if ref_col is None:
                ref_col_name = 'None'
            else:
                ref_col_name = f"{seut_collections[scene.seut.sceneType][ref_col.seut.col_type]['name']}"
                if ref_col.seut.col_type == 'bs':
                    ref_col_name += ref_col.seut.type_index

        # BS
        elif col_type == 'bs':
            if type_index is not None:
                if type_index in collections['bs'] and not collections['bs'][type_index] is None:
                    return collections['bs'][type_index]
            else:
                type_index = len(collections['bs'])

        # LOD
        elif col_type == 'lod':
            if ref_col is None:
                return False

            cols = get_cols_by_type(scene, 'lod', ref_col.seut.col_type)

            if type_index is not None:
                if type_index in cols:
                    return cols[type_index]
            else:
                if cols != {}:
                    type_index = len(cols)
                else:
                    type_index = 1
            
            if type_index == 1:
                lod_distance = 25
            else:
                lod_distance = cols[type_index - 1].seut.lod_distance * 2

            if ref_col.seut.col_type != 'main':
                ref_col_type = ref_col.seut.col_type
                ref_col_name = seut_collections[scene.seut.sceneType][ref_col_type]['name']
                ref_col_type_index = ref_col.seut.type_index
                name = f"{ref_col_name}{ref_col.seut.type_index}_{seut_collections[scene.seut.sceneType]['lod']['name']}{type_index} ({scene.seut.subtypeId})"
                color = 'COLOR_06'
    
    if type_index is None:
        type_index = ""
    name = name.format(subtpye_id=scene.seut.subtypeId, ref_col_name=ref_col_name, ref_col_type_index=ref_col_type_index, type_index=type_index)

    collection = bpy.data.collections.new(name)
    collection.seut.scene = scene
    collection.seut.col_type = col_type
    if type_index is not None:
        collection.seut.type_index = type_index
    if ref_col is not None:
        collection.seut.ref_col = ref_col
    if lod_distance != 0:
        collection.seut.lod_distance = lod_distance
    if bpy.app.version >= (2, 91, 0):
        collection.color_tag = color
    collections['seut'].children.link(collection)

    return collection


def sort_collections(context):

    scene = context.scene
    collections = get_collections(scene)
    seut_cols = collections['seut'].children
        
    for bs in sorted(collections['bs'], key=lambda bs: bs.seut.type_index):
        seut_cols.unlink(bs)
        seut_cols.link(bs)
        hkt = get_rev_ref_col(collections, bs, 'hkt')
        if not hkt is None:
            seut_cols.unlink(hkt)
            seut_cols.link(hkt)
    
    for lod in sorted(get_cols_by_type(scene, 'lod', 'main'), key=lambda lod: lod.seut.type_index):
        seut_cols.unlink(lod)
        seut_cols.link(lod)
        
    for lod in sorted(get_cols_by_type(scene, 'lod', 'bs'), key=lambda lod: lod.seut.type_index):
        seut_cols.unlink(lod)
        seut_cols.link(lod)


def get_cols_by_type(scene, col_type: str, ref_col_type: str = None) -> dict:
    """Returns a dict of cols with specified characteristics."""

    collections = get_collections(scene)
    cols_by_type = {}

    for col in collections[col_type]:
        if ref_col_type is not None and col.seut.ref_col.seut.col_type != ref_col_type:
            continue
        cols_by_type[col.type_index] = col
    
    return cols_by_type


def get_seut_collection(scene, col_type: str, ref_col_type: str = None, type_index: int = None) -> object:
    """Returns the first collection found with specified characteristics, None if none found."""

    collections = get_collections(scene)

    for col in collections[col_type]:
        if ref_col_type is not None and col.seut.ref_col.seut.col_type != ref_col_type:
            continue
        if type_index is not None and col.seut.type_index != type_index:
            continue
        return col
    
    return None


def get_rev_ref_col(collections: dict, collection: object, col_type: str):
    """Returns the first collection found which references the specified collection."""

    if collections[col_type] == None:
        return None

    for col in collections[col_type]:
        if col.seut.ref_col == collection:
            return col
            
    return None


def get_first_free_index(collections: dict) -> int:
    """Returns the first free index of the given dict of collections"""

    if collections == {} or 1 not in collections:
        index = 1
    else:
        temp_key = 2
        while temp_key in collections:
            temp_key += 1
        index = temp_key
    
    return index
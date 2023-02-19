import bpy
import os

from bpy.types  import Operator
from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty)

from .seut_errors                       import seut_report
from .materials.seut_ot_create_material import create_material

seut_collections = {
    'mainScene':{
        'main': {
            'name': 'Main',
            'type': 'Main Model',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
        'hkt': {
            'name': 'Collision',
            'type': 'Collision Objects',
            'schema': 'Collision - {ref_col_name}{ref_col_type_index} ({subtpye_id})',
            'color': 'COLOR_08'
            },
        'lod': {
            'name': 'LOD',
            'type': 'Level of Detail',
            'schema': 'LOD{type_index} ({subtpye_id})',
            'color': 'COLOR_01'
            },
        'bs': {
            'name': 'BS',
            'type': 'Build Stage Model',
            'schema': 'BS{type_index} ({subtpye_id})',
            'color': 'COLOR_05'
            },
        'mountpoints': {
            'name': 'Mountpoints',
            'type': 'Mountpoint Information',
            'schema': 'Mountpoints ({subtpye_id})',
            'color': 'COLOR_03'
            },
        'mirroring': {
            'name': 'Mirroring',
            'type': 'Mirroring Information',
            'schema': 'Mirroring ({subtpye_id})',
            'color': 'COLOR_03'
            },
        'render': {
            'name': 'Render',
            'type': 'Render Rig',
            'schema': 'Render ({subtpye_id})',
            'color': 'COLOR_03'
            }
    },
    'subpart': {
        'main': {
            'name': 'Main',
            'type': 'Subpart Model',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
        'hkt': {
            'name': 'Collision',
            'type': 'Collision Objects',
            'schema': 'Collision - {ref_col_name}{ref_col_type_index} ({subtpye_id})',
            'color': 'COLOR_08'
            },
        'lod': {
            'name': 'LOD',
            'type': 'Level of Detail',
            'schema': 'LOD{type_index} ({subtpye_id})',
            'color': 'COLOR_01'
            },
        'bs': {
            'name': 'BS',
            'type': 'Build Stage Model',
            'schema': 'BS{type_index} ({subtpye_id})',
            'color': 'COLOR_05'
            }
    },
    'character': {
        'main': {
            'name': 'Main',
            'type': 'Character Model',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
        'hkt': {
            'name': 'Collision',
            'type': 'Collision Objects',
            'schema': 'Collision - {ref_col_name}{ref_col_type_index} ({subtpye_id})',
            'color': 'COLOR_08'
            },
        'lod': {
            'name': 'LOD',
            'type': 'Level of Detail',
            'schema': 'LOD{type_index} ({subtpye_id})',
            'color': 'COLOR_01'
            },
    },
    'character_animation': {
        'main': {
            'name': 'Main',
            'type': 'Character Animation',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
    },
    'planet_editor': {
        'main': {
            'name': 'Main',
            'type': 'Planet Editor',
            'schema': 'Main ({subtpye_id})',
            'color': 'COLOR_04'
            },
    }
}


def update_ref_col(self, context):
    scene = self.scene

    self.type_index = 0
    if self.ref_col is not None:
        cols = get_cols_by_type(scene, self.col_type, self.ref_col)
        for key, col in cols.items():
            if col.seut == self:
                del cols[key]
                break
        self.type_index = get_first_free_index(cols)
        
        if self.col_type == 'lod':
            if self.type_index - 1 in cols:
                col = cols[self.type_index - 1]
                if self.lod_distance <= col.seut.lod_distance:
                    self.lod_distance = col.seut.lod_distance + 1
            if self.type_index + 1 in cols:
                col = cols[self.type_index + 1]
                if self.lod_distance >= col.seut.lod_distance:
                    self.lod_distance = col.seut.lod_distance - 1

    rename_collections(scene)
    # This can error on scene init.
    try:
        sort_collections(scene, context)
    except:
        pass


def poll_ref_col(self, object):
    collections = get_collections(self.scene)

    check = self.scene == object.seut.scene and object.seut.col_type != 'none' and object.seut.col_type in ['main', 'bs']

    if self.col_type == 'hkt':
        hkt = get_rev_ref_cols(collections, object, 'hkt')
        is_self = False
        if hkt != []:
            is_self = hkt[0].seut == self
        return check and (hkt == [] or is_self)
    
    elif self.col_type == 'lod':
        return check


def update_lod_distance(self, context):
    scene = context.scene

    if self.col_type is None or self.col_type == 'none':
        return

    cols = get_cols_by_type(scene, self.col_type, self.ref_col)

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

def update_hkt_file(self, context):

    if self.hkt_file in ["", self.hkt_file_before]:
        self.hkt_file_before = self.hkt_file
        return
    
    if os.path.isdir(self.hkt_file) or os.path.splitext(self.hkt_file)[1].lower() != '.hkt':
        seut_report(self, context, 'ERROR', False, 'E015', 'External Collision File', '.hkt')
        self.hkt_file = self.hkt_file_before
        
    self.hkt_file_before = self.hkt_file


class SEUT_Collection(PropertyGroup):
    """Holder for the varios collection properties"""

    version: IntProperty(
        name="SEUT Collection Version",
        description="Used as a reference to patch the SEUT collection properties to newer versions",
        default=0 # current: 3
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

    hkt_file: StringProperty(
        name = "Ext. File",
        description = "External HKT file to be used as the collision instead of any objects defined in this collision collection",
        subtype = "FILE_PATH",
        update = update_hkt_file
        )

    hkt_file_before: StringProperty(
        subtype = "FILE_PATH"
        )


class SEUT_OT_RecreateCollections(Operator):
    """Recreates any missing collections for the current scene type"""
    bl_idname = "scene.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene
        scene.render.fps = 60

        if not 'SEUT' in scene.view_layers:
            scene.view_layers[0].name = 'SEUT'
            scene.seut.version = 4
            scene.eevee.use_bloom = True

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
            scene.seut.subtypeBefore = scene.name
        
        for scn in bpy.data.scenes:
            if scene.seut.subtypeId == scn.seut.subtypeId:
                scene.seut.subtypeId = scene.name
                scene.seut.subtypeBefore = scene.name
                break

        create_collections(scene, context)

        tag = ' (' + scene.seut.subtypeId + ')'
        context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children['Main' + tag]

        return {'FINISHED'}


class SEUT_OT_CreateCollection(Operator):
    """Creates a collection, referencing the active one if applicable"""
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

        if not self.col_type in seut_collections[scene.seut.sceneType]:
            return {'FINISHED'}
            
        if self.col_type == 'hkt':
            ref_col = context.view_layer.active_layer_collection.collection

            if ref_col.seut.col_type == 'none' or ref_col.seut.col_type in ['hkt', 'lod']:
                return {'FINISHED'}
            
            if get_rev_ref_cols(collections, ref_col, 'hkt') != []:
                return {'FINISHED'}
        
        elif self.col_type == 'lod':
            ref_col = context.view_layer.active_layer_collection.collection

            if ref_col.seut.col_type == 'none' or ref_col.seut.col_type in ['hkt', 'lod']:
                return {'FINISHED'}

            index = get_first_free_index(get_cols_by_type(scene, self.col_type, ref_col))
        
        else:
            index = get_first_free_index(get_cols_by_type(scene, self.col_type))

        create_seut_collection(scene, self.col_type, index, ref_col)
        sort_collections(scene, context)

        return {'FINISHED'}


def get_collections(scene: object, inclusive: bool = False) -> dict:
    """Scans the existing collections of a scene to find the SEUT ones. Inclusive returns all collections, including ones disallowed by sceneType."""

    collections = {}
    collections['seut'] = None
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
            if not inclusive and not col.seut.col_type in seut_collections[scene.seut.sceneType] and not col.seut.col_type == 'seut':
                continue
            if inclusive:
                if not col.seut.col_type in collections:
                    collections[col.seut.col_type] = None
            if collections[col.seut.col_type] is None:
                collections[col.seut.col_type] = []
            collections[col.seut.col_type].append(col)
    
    return collections


def rename_collections(scene: object):
    """Scans existing collections to find the SEUT ones and renames them if the tag has changed."""
    
    # This ensures that after a full copy of a scene, the collections are reassigned to the new scene
    if len(scene.view_layers['SEUT'].layer_collection.children) < 1:
        return

    for vl_col in scene.view_layers['SEUT'].layer_collection.children:
        if vl_col.name.startswith("SEUT "):
            vl_col.collection.seut.scene = scene
            for vl_col in scene.view_layers['SEUT'].layer_collection.children[vl_col.name].children:
                if vl_col.collection.seut.scene is not scene:
                    vl_col.collection.seut.scene = scene
            break

    for col in bpy.data.collections:
        if col is None:
            continue
        if col.seut.scene is not scene:
            continue
        if col.seut.col_type == 'none':
            continue
        if col.seut.col_type not in seut_collections[scene.seut.sceneType] and col.seut.col_type != 'seut':
            col.color_tag = 'COLOR_07'
            continue

        if col.seut.col_type == 'seut':
            name = f"SEUT ({scene.seut.subtypeId})"
            color = 'COLOR_02'
        else:
            name = seut_collections[scene.seut.sceneType][col.seut.col_type]['schema']
            color = seut_collections[scene.seut.sceneType][col.seut.col_type]['color']

        type_index = ""
        if col.seut.type_index != 0:
            type_index = col.seut.type_index

        ref_col_name = ""
        ref_col_type_index = ""
        ref_col = None
        if col.seut.ref_col is not None:
            ref_col = col.seut.ref_col

            if ref_col.seut.col_type not in seut_collections[scene.seut.sceneType]:
                continue

            ref_col_type = ref_col.seut.col_type
            ref_col_name = seut_collections[scene.seut.sceneType][ref_col_type]['name']
            if ref_col_type != 'main':
                ref_col_type_index = ref_col.seut.type_index

            if col.seut.col_type == 'lod' and col.seut.ref_col.seut.col_type != 'main':
                name = f"{ref_col_name}{ref_col.seut.type_index}_{seut_collections[scene.seut.sceneType]['lod']['name']}{type_index} ({scene.seut.subtypeId})"
                color = 'COLOR_06'
        else:
            ref_col_name = "None"
            if col.seut.col_type == 'lod':
                name = f"{seut_collections[scene.seut.sceneType]['lod']['name']} ({scene.seut.subtypeId})"

        col.name = name.format(subtpye_id=scene.seut.subtypeId, ref_col_name=ref_col_name, ref_col_type_index=ref_col_type_index, type_index=type_index)
        col.color_tag = color


def create_collections(scene, context = None):
    """Recreates the collections SEUT requires"""

    collections = get_collections(scene)

    if collections['seut'] is None:
        collections['seut'] = []
        collections['seut'].append(bpy.data.collections.new(f"SEUT ({scene.seut.subtypeId})"))
        collections['seut'][0].seut.scene = scene
        collections['seut'][0].seut.col_type = 'seut'
        collections['seut'][0].seut.version = 3
        collections['seut'][0].color_tag = 'COLOR_02'
        scene.collection.children.link(collections['seut'][0])


    for key in collections.keys():
        if collections[key] == None:
            if key == 'main':
                collections['main'] = []
                collections['main'].append(create_seut_collection(scene, 'main'))
            elif key == 'bs':
                collections['bs'] = []
                collections['bs'].append(create_seut_collection(scene, 'bs', 1))
                collections['bs'].append(create_seut_collection(scene, 'bs', 2))
                collections['bs'].append(create_seut_collection(scene, 'bs', 3))

    # In two loops to ensure the cols that are referenced exist.
    for key in collections.keys():
        if collections[key] == None:

            if key == 'hkt':
                collections['hkt'] = []
                collections['hkt'].append(create_seut_collection(scene, 'hkt', ref_col=get_seut_collection(scene, 'main')))

            elif key == 'lod':
                collections['lod'] = []
                collections['lod'].append(create_seut_collection(scene, 'lod', 1, collections['main'][0]))
                collections['lod'].append(create_seut_collection(scene, 'lod', 2, collections['main'][0]))
                collections['lod'].append(create_seut_collection(scene, 'lod', 3, collections['main'][0]))
                if 'bs' in collections and len(collections['bs']) > 0:
                    collections['lod'].append(create_seut_collection(scene, 'lod', 1, get_seut_collection(scene, 'bs', type_index=1)))

    sort_collections(scene, context)

    return collections


def create_seut_collection(scene, col_type: str, type_index=None, ref_col=None):
    """Creates a SEUT collection with the specified characteristics."""

    collections = get_collections(scene)

    name = seut_collections[scene.seut.sceneType][col_type]['schema']
    color = seut_collections[scene.seut.sceneType][col_type]['color']
    lod_distance = 0
    ref_col_name = ""
    ref_col_type_index = ""
    
    if 'seut' not in collections or col_type not in collections:
        collections = create_collections(scene)

    if scene.seut.sceneType == 'mainScene':

        # Main
        if col_type == 'main':
            pass

        # HKT
        elif col_type == 'hkt':
            if ref_col is None or ref_col.seut.col_type in ['none', 'seut']:
                ref_col_name = 'None'
            else:
                ref_col_name = f"{seut_collections[scene.seut.sceneType][ref_col.seut.col_type]['name']}"
                if ref_col.seut.col_type == 'bs':
                    ref_col_type_index = ref_col.seut.type_index

        # BS
        elif col_type == 'bs':
            if collections['bs'] is not None:
                if type_index is not None:
                    if type_index in collections['bs'] and not collections['bs'][type_index] is None:
                        return collections['bs'][type_index]
                else:
                    type_index = len(collections['bs'])
            else:
                type_index = 1

        # LOD
        elif col_type == 'lod':
            if ref_col is None or ref_col.seut.col_type in ['none', 'seut']:
                return None

            cols = get_cols_by_type(scene, 'lod', ref_col)

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
        type_index = 0
    name = name.format(subtpye_id=scene.seut.subtypeId, ref_col_name=ref_col_name, ref_col_type_index=ref_col_type_index, type_index=type_index)

    collection = bpy.data.collections.new(name)
    collection.seut.version = 3
    collection.seut.scene = scene
    collection.seut.col_type = col_type
    if type_index is not None:
        collection.seut.type_index = type_index
    if ref_col is not None:
        collection.seut.ref_col = ref_col
    if lod_distance != 0:
        collection.seut.lod_distance = lod_distance
    collection.color_tag = color
    
    if 'seut' in collections and collections['seut'] is not None:
        collections['seut'][0].children.link(collection)
    elif f"SEUT ({scene.seut.subtypeId})" in scene.view_layers['SEUT'].layer_collection.children:
        scene.view_layers['SEUT'].layer_collection.children[f"SEUT ({scene.seut.subtypeId})"].children.link(collection)
    else:
        return None

    return collection


def sort_collections(scene, context = None):

    if context is not None:
        active_col = context.view_layer.active_layer_collection.collection
        col_props = [
            active_col.seut.col_type,
            active_col.seut.type_index,
            active_col.seut.ref_col
        ]

    collections = get_collections(scene)

    if collections['seut'] is None:
        return

    seut_cols = collections['seut'][0].children
    vl_cols = scene.view_layers['SEUT'].layer_collection.children[collections['seut'][0].name].children
    
    if 'bs' in collections and collections['bs'] is not None:
        for bs in sorted(collections['bs'], key=lambda bs: bs.seut.type_index):
            hide = vl_cols[bs.name].hide_viewport
            seut_cols.unlink(bs)
            seut_cols.link(bs)
            vl_cols[bs.name].hide_viewport = hide
            hkt = get_rev_ref_cols(collections, bs, 'hkt')
            if hkt != []:
                hide = vl_cols[hkt[0].name].hide_viewport
                seut_cols.unlink(hkt[0])
                seut_cols.link(hkt[0])
                vl_cols[hkt[0].name].hide_viewport = hide
    
    if 'lod' in collections and collections['lod'] is not None:
        for lod in sorted(get_cols_by_type(scene, 'lod', collections['main'][0]).values(), key=lambda lod: lod.seut.type_index):
            hide = vl_cols[lod.name].hide_viewport
            seut_cols.unlink(lod)
            seut_cols.link(lod)
            vl_cols[lod.name].hide_viewport = hide
    
    if 'bs' in collections and 'lod' in collections and collections['bs'] is not None and collections['lod'] is not None:
        for bs in sorted(collections['bs'], key=lambda bs: bs.seut.type_index):
            for lod in sorted(get_cols_by_type(scene, 'lod', bs).values(), key=lambda lod: lod.seut.type_index):
                hide = vl_cols[lod.name].hide_viewport
                seut_cols.unlink(lod)
                seut_cols.link(lod)
                vl_cols[lod.name].hide_viewport = hide
    
    if context is not None:
        layer_col_parent = scene.view_layers['SEUT'].layer_collection.children[f"SEUT ({scene.seut.subtypeId})"]
        name = ""

        if col_props[0] != 'none':
            for col in get_cols_by_type(scene, col_props[0], col_props[2]).values():
                if col.seut.type_index == col_props[1]:
                    name = col.name
            if name != layer_col_parent.name:
                context.view_layer.active_layer_collection = layer_col_parent.children[name]
            else:
                context.view_layer.active_layer_collection = layer_col_parent


def get_cols_by_type(scene, col_type: str, ref_col: object = None) -> dict:
    """Returns a dict of cols with specified characteristics."""

    collections = get_collections(scene)
    cols_by_type = {}

    if col_type in collections:
        if collections[col_type] is not None:
            for col in collections[col_type]:
                if ref_col is not None:
                    if col.seut.ref_col == ref_col:
                        cols_by_type[col.seut.type_index] = col
                else:
                    cols_by_type[col.seut.type_index] = col

    return cols_by_type


def get_seut_collection(scene, col_type: str, ref_col_type: str = None, type_index: int = None) -> object:
    """Returns the first collection found with specified characteristics, None if none found."""

    collections = get_collections(scene)

    if col_type in collections:
        for col in collections[col_type]:
            if ref_col_type is not None and col.seut.ref_col.seut.col_type != ref_col_type:
                continue
            if type_index is not None and col.seut.type_index != type_index:
                continue
            return col
    
    return None


def get_rev_ref_cols(collections: dict, collection: object, col_type: str) -> list:
    """Returns a list of all collections found (of a specified col_type) which reference the specified collection."""

    output = []

    if col_type not in collections:
        return output

    if collections[col_type] == None:
        return output

    for col in collections[col_type]:
        if col.seut.ref_col == collection:
            output.append(col)
            
    return output


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
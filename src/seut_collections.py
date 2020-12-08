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
    'lod1': 'LOD1',
    'lod2': 'LOD2',
    'lod3': 'LOD3',
    'bs1': 'BS1',
    'bs2': 'BS2',
    'bs3': 'BS3',
    'bs_lod': 'BS_LOD',
    'mountpoints': 'Mountpoints',
    'mirroring': 'Mirroring',
    'render': 'Render'
}

colors = {
    'seut': 'COLOR_01',
    'main': 'COLOR_01',
    'hkt': 'COLOR_01',
    'lod': 'COLOR_01',
    'bs': 'COLOR_01',
    'bs_lod': 'COLOR_01',
    'mountpoints': 'COLOR_01',
    'mirroring': 'COLOR_01',
    'render': 'COLOR_01'
}


class SEUT_Collection(PropertyGroup):
    """Holder for the varios collection properties"""
    
    scene: PointerProperty(
        type=bpy.types.Scene
    )
    
    col_type: EnumProperty(
        items=(
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

    type_index: IntProperty(
        default = 0
    )

    lod_distance: IntProperty(
        name = "LOD Distance",
        description = "From what distance this LOD should display",
        default = 25,
        min = 0
    )


class SEUT_OT_RecreateCollections(Operator):
    """Recreates the collections"""
    bl_idname = "scene.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if not 'SEUT' in scene.view_layers:
            # This errors sometimes if it's triggered from draw in the toolbar
            try:
                scene.view_layers[0].name = 'SEUT'
            except:
                pass

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


def get_collections(scene):
    """Scans existing collections to find the SEUT ones"""

    # Use the keys of names to create a new dict
    collections = {}
    for key in names.keys():
        collections[key] = None

    if not 'SEUT' in scene.view_layers:
        # This errors sometimes if it's triggered from draw in the toolbar
        try:
            scene.view_layers[0].name = 'SEUT'
        except:
            pass

    for col in bpy.data.collections:

        if col is None:
            continue
        
        # This is for backwards compatibility with old system.
        if col.seut.scene is None and re.search("\(" + scene.seut.subtypeId + "\)", col.name) != None:
            col.seut.scene = scene
            raw_type = re.match("([^ ]+) .*", col.name)
            temp_type = re.match("/[^[0-9]]*/", raw_type).lower()

            if temp_type == "collision":
                col.seut.col_type = "hkt"
            else:
                col.seut.col_type = temp_type

            if len(temp_type) != len(raw_type):
                col.seut.type_index = raw_type[len(temp_type):]
            else:
                col.seut.type_index = 0

        elif not col.seut.scene is scene:
            continue

        if col.seut.type_index > 0:
            collections[col.seut.col_type + str(col.seut.type_index)] = col
        else:
            collections[col.seut.col_type] = col
    
    return collections


def rename_collections(scene):
    """Scans existing collections to find the SEUT ones and renames them if the tag has changed"""

    # TODO: Figure out how to handle collections after scene copy, since their .seut.scene will still point to old one.

    for col in bpy.data.collections:
        if col is None:
            continue
        if not col.seut.scene is scene:
            continue
        if col.seut.type_index > 0:
            col.name = col.seut.col_type + str(col.seut.type_index) + " (" + col.seut.scene.seut.subtypeId + ")"
        else:
            col.name = col.seut.col_type + " (" + col.seut.scene.seut.subtypeId + ")"


def create_collections(context):
    """Recreates the collections SEUT requires"""

    scene = context.scene
    tag = ' (' + scene.seut.subtypeId + ')'
    collections = get_collections(scene)

    for key in collections.keys():
        if collections[key] == None and key != 'mountpoints' and key != 'mirroring' and key != 'render':

            collections[key] = bpy.data.collections.new(names[key] + tag)

            # TODO: If collection is LOD collection, set distance based on index

            if collections[key] is collections['seut']:
                scene.collection.children.link(collections[key])
            else:
                collections['seut'].children.link(collections[key])
        
        # TODO: Move collection to its scene if it's not there.

    return collections
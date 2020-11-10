import bpy
import re

from bpy.types import Operator

from .materials.seut_ot_create_material import create_material


names = {
    'seut': "SEUT",
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
    
        if not 'SEUT Node Group' in bpy.data.node_groups or bpy.data.node_groups['SEUT Node Group'].library != None:
            temp_mat = create_material()
            bpy.data.materials.remove(temp_mat)

        create_collections(context)

        return {'FINISHED'}


def get_collections(scene):
    """Scans existing collections to find the SEUT ones"""

    tag = ' (' + scene.seut.subtypeId + ')'

    # Use the keys of names to create a new dict
    collections = {}
    for key in names.keys():
        collections[key] = None

    children = scene.view_layers['SEUT'].layer_collection.children

    if str('SEUT' + tag) in children:
        collections['seut'] = children['SEUT' + tag].collection

    # Find collections in scene by keys and values in names
    if not collections['seut'] is None:
        for col in collections['seut'].children:
            for key in names.keys():
                if key == 'seut':
                    pass
                elif col.name == names[key] + tag:
                    collections[key] = col
    
    return collections


def rename_collections(scene):
    """Scans existing collections to find the SEUT ones and renames them if the tag has changed"""

    tag = ' (' + scene.seut.subtypeId + ')'
    tag_before = ' (' + scene.seut.subtypeBefore + ')'
    children = scene.view_layers['SEUT'].layer_collection.children

    for child in children:
        col = child.collection
        if col.name == 'SEUT' + tag_before or col.name[:4 + len(tag_before)] == 'SEUT' + tag_before and re.search("\.[0-9]{3}", col.name[-4:]) != None:
            seut_collection = col
            col.name = 'SEUT' + tag
    
    if seut_collection is None:
        return

    for col in seut_collection.children:
        for key in names.keys():
            
            col_name = col.name[:len(names[key] + " (")]

            if key == 'seut':
                pass
            elif col_name == names[key] + " (":
                col.name = names[key] + tag

    return


def create_collections(context):
    """Recreates the collections SEUT requires"""

    scene = context.scene
    tag = ' (' + scene.seut.subtypeId + ')'
    collections = get_collections(scene)

    for key in collections.keys():
        if collections[key] == None and key != 'mountpoints' and key != 'mirroring' and key != 'render':

            collections[key] = bpy.data.collections.new(names[key] + tag)

            if collections[key] is collections['seut']:
                scene.collection.children.link(collections[key])
            else:
                collections['seut'].children.link(collections[key])

    return collections
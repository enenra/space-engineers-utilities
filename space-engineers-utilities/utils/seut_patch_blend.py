import bpy
import re

from ..seut_collections     import names
from ..seut_collections     import colors
from ..seut_collections     import rename_collections

def apply_patches():

    # SEUT 0.9.95
    patch_view_layers()
    patch_collections()
    patch_highlight_empty_references()


def patch_view_layers():
    """Patches all SEUT scenes in BLEND file to have a named SEUT view layer."""

    for scn in bpy.data.scenes:

        tag = ' (' + scn.seut.subtypeId + ')'

        if 'SEUT' + tag in scn.view_layers[0].layer_collection.children:
            if not 'SEUT' in scn.view_layers:
                scn.view_layers[0].name = 'SEUT'


def patch_collections():
    """Patches all collections in the BLEND file to the new 0.9.95 system."""

    for scn in bpy.data.scenes:

        tag = ' (' + scn.seut.subtypeId + ')'

        # Ensure it only runs in SEUT scenes
        if not 'SEUT' in scn.view_layers:
            continue
        if not 'SEUT' + tag in scn.view_layers['SEUT'].layer_collection.children:
            continue
        # Ensure it doesn't run for scenes that have already been patched
        if not scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag].collection.seut.col_type == 'none':
            continue
        
        # Converting main collection
        seut_col = scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag].collection
        seut_col.seut.scene = scn
        seut_col.seut.col_type = 'seut'

        for col in seut_col.children:

            raw_type = re.match("^\w+", col.name).group(0)
            temp_type = re.match(".+?(?=[0-99])", raw_type)

            if temp_type is None:
                temp_type = str(raw_type.lower())
            else:
                temp_type = str(temp_type.group(0).lower())

            # Assigns HKT and BS_LOD collections to default collections
            if temp_type == 'collision':
                col.seut.col_type = 'hkt'
                # col.seut.ref_col = bpy.data.collections['Main' + tag]

            elif temp_type == 'bs_lod':
                col.seut.col_type = temp_type
                col.seut.type_index = 1
                col.seut.lod_distance = scn.seut.export_bs_lodDistance
            
            # Parses LOD distances to new format
            elif temp_type == 'lod':
                col.seut.col_type = temp_type
                
                if raw_type[len(temp_type):] == '1':
                    col.seut.lod_distance = scn.seut.export_lod1Distance
                elif raw_type[len(temp_type):] == '2':
                    col.seut.lod_distance = scn.seut.export_lod2Distance
                elif raw_type[len(temp_type):] == '3':
                    col.seut.lod_distance = scn.seut.export_lod3Distance

            else:
                col.seut.col_type = temp_type

            # Parses indexes of collections of the same type (LOD1, LOD2, etc.)
            if len(temp_type) != len(raw_type):
                col.seut.type_index = int(raw_type[len(temp_type):])
        
            col.seut.scene = scn
        
        # Recoloring collections
        for col in bpy.data.collections:
            if col is None:
                continue
            if not col.seut.scene is scn:
                continue

            if bpy.app.version >= (2, 91, 0):
                col.color_tag = colors[col.seut.col_type]

        
        rename_collections(scn)

    # This must happen after because the collection names might still be in flux beforehand
    for col in bpy.data.collections:
        if col is None:
            continue
        if col.seut.scene is None:
            continue

        tag = ' (' + col.seut.scene.seut.subtypeId + ')'
        if col.seut.col_type == 'hkt' and 'Main' + tag in bpy.data.collections:
            col.seut.ref_col = bpy.data.collections['Main' + tag]


def patch_highlight_empty_references():
    """Patches highlight empties to use the new CollectionProperty"""

    for obj in bpy.data.objects:
        if not obj is None and obj.type == 'EMPTY' and 'highlight' in obj:
            if not obj.seut.linkedObject is None and len(obj.seut.highlight_objects) < 1:
                ref = obj.seut.linkedObject
                obj.seut.linkedObject = None
                new = obj.seut.highlight_objects.add()
                new.obj = ref
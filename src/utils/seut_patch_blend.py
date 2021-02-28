import bpy
import re

from ..seut_collections     import names
from ..seut_collections     import colors
from ..seut_collections     import rename_collections

def apply_patches():

    patch_view_layers()
    patch_collections()


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
        if scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag].seut.col_type == 'seut':
            continue
        
        # Converting main collection
        seut_col = scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag]
        seut_col.seut.col_type = 'seut'
        seut_col.seut.scene = scn


        for col in seut_col.children:
            raw_type = re.match("([^ ]+) .*", col.name)
            temp_type = re.match("/[^[0-9]]*/", raw_type).lower()

            # Assigns HKT and BS_LOD collections to default collections
            if temp_type == 'collision':
                col.seut.col_type = 'hkt'
                col.seut.ref_col = bpy.data.collections['Main' + tag]

            elif temp_type == 'bs_lod':
                col.seut.col_type = 'bs_lod'
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
                col.seut.type_index = raw_type[len(temp_type):]
        
        # Recoloring collections
        for col in bpy.data.collections:
            if col is None:
                continue
            if not col.seut.scene is scn:
                continue

            col.color = colors[col.seut.col_type]

        
        rename_collections(scn)
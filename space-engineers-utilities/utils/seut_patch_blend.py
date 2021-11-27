import bpy
import re
import os

from ..seut_collections     import rename_collections, seut_collections, sort_collections
from ..seut_errors          import get_abs_path


def apply_patches():

    # SEUT 0.9.95
    patch_view_layers()
    patch_collections_v0995()
    patch_highlight_empty_references()

    # SEUT 0.9.96
    patch_mod_folder()
    patch_collections_v0996()
    patch_linked_objs()


def patch_view_layers():
    """Patches all SEUT scenes in BLEND file to have a named SEUT view layer."""

    for scn in bpy.data.scenes:
        if scn.seut.version >= 2:
            continue

        tag = ' (' + scn.seut.subtypeId + ')'

        if 'SEUT' + tag in scn.view_layers[0].layer_collection.children:
            if not 'SEUT' in scn.view_layers:
                scn.view_layers[0].name = 'SEUT'
                scn.seut.version = 1


def patch_collections_v0995():
    """Patches all collections in the BLEND file to the new 0.9.95 system."""

    for scn in bpy.data.scenes:
        if scn.seut.version >= 2:
            continue

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
            if col.seut.version >= 1:
                continue

            raw_type = re.match("^\w+", col.name).group(0)
            temp_type = re.match(".+?(?=[0-99])", raw_type)

            if temp_type is None:
                temp_type = str(raw_type.lower())
            else:
                temp_type = str(temp_type.group(0).lower())

            # Parses indexes of collections of the same type (LOD1, LOD2, etc.)
            if len(temp_type) != len(raw_type):
                col.seut.type_index = int(raw_type[len(temp_type):])

            # Assigns HKT and BS_LOD collections to default collections
            if temp_type == 'collision':
                col.seut.col_type = 'hkt'
                # col.seut.ref_col = bpy.data.collections['Main' + tag]

            elif temp_type == 'bs_lod':
                col.seut.col_type = 'none'
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
        
            col.seut.scene = scn
            col.seut.version = 1
        
        # Recoloring collections
        for col in bpy.data.collections:
            if col is None:
                continue
            if not col.seut.scene is scn:
                continue

            if bpy.app.version >= (2, 91, 0):
                col.color_tag = seut_collections[scn.seut.sceneType][col.seut.col_type]['color']

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
        if obj is None or obj.type != 'EMPTY' or not 'highlight' in obj:
            continue
        if obj.seut.version >= 1:
            continue

        if not obj.seut.linkedObject is None and len(obj.seut.highlight_objects) < 1:
            ref = obj.seut.linkedObject
            obj.seut.linkedObject = None
            new = obj.seut.highlight_objects.add()
            new.obj = ref
            obj.seut.version = 1


def patch_mod_folder():
    """Introduce mod folder with default being derived from mod folder"""

    if not bpy.data.is_saved:
        return

    for scn in bpy.data.scenes:
        if scn.seut.version >= 2:
            continue

        if scn.seut.export_exportPath == "":
            continue

        path = get_abs_path(scn.seut.export_exportPath)
        
        while os.path.basename(path) != "Models":
            if os.path.dirname(path) == path:
                break

            path = get_abs_path(os.path.dirname(path))
        
        if os.path.exists(os.path.dirname(path)):
            scn.seut.mod_path = os.path.dirname(path)
        scn.seut.version = 2


def patch_collections_v0996():
    """Patches collections for removal of BS_LOD-type and change for LOD to have ref_cols"""

    for scn in bpy.data.scenes:
        if not 'SEUT' in scn.view_layers:
            continue
        if scn.seut.version >= 3:
            continue

        assignments = {}
        for col in bpy.data.collections:
            if col.seut.version >= 3:
                continue
            if col.seut.scene != scn:
                continue

            if col.seut.col_type == 'mountpoints' and len(col.objects) <= 0:
                col.seut.col_type = 'lod'
                if f"BS1 ({scn.seut.subtypeId})" in bpy.data.collections:
                    assignments[col] = f"BS1 ({scn.seut.subtypeId})"
                col.seut.version = 3
            
            elif col.seut.col_type == 'lod' and col.seut.ref_col is None:
                if f"Main ({scn.seut.subtypeId})" in bpy.data.collections:
                    assignments[col] = f"Main ({scn.seut.subtypeId})"
                col.seut.version = 3
        
        for col, name in assignments.items():
            col.seut.ref_col = bpy.data.collections[name]

        rename_collections(scn)


def patch_linked_objs():
    """Patches all linked objects to the new .linked marker. (L) is only visual now."""

    for empty in bpy.data.objects:
        if empty.type != 'EMPTY' or not 'file' in empty:
            continue
        if empty.seut.version >= 2:
            continue

        empty.seut.version = 2
            
        for obj in empty.children:
            if '(L)' in obj.name and not obj.seut.linked:
                obj.seut.linked = True
                obj.seut.version = 2
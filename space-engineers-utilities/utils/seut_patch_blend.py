import bpy
import re
import os

from bpy.types              import Operator
from bpy.props              import StringProperty

from ..seut_collections     import *
from ..seut_errors          import get_abs_path


class SEUT_OT_PatchBLEND(Operator):
    """Patches the BLEND file's SEUT properties to the latest version"""
    bl_idname = "wm.patch_blend"
    bl_label = "Patch BLEND File"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        
        apply_patches()
        
        return {'FINISHED'}


def check_patch_needed() -> bool:
    
    for scn in bpy.data.scenes:
        if 'SEUT' in scn.view_layers and scn.seut.version < 4:
            return True
        if "SEUT" in scn.view_layers and ("Paint Color" not in scn.view_layers["SEUT"] or "UV Grid Overlay" not in scn.view_layers["SEUT"]):
            return True

    for col in bpy.data.collections:
        if col.seut.version < 3 and col.seut.col_type != 'none':
            return True

    return False


def apply_patches():

    # SEUT 0.9.95
    patch_view_layers()
    patch_collections_v0995()
    patch_highlight_empty_references()

    # SEUT 0.9.96
    patch_scenes()
    patch_collections_v0996()
    patch_linked_objs()

    # SEUT 1.1.0
    patch_paint_color()


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
        if scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag].collection is not None:
            seut_col = scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag].collection
            if seut_col.seut.col_type != 'none':
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
            if col.seut.col_type == 'none':
                continue
            
            if col.seut.col_type == 'seut':
                col.color_tag = 'COLOR_02'
            else:
                if col.seut.col_type not in seut_collections[scn.seut.sceneType]:
                    continue
                col.color_tag = seut_collections[scn.seut.sceneType][col.seut.col_type]['color']

    # This must happen after because the collection names might still be in flux beforehand
    for col in bpy.data.collections:
        if col is None:
            continue
        if col.seut.scene is None:
            continue

        tag = ' (' + col.seut.scene.seut.subtypeId + ')'
        if col.seut.col_type == 'hkt' and 'Main' + tag in bpy.data.collections:
            if len(get_rev_ref_cols(get_collections(col.seut.scene), bpy.data.collections['Main' + tag], 'hkt')) < 1:
                col.seut.ref_col = bpy.data.collections['Main' + tag]


def patch_highlight_empty_references():
    """Patches highlight empties to use the new CollectionProperty"""

    for obj in bpy.data.objects:
        if obj is None or obj.type != 'EMPTY' or not 'highlight' in obj:
            continue

        if not obj.seut.linkedObject is None and len(obj.seut.highlight_objects) < 1:
            ref = obj.seut.linkedObject
            obj.seut.linkedObject = None
            new = obj.seut.highlight_objects.add()
            new.obj = ref


def patch_scenes():
    """Introduce mod folder with default being derived from mod folder as well as transition to export_sbc_type"""

    if not bpy.data.is_saved:
        return

    for scn in bpy.data.scenes:
        if scn.seut.version >= 3:
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

        if not scn.seut.export_sbc:
            scn.seut.export_sbc_type = 'none'

        scn.seut.version = 3


def patch_collections_v0996():
    """Patches collections for removal of BS_LOD-type and change for LOD to have ref_cols"""

    for scn in bpy.data.scenes:
        if not 'SEUT' in scn.view_layers:
            continue

        assignments = {}
        for col in bpy.data.collections:
            if col.seut.version >= 3:
                continue
            if col.seut.scene != scn:
                continue

            if col.seut.col_type == 'mountpoints' and scn.seut.mountpointToggle == 'off' or col.seut.col_type == 'none' and 'BS_LOD' in col.name:
                col.seut.col_type = 'lod'
                if f"BS1 ({scn.seut.subtypeId})" in bpy.data.collections:
                    assignments[col] = [f"BS1 ({scn.seut.subtypeId})", col.seut.type_index]
                col.seut.version = 3
            
            elif col.seut.col_type == 'lod' and col.seut.ref_col is None:
                if f"Main ({scn.seut.subtypeId})" in bpy.data.collections:
                    assignments[col] = [f"Main ({scn.seut.subtypeId})", col.seut.type_index]
                col.seut.version = 3
                
            else:
                col.seut.version = 3
        
        for col, data in assignments.items():
            col.seut.ref_col = bpy.data.collections[data[0]]
            col.seut.type_index = data[1]

        rename_collections(scn)
        sort_collections(scn)
        scn.view_layers['SEUT'].update()
        scn.seut.version = 4


def patch_linked_objs():
    """Patches all linked objects to the new .linked marker. (L) is only visual now."""

    for empty in bpy.data.objects:
        if empty.type != 'EMPTY' or not 'file' in empty:
            continue
            
        for obj in empty.children:
            if '(L)' in obj.name and not obj.seut.linked:
                obj.seut.linked = True


def patch_paint_color():
    """Adds the paint_color custom property to all view_layers that miss it."""

    for scn in bpy.data.scenes:
        if not 'SEUT' in scn.view_layers:
            continue
        
        vl = scn.view_layers["SEUT"]
        vl["Paint Color"] = (0.0, 0.0, 0.0)
        prop_manager = vl.id_properties_ui("Paint Color")
        prop_manager.update(
            default= (0.0, 0.0, 0.0),
            min=0.0,
            max=1.0,
            subtype='COLOR'
        )

        vl['UV Grid Overlay'] = False
        prop_manager = vl.id_properties_ui("UV Grid Overlay")
        prop_manager.update(
            description="Whether to overlay the UV Grid over all materials"
        )
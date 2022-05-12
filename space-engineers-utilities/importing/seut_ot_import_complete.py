import bpy
import os
import re

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

from bpy.types                  import Operator

from .seut_ot_import        import import_fbx, remap_materials
from ..seut_collections     import *
from ..seut_errors          import seut_report


class SEUT_OT_ImportComplete(Operator):
    """Attempts to import not only the FBX but also all its associated LODs and Build Stages"""
    bl_idname = "scene.import_complete"
    bl_label = "Complete Import"
    bl_options = {'REGISTER', 'UNDO'}


    filter_glob: StringProperty(
        default='*.fbx',
        options={'HIDDEN'}
        )

    filepath: StringProperty(
        subtype="FILE_PATH"
        )


    @classmethod
    def poll(cls, context):
        return context.scene is not None


    def execute(self, context):
        scene = context.scene

        collections = get_collections(scene)

        filename = os.path.basename(self.filepath)
        directory = os.path.dirname(self.filepath)

        basename = get_basename(filename)
        scene.seut.subtypeId = basename
        tag = ' (' + scene.seut.subtypeId + ')'

        
        col_counter = 0
        failed_counter = 0

        for f in os.listdir(directory):
            if f is None:
                continue

            if os.path.isdir(f) or (os.path.splitext(f)[1] != ".fbx" and os.path.splitext(f)[1] != ".FBX"):
                continue
                
            if basename == os.path.splitext(f)[0] or f"{basename}Construction" in f or f"{basename}_Construction" in f or f"{basename}_BS" in f or f"{basename}_LOD" in f:
                pass
            else:
                continue

            fbx_type = determine_fbx_type(f)

            if fbx_type is None:
                continue

            col_type = fbx_type['col_type']
            type_index = fbx_type['type_index']
            ref_col_type = fbx_type['ref_col_type']
            ref_col_type_index = fbx_type['ref_col_type_index']
            
            if ref_col_type is not None:
                ref_col = get_seut_collection(scene, ref_col_type, ref_col_type=None, type_index=ref_col_type_index)
            else:
                ref_col = None

            if col_type in ['bs', 'lod']:
                cols = get_cols_by_type(scene, col_type, ref_col)
                if col_type in collections and type_index in cols:
                    col = cols[type_index]
                else:
                    col = create_seut_collection(scene, col_type, type_index, ref_col)

            elif col_type == 'main':
                if 'main' in collections:
                    col = collections['main'][0]
                else:
                    col = create_seut_collection(scene, 'main', None, None)
                        
            col_counter += 1
            context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children[col.name]
            result = import_fbx(self, context, os.path.join(directory, f))

            if not result == {'FINISHED'}:
                failed_counter += 1

            if fbx_type['col_type'] != 'main':
                scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children[col.name].hide_viewport = True
        
        remap_materials(self, context)

        sort_collections(scene, context)
        
        seut_report(self, context, 'INFO', True, 'I021', col_counter - failed_counter, col_counter)
        
        return {'FINISHED'}


    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


def get_basename(filename: str):

    filename = os.path.splitext(filename)[0]

    if "_Construction" in filename:
        filename = filename[:filename.find("_Construction")]
    elif "Construction" in filename:
        filename = filename[:filename.find("Construction")]
    elif "_BS" in filename:
        filename = filename[:filename.find("_BS")]
        
    if "_LOD" in filename:
        filename = filename[:filename.find("_LOD")]
    
    return filename


def determine_fbx_type(filename: str):
    """Returns the collection type and index (if applicable) that a file belongs into. Returns None if file should be skipped."""

    fbx_type = {
        'col_type': None, 
        'type_index': None,
        'ref_col_type': None,
        'ref_col_type_index': None
        }

    # LOD
    if "_LOD" in filename:
        fbx_type['col_type'] = 'lod'
        fbx_type['ref_col_type'] = 'main'
        fbx_type['type_index'] = int(re.search("(?<=_LOD)[0-9]{1,}", filename)[0])
    
    # BS / Construction
    if "Construction_" in filename:
        if fbx_type['col_type'] is not None:
            fbx_type['ref_col_type'] = 'bs'
            fbx_type['ref_col_type_index'] = int(re.search("(?<=Construction_)[0-9]{1,}", filename)[0])
        else:
            fbx_type['col_type'] = 'bs'
            fbx_type['type_index'] = int(re.search("(?<=Construction_)[0-9]{1,}", filename)[0])
    else:
        if "_Construction" in filename:
            if fbx_type['col_type'] is not None:
                fbx_type['ref_col_type'] = 'bs'
                fbx_type['ref_col_type_index'] = int(re.search("(?<=_Construction)[0-9]{1,}", filename)[0])
            else:
                fbx_type['col_type'] = 'bs'
                fbx_type['type_index'] = int(re.search("(?<=_Construction)[0-9]{1,}", filename)[0])

    if "_BS_LOD" in filename:
            fbx_type['ref_col_type'] = 'bs'
            fbx_type['ref_col_type_index'] = 1

    if "_BS" in filename:
        if fbx_type['col_type'] is not None:
            fbx_type['ref_col_type'] = 'bs'
            fbx_type['ref_col_type_index'] = int(re.search("(?<=_BS)[0-9]{1,}", filename)[0])
        elif fbx_type['ref_col_type'] is not None:
            fbx_type['col_type'] = 'bs'
            fbx_type['type_index'] = int(re.search("(?<=_BS)[0-9]{1,}", filename)[0])
    
    # Main
    if fbx_type['col_type'] is None:
        fbx_type['col_type'] = 'main'

    return fbx_type
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

from .seut_ot_import        import import_fbx
from ..seut_collections     import get_collections, create_seut_collection, names
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

        wm = context.window_manager
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

            if basename + "." not in f and basename + "Construction_" not in f and basename + "_" not in f:
                continue

            fbx_type = determine_fbx_type(f)

            if fbx_type is None:
                continue

            if fbx_type['col_type'] == 'bs' or fbx_type['col_type'] == 'lod' or fbx_type['col_type'] == 'bs_lod':
                if fbx_type['col_type'] in collections and fbx_type['type_index'] in collections[fbx_type['col_type']]:
                    col = collections[fbx_type['col_type']][fbx_type['type_index']]
                else:
                    col = create_seut_collection(context, fbx_type['col_type'], fbx_type['type_index'], None)

            elif fbx_type['col_type'] == 'main':
                if fbx_type['col_type'] in collections:
                    col = collections[fbx_type['col_type']]
                else:
                    col = create_seut_collection(context, fbx_type['col_type'], fbx_type['type_index'], None)
            
            col_counter += 1
            context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children[col.name]
            result = import_fbx(self, context, os.path.join(directory, f))

            if not result == {'FINISHED'}:
                failed_counter += 1

            if fbx_type['col_type'] != 'main':
                scene.view_layers['SEUT'].layer_collection.children['SEUT' + tag].children[col.name].hide_viewport = True
        
        seut_report(self, context, 'INFO', True, 'I021', col_counter - failed_counter, col_counter)
        
        return {'FINISHED'}


    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


def get_basename(filename: str):

    if filename.find("_") != -1:
        filename = filename[:filename.find("_")]
    
    if filename.find("Construction") != -1:
        filename = filename[:filename.find("Construction")]
    
    if filename.find(".fbx") != -1:
        filename = filename[:filename.find(".fbx")]
    elif filename.find(".FBX") != -1:
        filename = filename[:filename.find(".FBX")]
    
    return filename


def determine_fbx_type(filename: str):
    """Returns the collection type and index (if applicable) that a file belongs into. Returns None if file should be skipped."""

    fbx_type = {
        'col_type': None, 
        'type_index': None
        }
    
    if filename.find("_BS_LOD") != -1:
        fbx_type['col_type'] = 'bs_lod'

        if re.search("(?<=_BS_LOD)[0-9]{1,}", filename) != -1:
            fbx_type['type_index'] = int(re.search("(?<=_BS_LOD)[0-9]{1,}", filename)[0])
    
    elif filename.find("Construction_") != -1 and filename.find("_LOD") != -1:
        fbx_type['col_type'] = 'bs_lod'

        # More than one BS_LOD for a BS is currently not supported.
        if re.search("(?<=_LOD)[0-9]{1,}", filename)[0] != str(1):
            return None

        fbx_type['type_index'] = int(re.search("(?<=Construction_)[0-9]{1,}", filename)[0])

    elif filename.find("_LOD") != -1:
        fbx_type['col_type'] = 'lod'
        fbx_type['type_index'] = int(re.search("(?<=_LOD)[0-9]{1,}", filename)[0])

    elif filename.find("_BS") != -1:
        fbx_type['col_type'] = 'bs'
        fbx_type['type_index'] = int(re.search("(?<=_BS)[0-9]{1,}", filename)[0])

    elif filename.find("Construction_") != -1:
        fbx_type['col_type'] = 'bs'
        fbx_type['type_index'] = int(re.search("(?<=Construction_)[0-9]{1,}", filename)[0])

    elif filename.find(".hkt") != -1:
        fbx_type['col_type'] = 'hkt'

    else:
        fbx_type['col_type'] = 'main'

    return fbx_type
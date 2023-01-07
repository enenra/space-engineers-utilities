import bpy
import os
import addon_utils

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

from .seut_ot_import_materials              import import_materials
from ..empties.seut_empties                 import empty_types
from ..materials.seut_ot_remap_materials    import remap_materials
from ..seut_errors                          import seut_report
from ..seut_utils                           import get_seut_blend_data


class SEUT_OT_Import(Operator):
    """Import FBX files and remap materials"""
    bl_idname = "scene.import"
    bl_label = "Import FBX"
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

        result = import_fbx(self, context, self.filepath)
        remap_materials(self, context)

        return result


    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


def import_fbx(self, context, filepath):
    """Imports FBX and adjusts them for use in SEUT"""
    
    data = get_seut_blend_data()

    existing_objects = set(context.scene.objects)

    try:
        if addon_utils.check("better_fbx") == (True, True) and data.seut.better_fbx:
            result = bpy.ops.better_import.fbx(filepath=filepath)
        else:
            result = bpy.ops.import_scene.fbx(filepath=filepath)
    except RuntimeError as error:
        seut_report(self, context, 'ERROR', True, 'E036', str(error))
        return {'CANCELLED'}
        
    new_objects = set(context.scene.objects)
    imported_objects = new_objects.copy()
    
    for new in new_objects:
        for existing in existing_objects:
            if new == existing:
                imported_objects.remove(new)

    # Sanity check to catch import failure
    if imported_objects == None:
        seut_report(self, context, 'ERROR', True, 'E001')
        return {'CANCELLED'}

    for obj in imported_objects:
        
        if obj.type == 'EMPTY':
            
            # Changes empty display type to correct one
            obj.empty_display_type = 'CUBE'
            for key in empty_types.keys():
                if obj.name[:len(key)] == key:
                    obj.empty_display_type = empty_types[key]
                    break

            # Empties are imported at 2x the size they should be, this fixes that issue
            obj.scale.x *= 0.5
            obj.scale.y *= 0.5
            obj.scale.z *= 0.5

            if 'file' in obj and obj['file'] in bpy.data.scenes:
                obj.seut.linkedScene = bpy.data.scenes[obj['file']]

            if 'highlight' in obj:
                if obj['highlight'].find(";") == -1:
                    if obj['highlight'] in bpy.data.objects:
                        new = obj.seut.highlight_objects.add()
                        new.obj = bpy.data.objects[obj['highlight']]
                else:
                    split = obj['highlight'].split(";")
                    for entry in split:
                        if entry in bpy.data.objects:
                            new = obj.seut.highlight_objects.add()
                            new.obj = bpy.data.objects[entry]
    
    xml_path = os.path.splitext(filepath)[0] + '.xml'
    if os.path.exists(xml_path):
        import_materials(self, context, xml_path)

    seut_report(self, context, 'INFO', True, 'I014', filepath)

    return {'FINISHED'}
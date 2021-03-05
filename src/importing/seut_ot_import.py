import bpy

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

from ..empties.seut_empties                 import empty_types
from ..materials.seut_ot_remap_materials    import SEUT_OT_RemapMaterials
from ..seut_errors                          import seut_report


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
        """Imports FBX and adjusts them for use in SEUT"""

        wm = context.window_manager

        existing_objects = set(context.scene.objects)

        try:
            result = bpy.ops.import_scene.fbx(filepath=self.filepath)
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
                if 'MaxHandle' not in obj and 'file' not in obj:
                    obj.scale.x *= 0.5
                    obj.scale.y *= 0.5
                    obj.scale.z *= 0.5

                if 'file' in obj and obj['file'] in bpy.data.scenes:
                    obj.seut.linkedScene = bpy.data.scenes[obj['file']]
                if 'highlight' in obj and obj['highlight'] in bpy.data.objects:
                    obj.seut.linkedObject = bpy.data.objects[obj['highlight']]
        
        # Then run material remap
        bpy.ops.object.remapmaterials()

        if wm.seut.fix_scratched_materials:
            for obj in imported_objects:
                for slot in obj.material_slots:

                    if slot.material == bpy.data.materials['PaintedMetalScratched_Colorable']:
                        slot.material = bpy.data.materials['PaintedMetal_Colorable']

                    elif slot.material == bpy.data.materials['PaintedMetal_Yellow']:
                        slot.material = bpy.data.materials['PaintedMetalScratched_Yellow']

                    elif slot.material == bpy.data.materials['PaintedMetal_Darker']:
                        slot.material = bpy.data.materials['PaintedMetalScratched_Darker']

                    elif slot.material == bpy.data.materials['PaintedMetalScratched_VeryDark']:
                        slot.material = bpy.data.materials['PaintedMetal_VeryDark']

        seut_report(self, context, 'INFO', True, 'I014')

        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

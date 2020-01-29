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

from .materials.seut_ot_remapMaterials    import SEUT_OT_RemapMaterials

class SEUT_OT_Import(Operator):
    """Import FBX files and remap materials"""
    bl_idname = "scene.import"
    bl_label = "Import FBX"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(
        default='*.fbx',
        options={'HIDDEN'}
        )

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH"
        )

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):

        # The import FBX operator doesn't actually return the imported objects, so I need to compare the before and after.
        importObject = None

        existingObjects = set(context.scene.objects)

        result = bpy.ops.import_scene.fbx(filepath=self.filepath)

        newObjects = set(context.scene.objects)
        importedObjects = newObjects.copy()
        
        for obj1 in newObjects:
            for obj2 in existingObjects:
                if obj1 == obj2:
                    importedObjects.remove(obj1)

        # Sanity check to catch import failure
        if importedObjects == None:
            self.report({'ERROR'}, "SEUT: Import error. Imported object not found. (001)")
            return

        # Convert empties to display type 'cube'
        bpy.ops.object.emptytocubetype()

        # Sync highlight and subpart targets, if available
        for obj in importedObjects:
            if obj.type == 'EMPTY' and 'file' in obj and obj['file'] in bpy.data.scenes:
                obj.seut.linkedScene = bpy.data.scenes[obj['file']]
            if obj.type == 'EMPTY' and 'highlight' in obj and obj['highlight'] in bpy.data.objects:
                obj.seut.linkedObject = bpy.data.objects[obj['highlight']]
        
        # Then run material remap
        bpy.ops.object.remapmaterials()

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

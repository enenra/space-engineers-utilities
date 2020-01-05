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

from .seut_import_remapMaterials    import SEUT_OT_RemapMaterials

class SEUT_OT_Import(bpy.types.Operator):
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

        # First import FBX
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
            print("SEUT Error 001: Import error. Imported object not found.")
            return
        
        # Then run material remap
        SEUT_OT_RemapMaterials.remap_To_Library_Materials(context, importedObjects)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

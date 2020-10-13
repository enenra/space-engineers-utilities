import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_xml, export_model_FBX
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection, check_collection_excluded, check_toolpath, report_error

class SEUT_OT_ExportMain(Operator):
    """Exports the main model"""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['main'] is not None
        
    def execute(self, context):
        """Exports the 'Main' collection"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = SEUT_OT_ExportMain.export_Main(self, context, False)

        return result
    
    def export_Main(self, context, partial):
        """Exports the 'Main' collection"""

        scene = context.scene
        collections = get_collections(scene)
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        fbxImporterPath = os.path.abspath(bpy.path.abspath(preferences.fbxImporterPath))

        # Checks whether collection exists, is excluded or is empty
        result = check_collection(self, context, scene, collections['main'], False)
        if not result == {'CONTINUE'}:
            return result

        result = check_toolpath(self, context, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result
        
        foundArmatures = False
        for obj in collections['main'].objects:
            if obj is not None and obj.type == 'ARMATURE':
                foundArmatures = True
        
        if not foundArmatures and (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
            self.report({'WARNING'}, "SEUT: Scene is of type '%s' but does not contain any armatures." % (scene.seut.sceneType))
        if foundArmatures and not (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
            self.report({'WARNING'}, "SEUT: Scene is of type '%s' but contains armatures." % (scene.seut.sceneType))

        unparentedObjects = 0
        for obj in collections['main'].objects:
            if obj.parent is None:
                unparentedObjects += 1
        
        if unparentedObjects > 1:
            report_error(self, context, True, 'E031')
            return {'CANCELLED'}
        
        for obj in collections['main'].objects:
            if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                report_error(self, context, True, 'E032', obj.name)
                return {'CANCELLED'}


        print("\n------------------------------ Exporting Collection '" + collections['main'].name + "'.")
        export_xml(self, context, collections['main'])
        export_model_FBX(self, context, collections['main'])
        print("------------------------------ Finished exporting Collection '" + collections['main'].name + "'.\n")
        
        return {'FINISHED'}
import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_xml, export_fbx, export_collection
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection, check_collection_excluded, check_toolpath, seut_report, get_abs_path, check_uvms
from ..seut_utils                   import get_preferences


class SEUT_OT_ExportMain(Operator):
    """Exports the Main collection"""
    bl_idname = "object.export_main"
    bl_label = "Export Main Collection"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['main'] is not None
        

    def execute(self, context):
        """Calls the function to export the Main collection"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = export_main(self, context)

        return result
    
    
def export_main(self, context):
    """Exports the Main collection"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['main'], False)
    if not result == {'CONTINUE'}:
        return result

    # Check for availability of FBX Importer
    result = check_toolpath(self, context, preferences.fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
    if not result == {'CONTINUE'}:
        return result

    found_armatures = False
    unparented_objects = 0
    for obj in collections['main'].objects:

        if obj is not None and obj.type == 'ARMATURE':
            found_armatures = True
        
        if obj.parent is None:
            unparented_objects += 1
        
        # Check for missing UVMs (this might not be 100% reliable)
        if check_uvms(obj) != {'CONTINUE'}:
            return {'MISSING_UVMS'}  
    
    # Check for armatures being present in collection
    if not found_armatures and (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
        seut_report(self, context, 'WARNING', True, 'W008', scene.seut.sceneType)
    if found_armatures and not (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
        seut_report(self, context, 'WARNING', True, 'W009', scene.seut.sceneType)
    
    # Check for unparented objects
    if unparented_objects > 1:
        seut_report(self, context, 'ERROR', True, 'E031')
        return {'UNPARENTED_OBJECTS'}

    export_collection(self, context, collections['main'])
    
    return {'FINISHED'}
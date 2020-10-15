import bpy
import os
import shutil

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_options      import HAVOK_OPTION_FILE_CONTENT
from .havok.seut_havok_hkt          import process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm
from .seut_export_utils             import ExportSettings, export_to_fbxfile
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection, check_collection_excluded, check_toolpath, seut_report, get_abs_path, check_uvms


class SEUT_OT_ExportHKT(Operator):
    """Exports the Collision collection"""
    bl_idname = "object.export_hkt"
    bl_label = "Export Collision Collection"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['hkt'] is not None


    def execute(self, context):
        """Calls the function to export the Collision collection"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = export_hkt(self, context)

        return result
    

def export_hkt(self, context):
    """Exports collision to HKT"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()
    settings = ExportSettings(scene, None)
    path = get_abs_path(scene.seut.export_exportPath) + "\\"

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['hkt'], True)
    if not result == {'CONTINUE'}:
        return result

    # Check for availability of FBX Importer
    result = check_toolpath(self, context, preferences.fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
    if not result == {'CONTINUE'}:
        return result

    # Check for availability of Havok SFM
    result = check_toolpath(self, context, preferences.havokPath, "Havok Standalone Filter Manager", "hctStandAloneFilterManager.exe")
    if not result == {'CONTINUE'}:
        return result
    
    for obj in collections['hkt'].objects:

        # Check for missing UVMs (this might not be 100% reliable)
        if check_uvms(obj) != {'CONTINUE'}:
            return {'MISSING_UVMS'}

        # Check for unapplied modifiers
        if len(obj.modifiers) > 0:
            seut_report(self, context, 'ERROR', True, 'E034', obj.name)
            return {'UNAPPLIED_MODIFIERS'}
        
        # Apply Rigid Body
        context.view_layer.objects.active = obj
        # bpy.ops.object.transform_apply(location = True, scale = True, rotation = True) # This runs on all objects instead of just the active one for some reason. Breaks when there's instanced subparts.
        bpy.ops.rigidbody.object_add(type='ACTIVE')
    
    # Check if max amount of collision objects is exceeded
    if len(collections['hkt'].objects) > 16:
        seut_report(self, context, 'ERROR', True, 'E022', len(collections['hkt'].objects))
        return {'TOO_MANY_COLLISION_OBJECTS'}

    # FBX export via Custom FBX Importer
    fbx_hkt_file = join(path, scene.seut.subtypeId + ".hkt.fbx")
    hkt_file = join(path, scene.seut.subtypeId + ".hkt")
    
    export_to_fbxfile(settings, scene, fbx_hkt_file, collections['hkt'].objects, ishavokfbxfile=True)

    # Then create the HKT file.
    process_hktfbx_to_fbximporterhkt(context, settings, fbx_hkt_file, hkt_file)
    process_fbximporterhkt_to_final_hkt_for_mwm(self, context, scene, path, settings, hkt_file, hkt_file)
        
    return {'FINISHED'}
import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_xml, export_fbx, export_collection
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection_excluded, check_collection, check_toolpath, seut_report, check_uvms
from ..seut_utils                   import get_preferences


class SEUT_OT_ExportLOD(Operator):
    """Exports LOD collections"""
    bl_idname = "object.export_lod"
    bl_label = "Export LOD Collections"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['lod1'] is not None or collections['lod2'] is not None or collections['lod3'] is not None or collections['bs_lod'] is not None


    def execute(self, context):
        """Calls the function to export the LOD collections"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = export_lod(self, context)

        return result
    

def export_lod(self, context):
    """Exports LOD collections"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Check for availability of FBX Importer
    result = check_toolpath(self, context, preferences.fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
    if not result == {'CONTINUE'}:
        return result

    # Checks whether collections exists, are excluded or are empty
    lod1_valid = False
    result = check_collection(self, context, scene, collections['lod1'], True)
    if result == {'CONTINUE'}:
        lod1_valid = True

    lod2_valid = False
    result = check_collection(self, context, scene, collections['lod2'], True)
    if result == {'CONTINUE'}:
        lod2_valid = True

    lod3_valid = False
    result = check_collection(self, context, scene, collections['lod3'], True)
    if result == {'CONTINUE'}:
        lod3_valid = True

    bs_lod_valid = False
    result = check_collection(self, context, scene, collections['bs_lod'], True)
    if result == {'CONTINUE'}:
        bs_lod_valid = True

    if (not lod1_valid and lod2_valid) or (not lod2_valid and lod3_valid):
        seut_report(self, context, 'ERROR', True, 'E015', 'LOD')
        return {'INVALID_LOD_SETUP'}

    # Checks whether LOD distances are valid
    if scene.seut.export_lod1Distance > scene.seut.export_lod2Distance or scene.seut.export_lod2Distance > scene.seut.export_lod3Distance:
        seut_report(self, context, 'ERROR', True, 'E011')
        return {'INVALID_LOD_DISTANCES'}
    
    # Check for missing UVMs (this might not be 100% reliable)
    if lod1_valid:
        for obj in collections['lod1'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}

    if lod2_valid:
        for obj in collections['lod2'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}
    
    if lod3_valid:
        for obj in collections['lod3'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}
    
    if bs_lod_valid:
        for obj in collections['bs_lod'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}

    if lod1_valid:
        export_collection(self, context, collections['lod1'])  
    if lod2_valid:
        export_collection(self, context, collections['lod2'])
    if lod3_valid:
        export_collection(self, context, collections['lod3'])
    if bs_lod_valid:
        export_collection(self, context, collections['bs_lod'])
    
    return {'FINISHED'}
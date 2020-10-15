import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_xml, export_fbx, export_collection
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection_excluded, check_collection, check_toolpath, seut_report, check_uvms


class SEUT_OT_ExportBS(Operator):
    """Exports Build Stage collections"""
    bl_idname = "object.export_bs"
    bl_label = "Export Build Stage Collections"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None


    def execute(self, context):
        """Calls the function to export the Build Stage collections"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = export_bs(self, context)

        return result
    

def export_bs(self, context):
    """Exports Build Stage collections"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Check for availability of FBX Importer
    result = check_toolpath(self, context, preferences.fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
    if not result == {'CONTINUE'}:
        return result

    # Checks whether collections exists, are excluded or are empty
    colBS1Good = False
    result = check_collection(self, context, scene, collections['bs1'], True)
    if result == {'CONTINUE'}:
        colBS1Good = True

    colBS2Good = False
    result = check_collection(self, context, scene, collections['bs2'], True)
    if result == {'CONTINUE'}:
        colBS2Good = True

    colBS3Good = False
    result = check_collection(self, context, scene, collections['bs3'], True)
    if result == {'CONTINUE'}:
        colBS3Good = True

    if (not colBS1Good and colBS2Good) or (not colBS2Good and colBS3Good):
        seut_report(self, context, 'ERROR', True, 'E015', 'BS')
        return {'INVALID_BS_SETUP'}
    
    # Check for missing UVMs (this might not be 100% reliable)
    if colBS1Good:
        for obj in collections['bs1'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}
    
    if colBS2Good:
        for obj in collections['bs2'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}
    
    if colBS3Good:
        for obj in collections['bs3'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'MISSING_UVMS'}

    if colBS1Good:
        export_collection(self, context, collections['bs1'])
    if colBS2Good:
        export_collection(self, context, collections['bs2'])
    if colBS3Good:
        export_collection(self, context, collections['bs3'])
    
    return {'FINISHED'}
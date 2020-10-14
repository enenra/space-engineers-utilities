import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_xml, export_model_FBX
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection_excluded, check_collection, check_toolpath, seut_report

class SEUT_OT_ExportLOD(Operator):
    """Exports all LODs"""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['lod1'] is not None or collections['lod2'] is not None or collections['lod3'] is not None or collections['bs_lod'] is not None


    def execute(self, context):
        """Exports the 'LOD' collections"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = SEUT_OT_ExportLOD.export_LOD(self, context, False)

        return result
    
    def export_LOD(self, context, partial):
        """Exports the 'LOD' collections"""

        scene = context.scene
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        fbxImporterPath = os.path.abspath(bpy.path.abspath(preferences.fbxImporterPath))
        collections = get_collections(scene)

        result = check_toolpath(self, context, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        colLOD1Good = False
        result = check_collection(self, context, scene, collections['lod1'], partial)
        if result == {'CONTINUE'}:
            colLOD1Good = True

        colLOD2Good = False
        result = check_collection(self, context, scene, collections['lod2'], partial)
        if result == {'CONTINUE'}:
            colLOD2Good = True

        colLOD3Good = False
        result = check_collection(self, context, scene, collections['lod3'], partial)
        if result == {'CONTINUE'}:
            colLOD3Good = True

        colBSLODGood = False
        result = check_collection(self, context, scene, collections['bs_lod'], partial)
        if result == {'CONTINUE'}:
            colBSLODGood = True

        if (not colLOD1Good and colLOD2Good) or (not colLOD2Good and colLOD3Good):
            if partial:
                print("SEUT Warning: Invalid LOD setup. Cannot have LOD2 but no LOD1, or LOD3 but no LOD2.")
                return {'FINISHED'}
            else:
                seut_report(self, context, 'ERROR', True, 'E015', 'LOD')
                return {'CANCELLED'}

        if scene.seut.export_lod1Distance > scene.seut.export_lod2Distance or scene.seut.export_lod2Distance > scene.seut.export_lod3Distance:
            if partial:
                print("SEUT Warning: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2.")
                return {'FINISHED'}
            else:
                seut_report(self, context, 'ERROR', True, 'E011')
                return {'CANCELLED'}
        
        if colLOD1Good:
            for obj in collections['lod1'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}
        
        if colLOD2Good:
            for obj in collections['lod2'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}
        
        if colLOD3Good:
            for obj in collections['lod3'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}
        
        if colBSLODGood:
            for obj in collections['bs_lod'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}


        if colLOD1Good:
            print("\n------------------------------ Exporting Collection '" + collections['lod1'].name + "'.")
            export_xml(self, context, collections['lod1'])
            export_model_FBX(self, context, collections['lod1'])
            print("------------------------------ Finished exporting Collection '" + collections['lod1'].name + "'.")
        
        if colLOD2Good:
            print("\n------------------------------ Exporting Collection '" + collections['lod2'].name + "'.")
            export_xml(self, context, collections['lod2'])
            export_model_FBX(self, context, collections['lod2'])
            print("------------------------------ Finished exporting Collection '" + collections['lod2'].name + "'.")

        if colLOD3Good:
            print("\n------------------------------ Exporting Collection '" + collections['lod3'].name + "'.")
            export_xml(self, context, collections['lod3'])
            export_model_FBX(self, context, collections['lod3'])
            print("------------------------------ Finished exporting Collection '" + collections['lod3'].name + "'.")

        if colBSLODGood:
            print("\n------------------------------ Exporting Collection '" + collections['bs_lod'].name + "'.")
            export_xml(self, context, collections['bs_lod'])
            export_model_FBX(self, context, collections['bs_lod'])
            print("------------------------------ Finished exporting Collection '" + collections['bs_lod'].name + "'.")
        
        return {'FINISHED'}
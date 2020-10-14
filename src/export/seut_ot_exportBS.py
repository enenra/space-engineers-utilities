import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_xml, export_fbx
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection_excluded, check_collection, check_toolpath, seut_report

class SEUT_OT_ExportBS(Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_buildstages"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = SEUT_OT_ExportBS.export_BS(self, context, False)

        return result
    
    def export_BS(self, context, partial):
        """Exports the 'Build Stages' collections"""

        scene = context.scene
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        fbxImporterPath = os.path.abspath(bpy.path.abspath(preferences.fbxImporterPath))
        collections = get_collections(scene)

        result = check_toolpath(self, context, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        colBS1Good = False
        result = check_collection(self, context, scene, collections['bs1'], partial)
        if result == {'CONTINUE'}:
            colBS1Good = True

        colBS2Good = False
        result = check_collection(self, context, scene, collections['bs2'], partial)
        if result == {'CONTINUE'}:
            colBS2Good = True

        colBS3Good = False
        result = check_collection(self, context, scene, collections['bs3'], partial)
        if result == {'CONTINUE'}:
            colBS3Good = True

        if (not colBS1Good and colBS2Good) or (not colBS2Good and colBS3Good):
            if partial:
                print("SEUT Warning: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2.")
                return {'FINISHED'}
            else:
                seut_report(self, context, 'ERROR', True, 'E015', 'BS')
                return {'CANCELLED'}
        
        if colBS1Good:
            for obj in collections['bs1'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}
        
        if colBS2Good:
            for obj in collections['bs2'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}
        
        if colBS3Good:
            for obj in collections['bs3'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    seut_report(self, context, 'ERROR', True, 'E032', obj.name)
                    return {'CANCELLED'}


        if colBS1Good:
            print("\n------------------------------ Exporting Collection '" + collections['bs1'].name + "'.")
            export_xml(self, context, collections['bs1'])
            export_fbx(self, context, collections['bs1'])
            print("------------------------------ Finished exporting Collection '" + collections['bs1'].name + "'.\n")
        
        if colBS2Good:
            print("\n------------------------------ Exporting Collection '" + collections['bs2'].name + "'.")
            export_xml(self, context, collections['bs2'])
            export_fbx(self, context, collections['bs2'])
            print("------------------------------ Finished exporting Collection '" + collections['bs2'].name + "'.\n")

        if colBS3Good:
            print("\n------------------------------ Exporting Collection '" + collections['bs3'].name + "'.")
            export_xml(self, context, collections['bs3'])
            export_fbx(self, context, collections['bs3'])
            print("------------------------------ Finished exporting Collection '" + collections['bs3'].name + "'.\n")
        
        return {'FINISHED'}
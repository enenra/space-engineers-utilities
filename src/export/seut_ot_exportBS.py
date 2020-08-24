import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_XML, export_model_FBX
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral, isCollectionExcluded, errorCollection, errorToolPath

class SEUT_OT_ExportBS(Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_buildstages"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.getCollections(context.scene)
        return collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = SEUT_OT_ExportBS.export_BS(self, context, False)

        return result
    
    def export_BS(self, context, partial):
        """Exports the 'Build Stages' collections"""

        scene = context.scene
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        fbxImporterPath = os.path.normpath(bpy.path.abspath(preferences.fbxImporterPath))
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        result = errorToolPath(self, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        colBS1Good = False
        result = errorCollection(self, scene, collections['bs1'], partial)
        if result == {'CONTINUE'}:
            colBS1Good = True

        colBS2Good = False
        result = errorCollection(self, scene, collections['bs2'], partial)
        if result == {'CONTINUE'}:
            colBS2Good = True

        colBS3Good = False
        result = errorCollection(self, scene, collections['bs3'], partial)
        if result == {'CONTINUE'}:
            colBS3Good = True

        if (not colBS1Good and colBS2Good) or (not colBS2Good and colBS3Good):
            if partial:
                print("SEUT Warning: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2.")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                print("SEUT Error: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                return {'CANCELLED'}
        
        if colBS1Good:
            for obj in collections['bs1'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                    print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers. (032)")
                    return {'CANCELLED'}
        
        if colBS2Good:
            for obj in collections['bs2'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                    print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers. (032)")
                    return {'CANCELLED'}
        
        if colBS3Good:
            for obj in collections['bs3'].objects:
                if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                    self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                    print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers. (032)")
                    return {'CANCELLED'}


        if colBS1Good:
            print("\n------------------------------ Exporting Collection '" + collections['bs1'].name + "'.")
            export_XML(self, context, collections['bs1'])
            export_model_FBX(self, context, collections['bs1'])
            print("------------------------------ Finished exporting Collection '" + collections['bs1'].name + "'.\n")
        
        if colBS2Good:
            print("\n------------------------------ Exporting Collection '" + collections['bs2'].name + "'.")
            export_XML(self, context, collections['bs2'])
            export_model_FBX(self, context, collections['bs2'])
            print("------------------------------ Finished exporting Collection '" + collections['bs2'].name + "'.\n")

        if colBS3Good:
            print("\n------------------------------ Exporting Collection '" + collections['bs3'].name + "'.")
            export_XML(self, context, collections['bs3'])
            export_model_FBX(self, context, collections['bs3'])
            print("------------------------------ Finished exporting Collection '" + collections['bs3'].name + "'.\n")
        
        return {'FINISHED'}
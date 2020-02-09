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
        collections = SEUT_OT_RecreateCollections.get_Collections(context.scene)
        return collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_buildstages'")

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == {'CONTINUE'}:
            return result

        result = SEUT_OT_ExportBS.export_BS(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_buildstages'")

        return result
    
    def export_BS(self, context, partial):
        """Exports the 'Build Stages' collections"""

        scene = context.scene
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        fbxImporterPath = os.path.normpath(bpy.path.abspath(preferences.fbxImporterPath))
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)

        result = errorToolPath(self, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        colBS1Good = False
        result = errorCollection(self, context, collections['bs1'], partial)
        if result == {'CONTINUE'}:
            colBS1Good = True

        colBS2Good = False
        result = errorCollection(self, context, collections['bs2'], partial)
        if result == {'CONTINUE'}:
            colBS2Good = True

        colBS3Good = False
        result = errorCollection(self, context, collections['bs3'], partial)
        if result == {'CONTINUE'}:
            colBS3Good = True

        if (not colBS1Good and colBS2Good) or (not colBS2Good and colBS3Good):
            if partial:
                print("SEUT Warning: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                print("SEUT Error: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                return {'CANCELLED'}

        # Export BS1, if present.
        if colBS1Good:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS1'.")
                export_XML(self, context, collections['bs1'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS1'.")
                export_model_FBX(self, context, collections['bs1'])
        
        # Export BS2, if present.
        if colBS2Good:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS2'.")
                export_XML(self, context, collections['bs2'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS2'.")
                export_model_FBX(self, context, collections['bs2'])

        # Export BS3, if present.
        if colBS3Good:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS3'.")
                export_XML(self, context, collections['bs3'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS3'.")
                export_model_FBX(self, context, collections['bs3'])
        
        return {'FINISHED'}
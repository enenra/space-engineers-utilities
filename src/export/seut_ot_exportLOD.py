import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import export_XML, export_model_FBX
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral, isCollectionExcluded, errorCollection, errorToolPath

class SEUT_OT_ExportLOD(Operator):
    """Exports all LODs"""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.getCollections(context.scene)
        return collections['lod1'] is not None or collections['lod2'] is not None or collections['lod3'] is not None or collections['bs_lod'] is not None


    def execute(self, context):
        """Exports the 'LOD' collections"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_lod'")

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = SEUT_OT_ExportLOD.export_LOD(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_lod'")

        return result
    
    def export_LOD(self, context, partial):
        """Exports the 'LOD' collections"""

        scene = context.scene
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        fbxImporterPath = os.path.normpath(bpy.path.abspath(preferences.fbxImporterPath))
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        result = errorToolPath(self, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        colLOD1Good = False
        result = errorCollection(self, context, collections['lod1'], partial)
        if result == {'CONTINUE'}:
            colLOD1Good = True

        colLOD2Good = False
        result = errorCollection(self, context, collections['lod2'], partial)
        if result == {'CONTINUE'}:
            colLOD2Good = True

        colLOD3Good = False
        result = errorCollection(self, context, collections['lod3'], partial)
        if result == {'CONTINUE'}:
            colLOD3Good = True

        colBSLODGood = False
        result = errorCollection(self, context, collections['bs_lod'], partial)
        if result == {'CONTINUE'}:
            colBSLODGood = True

        if (not colLOD1Good and colLOD2Good) or (not colLOD2Good and colLOD3Good):
            if partial:
                print("SEUT Warning: Invalid LOD setup. Cannot have LOD2 but no LOD1, or LOD3 but no LOD2. (015)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Invalid LOD setup. Cannot have LOD2 but no LOD1, or LOD3 but no LOD2. (015)")
                print("SEUT Error: Invalid LOD setup. Cannot have LOD2 but no LOD1, or LOD3 but no LOD2. (015)")
                return {'CANCELLED'}

        if scene.seut.export_lod1Distance > scene.seut.export_lod2Distance or scene.seut.export_lod2Distance > scene.seut.export_lod3Distance:
            if partial:
                print("SEUT Warning: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                print("SEUT Error: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                return {'CANCELLED'}
        
        for obj in collections['lod1'].objects:
            if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers.")
                return {'CANCELLED'}
        
        for obj in collections['lod2'].objects:
            if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers.")
                return {'CANCELLED'}
        
        for obj in collections['lod3'].objects:
            if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers.")
                return {'CANCELLED'}
        
        for obj in collections['bs_lod'].objects:
            if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                self.report({'ERROR'}, "SEUT: Object '%s' does not have any valid UV-Maps. This will crash Space Engineers. (032)" % (obj.name))
                print("SEUT Error: Object '" + obj.name + "' does not have any valid UV-Maps. This will crash Space Engineers.")
                return {'CANCELLED'}

        # Export LOD1, if present.
        if colLOD1Good:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD1'.")
                export_XML(self, context, collections['lod1'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD1'.")
                export_model_FBX(self, context, collections['lod1'])
        
        # Export LOD2, if present.
        if colLOD2Good:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD2'.")
                export_XML(self, context, collections['lod2'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD2'.")
                export_model_FBX(self, context, collections['lod2'])

        # Export LOD3, if present.
        if colLOD3Good:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD3'.")
                export_XML(self, context, collections['lod3'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD3'.")
                export_model_FBX(self, context, collections['lod3'])

        # Export BS_LOD, if present.
        if colBSLODGood:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS_LOD'.")
                export_XML(self, context, collections['bs_lod'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS_LOD'.")
                export_model_FBX(self, context, collections['bs_lod'])
        
        return {'FINISHED'}
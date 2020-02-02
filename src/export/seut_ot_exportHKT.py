import bpy
import os
import shutil

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_options      import HAVOK_OPTION_FILE_CONTENT
from .havok.seut_havok_hkt          import process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm
from .seut_export_utils             import ExportSettings, export_to_fbxfile
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral, errorCollection, isCollectionExcluded, errorToolPath


class SEUT_OT_ExportHKT(Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.get_Collections(context.scene)
        return collections['hkt'] is not None


    def execute(self, context):
        """Exports collision to HKT"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_hkt'")

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == 'CONTINUE':
            return {result}
        
        SEUT_OT_ExportHKT.export_HKT(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_hkt'")

        return {'FINISHED'}
    
    def export_HKT(self, context, partial):
        """Exports collision to HKT"""

        scene = context.scene
        depsgraph = None
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        settings = ExportSettings(scene, depsgraph)
        exportPath = os.path.normpath(bpy.path.abspath(scene.seut.export_exportPath))
        fbxImporterPath = os.path.normpath(bpy.path.abspath(preferences.fbxImporterPath))
        havokPath = os.path.normpath(bpy.path.abspath(preferences.havokPath))

        # Checks whether collection exists, is excluded or is empty
        result = errorCollection(self, context, collections['hkt'], partial)
        if not result == 'CONTINUE':
            return {result}

        result = errorToolPath(self, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        result = errorToolPath(self, havokPath, "Havok Standalone Filter Manager", "hctStandAloneFilterManager.exe")
        if not result == {'CONTINUE'}:
            return result

        for obj in collections['hkt'].objects:
            context.view_layer.objects.active = obj
            bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
            bpy.ops.rigidbody.object_add(type='ACTIVE')

        path = bpy.path.abspath(scene.seut.export_exportPath)

        # Re-scale collision objects via rescale factor before export.
        for obj in collections['hkt'].objects:
            obj.scale *= context.scene.seut.export_rescaleFactor

        # FBX export via Custom FBX Importer
        fbxhktfile = join(path, scene.seut.subtypeId + ".hkt.fbx")
        hktfile = join(path, scene.seut.subtypeId + ".hkt")
        
        export_to_fbxfile(settings, scene, fbxhktfile, collections['hkt'].objects, ishavokfbxfile=True)

        # Then create the HKT file.
        process_hktfbx_to_fbximporterhkt(settings, fbxhktfile, hktfile)
        process_fbximporterhkt_to_final_hkt_for_mwm(self, scene, path, settings, hktfile, hktfile)

        # Re-scale collision objects via rescale factor after export.
        for obj in collections['hkt'].objects:
            obj.scale /= context.scene.seut.export_rescaleFactor
           
        return
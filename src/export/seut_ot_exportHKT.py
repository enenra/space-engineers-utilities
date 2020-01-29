import bpy
import os
import shutil

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_options      import HAVOK_OPTION_FILE_CONTENT
from .havok.seut_havok_hkt          import process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm
from .seut_export_utils             import ExportSettings, export_to_fbxfile
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral, errorCollection, isCollectionExcluded


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

        if preferences.fbxImporterPath == "" or os.path.exists(fbxImporterPath) == False:
            if partial:
                print("SEUT Warning: Path to Custom FBX Importer '" + fbxImporterPath + "' not valid. (012)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Path to Custom FBX Importer '%s' not valid. (012)" % (fbxImporterPath))
                print("SEUT Error: Path to Custom FBX Importer '" + fbxImporterPath + "' not valid. (012)")
                return {'CANCELLED'}

        if preferences.havokPath == "" or os.path.exists(havokPath) == False:
            if partial:
                print("SEUT Error: Path to Havok Standalone Filter Tool '" + havokPath + "' not valid. (013)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Path to Havok Standalone Filter Tool '%s' not valid. (013)" % (havokPath))
                print("SEUT Error: Path to Havok Standalone Filter Tool '" + havokPath + "' not valid. (013)")
                return {'CANCELLED'}

        # Checks whether collection exists, is excluded or is empty
        result = errorCollection(self, context, collections['hkt'], partial)
        if not result == 'CONTINUE':
            return {result}

        for obj in collections['hkt'].objects:
            context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_add(type='ACTIVE')

        if preferences.looseFilesExportFolder == '0':
            path = os.path.dirname(bpy.data.filepath) + "\\"
        elif preferences.looseFilesExportFolder == '1':
            path = bpy.path.abspath(scene.seut.export_exportPath)

        # FBX export via Custom FBX Importer
        fbxhktfile = join(path, scene.seut.subtypeId + ".hkt.fbx")
        hktfile = join(path, scene.seut.subtypeId + ".hkt")
        
        export_to_fbxfile(settings, scene, fbxhktfile, collections['hkt'].objects, ishavokfbxfile=True)

        # Then create the HKT file.
        process_hktfbx_to_fbximporterhkt(settings, fbxhktfile, hktfile)
        process_fbximporterhkt_to_final_hkt_for_mwm(self, scene, path, settings, hktfile, hktfile)
           
        return
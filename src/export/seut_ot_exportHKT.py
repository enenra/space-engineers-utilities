import bpy
import os
import shutil

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_options      import HAVOK_OPTION_FILE_CONTENT
from .havok.seut_havok_hkt          import process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm
from .seut_export_utils             import ExportSettings, export_to_fbxfile
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral, errorCollection, isCollectionExcluded, errorToolPath, report_error


class SEUT_OT_ExportHKT(Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.getCollections(context.scene)
        return collections['hkt'] is not None


    def execute(self, context):
        """Exports collision to HKT"""

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = SEUT_OT_ExportHKT.export_HKT(self, context, False)

        return result
    
    def export_HKT(self, context, partial):
        """Exports collision to HKT"""

        scene = context.scene
        depsgraph = None
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        settings = ExportSettings(scene, depsgraph)
        exportPath = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath))
        fbxImporterPath = os.path.abspath(bpy.path.abspath(preferences.fbxImporterPath))
        havokPath = os.path.abspath(bpy.path.abspath(preferences.havokPath))

        # Checks whether collection exists, is excluded or is empty
        result = errorCollection(self, context, scene, collections['hkt'], partial)
        if not result == {'CONTINUE'}:
            return result

        result = errorToolPath(self, fbxImporterPath, "Custom FBX Importer", "FBXImporter.exe")
        if not result == {'CONTINUE'}:
            return result

        result = errorToolPath(self, havokPath, "Havok Standalone Filter Manager", "hctStandAloneFilterManager.exe")
        if not result == {'CONTINUE'}:
            return result
        
        for obj in collections['hkt'].objects:
            if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
                report_error(self, context, True, 'E032', obj.name)
                return {'CANCELLED'}
            if len(obj.modifiers) > 0:
                report_error(self, context, True, 'E034', obj.name)
                return {'CANCELLED'}
        
        if len(collections['hkt'].objects) > 16:
            report_error(self, context, True, 'E022', len(collections['hkt'].objects))
            return {'CANCELLED'}


        for obj in collections['hkt'].objects:
            context.view_layer.objects.active = obj
            # bpy.ops.object.transform_apply(location = True, scale = True, rotation = True) # This runs on all objects instead of just the active one for some reason. Breaks when there's instanced subparts.
            bpy.ops.rigidbody.object_add(type='ACTIVE')

        path = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath)) + "\\"

        # FBX export via Custom FBX Importer
        fbxhktfile = join(path, scene.seut.subtypeId + ".hkt.fbx")
        hktfile = join(path, scene.seut.subtypeId + ".hkt")
        
        export_to_fbxfile(settings, scene, fbxhktfile, collections['hkt'].objects, ishavokfbxfile=True)

        # Then create the HKT file.
        process_hktfbx_to_fbximporterhkt(context, settings, fbxhktfile, hktfile)
        process_fbximporterhkt_to_final_hkt_for_mwm(self, context, scene, path, settings, hktfile, hktfile)
           
        return {'FINISHED'}
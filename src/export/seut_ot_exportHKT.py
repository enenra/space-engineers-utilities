import bpy
import os

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_options      import HAVOK_OPTION_FILE_CONTENT
from .havok.seut_havok_hkt          import export_hktfbx_for_fbximporter, process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from .seut_export_utils             import ExportSettings, isCollectionExcluded

class SEUT_OT_ExportHKT(Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.get_Collections()
        return collections['hkt'] is not None


    def execute(self, context):
        """Exports collision to HKT"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_hkt'")

        scene = context.scene
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        exportPath = os.path.normpath(bpy.path.abspath(scene.seut.export_exportPath))

        if preferences.looseFilesExportFolder == '1' and scene.seut.export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            print("SEUT Error: No export folder defined. (003)")
        elif preferences.looseFilesExportFolder == '1' and os.path.exists(exportPath) == False:
            self.report({'ERROR'}, "SEUT: Export path '%s' doesn't exist. (003)" % (exportPath))
            print("SEUT Error: Export path '" + exportPath + "' doesn't exist. (003)")
            return {'CANCELLED'}

        if preferences.looseFilesExportFolder == '1' and scene.seut.export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export path '%s' does not contain 'Models\\'. Cannot be transformed into relative path. (014)" % (exportPath))
            print("SEUT Error: Export path '" + exportPath + "' does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.seut.subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            print("SEUT Error: No SubtypeId set. (004)")
            return {'CANCELLED'}
        
        SEUT_OT_ExportHKT.export_HKT(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_hkt'")

        return {'FINISHED'}
    
    def export_HKT(self, context, partial):
        """Exports collision to HKT"""

        scene = context.scene
        depsgraph = None
        collections = SEUT_OT_RecreateCollections.get_Collections()
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        settings = ExportSettings(scene, depsgraph)
        exportPath = os.path.normpath(bpy.path.abspath(scene.seut.export_exportPath))
        fbxImporterPath = os.path.normpath(bpy.path.abspath(preferences.fbxImporterPath))
        havokPath = os.path.normpath(bpy.path.abspath(preferences.havokPath))

        if preferences.fbxImporterPath == "" or os.path.exists(fbxImporterPath) == False:
            if partial:
                self.report({'WARNING'}, "SEUT: Path to Custom FBX Importer '%s' not valid. (012)" % (fbxImporterPath))
                print("SEUT Warning: Path to Custom FBX Importer '" + fbxImporterPath + "' not valid. (012)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Path to Custom FBX Importer '%s' not valid. (012)" % (fbxImporterPath))
                print("SEUT Error: Path to Custom FBX Importer '" + fbxImporterPath + "' not valid. (012)")
                return {'CANCELLED'}

        if preferences.havokPath == "" or os.path.exists(havokPath) == False:
            if partial:
                self.report({'ERROR'}, "SEUT: Path to Havok Standalone Filter Tool '%s' not valid. (013)" % (havokPath))
                print("SEUT Error: Path to Havok Standalone Filter Tool '" + havokPath + "' not valid. (013)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Path to Havok Standalone Filter Tool '%s' not valid. (013)" % (havokPath))
                print("SEUT Error: Path to Havok Standalone Filter Tool '" + havokPath + "' not valid. (013)")
                return {'CANCELLED'}

        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children
        isExcluded = isCollectionExcluded("Collision", allCurrentViewLayerCollections)

        if isExcluded is True:
            if partial:
                self.report({'WARNING'}, "SEUT: Collection 'Collision' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                print("SEUT Warning: Collection 'Collision' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Collection 'Collision' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                print("SEUT Error: Collection 'Collision' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                return {'CANCELLED'}

        if collections['hkt'] == None:
            if partial:
                self.report({'WARNING'}, "SEUT: Collection 'Collision' not found. Export not possible. (002)")
                print("SEUT Warning: Collection 'Collision' not found. Export not possible. (002)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Collection 'Collision' not found. Export not possible. (002)")
                print("SEUT Error: Collection 'Collision' not found. Export not possible. (002)")
                return {'CANCELLED'}

        if len(collections['hkt'].objects) == 0:
            if partial:
                self.report({'WARNING'}, "SEUT: Collection 'Collision' is empty. Export not possible. (005)")
                print("SEUT Warning: Collection 'Collision' is empty. Export not possible. (005)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Collection 'Collision' is empty. Export not possible. (005)")
                print("SEUT Error: Collection 'Collision' is empty. Export not possible. (005)")
                return {'CANCELLED'}

        for obj in collections['hkt'].objects:
            context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_add(type='ACTIVE')

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            print("SEUT Error: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return {'CANCELLED'}
        else:
            if preferences.looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.seut.export_exportPath)

        # FBX export via Custom FBX Importer
        fbxhktfile = join(path, scene.seut.subtypeId + ".hkt.fbx")
        hktfile = join(path, scene.seut.subtypeId + ".hkt")
        
        export_hktfbx_for_fbximporter(settings, fbxhktfile, collections['hkt'].objects)

        # Then create the HKT file.
        process_hktfbx_to_fbximporterhkt(settings, fbxhktfile, hktfile)
        process_fbximporterhkt_to_final_hkt_for_mwm(self, scene, path, settings, hktfile, hktfile)

        return
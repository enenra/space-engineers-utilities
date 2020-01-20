import bpy
import os

from bpy.types                       import Operator
from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_ot_export                 import SEUT_OT_Export

class SEUT_OT_ExportMain(Operator):
    """Exports the main model"""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        """Exports the 'Main' collection"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        collections = SEUT_OT_RecreateCollections.get_Collections()
        exportPath = os.path.normpath(bpy.path.abspath(scene.prop_export_exportPath))

        # self.report({'INFO'}, "SEUT: Running operator: 'object.export_main'")

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (Export: 003)")
            print("SEUT: No export folder defined. (Export: 003)")
        elif preferences.pref_looseFilesExportFolder == '1' and os.path.exists(exportPath) == False:
            self.report({'ERROR'}, "SEUT: Export folder "+exportPath+" doesn't exist. (Export: 003)")
            print("SEUT: Export folder "+exportPath+" doesn't exist. (Export: 003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            exportPath = scene.prop_export_exportPath
            self.report({'ERROR'}, "SEUT: Export folder"+exportPath+" does not contain 'Models\\'. Cannot be transformed into relative path. (ExportMain: 014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children
        isCollectionExcluded = SEUT_OT_Export.isCollectionExcluded("Main", allCurrentViewLayerCollections)

        if isCollectionExcluded is True:
            self.report({'ERROR'}, "SEUT: Collection 'Main' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
            return {'CANCELLED'}

        if collections['main'] == None:
            self.report({'ERROR'}, "SEUT: Collection 'Main' not found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['main'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Main' is empty. Export not possible. (005)")
            return {'CANCELLED'}

        # Export XML if boolean is set.
        if scene.prop_export_xml:
            self.report({'INFO'}, "SEUT: Exporting XML for 'Main'.")
            SEUT_OT_Export.export_XML(self, context, collections['main'])

        # Export FBX if boolean is set.
        if scene.prop_export_fbx:
            self.report({'INFO'}, "SEUT: Exporting FBX for 'Main'.")
            SEUT_OT_Export.export_FBX(self, context, collections['main'])

        return {'FINISHED'}
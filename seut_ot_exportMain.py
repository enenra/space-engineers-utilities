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

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_main'")

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        collections = SEUT_OT_RecreateCollections.get_Collections()
        exportPath = os.path.normpath(bpy.path.abspath(scene.prop_export_exportPath))

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            print("SEUT Error: No export folder defined. (003)")
        elif preferences.pref_looseFilesExportFolder == '1' and os.path.exists(exportPath) == False:
            self.report({'ERROR'}, "SEUT: Export path '%s' doesn't exist. (003)" % (exportPath))
            print("SEUT Error: Export path '" + exportPath + "' doesn't exist. (003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export path '%s' does not contain 'Models\\'. Cannot be transformed into relative path. (014)" % (exportPath))
            print("SEUT Error: Export path '" + exportPath + "' does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            print("SEUT Error: No SubtypeId set. (004)")
            return {'CANCELLED'}

        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children
        isCollectionExcluded = SEUT_OT_Export.isCollectionExcluded("Main", allCurrentViewLayerCollections)

        if isCollectionExcluded is True:
            self.report({'ERROR'}, "SEUT: Collection 'Main' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
            print("SEUT Error: Collection 'Main' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
            return {'CANCELLED'}

        if collections['main'] == None:
            self.report({'ERROR'}, "SEUT: Collection 'Main' not found. Export not possible. (002)")
            print("SEUT Error: Collection 'Main' not found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['main'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Main' is empty. Export not possible. (005)")
            print("SEUT Error: Collection 'Main' is empty. Export not possible. (005)")
            return {'CANCELLED'}

        # Export XML if boolean is set.
        if scene.prop_export_xml:
            self.report({'INFO'}, "SEUT: Exporting XML for 'Main'.")
            SEUT_OT_Export.export_XML(self, context, collections['main'])
        else:
            print("SEUT Info: 'XML' export disabled.")

        # Export FBX if boolean is set.
        if scene.prop_export_fbx:
            self.report({'INFO'}, "SEUT: Exporting FBX for 'Main'.")
            SEUT_OT_Export.export_FBX(self, context, collections['main']) #STOLLIE: This exports the Main Model using Blenders in-built method.
        else:
            print("SEUT Info: 'FBX' export disabled.")

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_main'")

        return {'FINISHED'}
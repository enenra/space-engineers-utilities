import bpy

from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_ot_export                 import SEUT_OT_Export

class SEUT_OT_ExportMain(bpy.types.Operator):
    """Exports the main model"""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'Main' collection"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get("space-engineers-utilities").preferences

        collections = SEUT_OT_RecreateCollections.get_Collections()

        # If no export folder is set, error out.
        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            print("SEUT Error 003: No export folder defined.")
            return {'CANCELLED'}

        # If no SubtypeId is set, error out.
        if scene.prop_subtypeId == "":
            print("SEUT Error 004: No SubtypeId set.")
            return {'CANCELLED'}

        # If main collection isn't found, error out.
        if collections['main'] == None:
            print("SEUT Error 002: Collection 'Main' not found. Export not possible.")
            return {'CANCELLED'}

        # If main collection is empty, error out.
        if len(collections['main'].objects) == 0:
            print("SEUT Error 005: Collection 'Main' is empty. Export not possible.")
            return {'CANCELLED'}

        # Export XML if boolean is set.
        if scene.prop_export_xml:
            print("SEUT Info: Exporting XML for 'Main'.")
            SEUT_OT_Export.export_XML(context, collections['main'])

        # Export FBX if boolean is set.
        if scene.prop_export_fbx:
            print("SEUT Info: Exporting FBX for 'Main'.")
            SEUT_OT_Export.export_FBX(context, collections['main'])


        return {'FINISHED'}
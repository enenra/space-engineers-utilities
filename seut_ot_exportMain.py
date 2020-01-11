import bpy

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

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            return {'CANCELLED'}

        if scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
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
            SEUT_OT_Export.export_XML(context, collections['main'])

        # Export FBX if boolean is set.
        if scene.prop_export_fbx:
            self.report({'INFO'}, "SEUT: Exporting FBX for 'Main'.")
            SEUT_OT_Export.export_FBX(context, collections['main'])


        return {'FINISHED'}
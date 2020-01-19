import bpy
import os

from bpy.types                       import Operator
from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_ot_export                 import SEUT_OT_Export

class SEUT_OT_ExportBS(Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_buildstages"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        collections = SEUT_OT_RecreateCollections.get_Collections()

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "" or os.path.exists(scene.prop_export_exportPath) == False:
            self.report({'ERROR'}, "SEUT: No export folder defined or export folder doesn't exist. (ExportBS: 003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        if collections['bs1'] == None and collections['bs2'] == None and collections['bs3'] == None:
            self.report({'ERROR'}, "SEUT: No 'BS'-type collections found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) == 0:
            self.report({'ERROR'}, "SEUT: All 'BS'-type collections are empty. Export not possible. (005)")
            return {'CANCELLED'}

        if (len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) != 0) or (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
            self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
            return {'CANCELLED'}

        # Export BS1, if present.
        if collections['bs1'] == None or len(collections['bs1'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'BS1' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS1'.")
                SEUT_OT_Export.export_XML(self, context, collections['bs1'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS1'.")
                SEUT_OT_Export.export_FBX(self, context, collections['bs1'])
        
        # Export BS2, if present.
        if collections['bs2'] == None or len(collections['bs2'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'BS2' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS2'.")
                SEUT_OT_Export.export_XML(self, context, collections['bs2'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS2'.")
                SEUT_OT_Export.export_FBX(self, context, collections['bs2'])

        # Export BS3, if present.
        if collections['bs3'] == None or len(collections['bs3'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'BS3' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS3'.")
                SEUT_OT_Export.export_XML(self, context, collections['bs3'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS3'.")
                SEUT_OT_Export.export_FBX(self, context, collections['bs3'])


        return {'FINISHED'}
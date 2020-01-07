import bpy

from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_ot_export                 import SEUT_OT_Export

class SEUT_OT_ExportBS(bpy.types.Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_bs"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

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

        # If no collections are found, error out.
        if collections['bs1'] == None and collections['bs2'] == None and collections['bs3'] == None:
            print("SEUT Error 003: No 'BS'-type collections found. Export not possible.")
            return {'CANCELLED'}

        # If all collections are empty, error out.
        if len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) == 0:
            print("SEUT Error 005: All 'BS'-type collections are empty. Export not possible.")
            return {'CANCELLED'}

        # Export BS1, if present.
        if collections['bs1'] == None or len(collections['bs1'].objects) == 0:
            print("SEUT Error 002: Collection 'BS1' not found or empty. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'BS1'.")
                SEUT_OT_Export.export_XML(context, collections['bs1'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'BS1'.")
                SEUT_OT_Export.export_FBX(context, collections['bs1'])
        
        # Export BS2, if present.
        if collections['bs2'] == None or len(collections['bs2'].objects) == 0:
            print("SEUT Error 002: Collection 'BS2' not found or empty. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'BS2'.")
                SEUT_OT_Export.export_XML(context, collections['bs2'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'BS2'.")
                SEUT_OT_Export.export_FBX(context, collections['bs2'])

        # Export BS3, if present.
        if collections['bs3'] == None or len(collections['bs3'].objects) == 0:
            print("SEUT Error 002: Collection 'BS3' not found or empty. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'BS3'.")
                SEUT_OT_Export.export_XML(context, collections['bs3'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'BS3'.")
                SEUT_OT_Export.export_FBX(context, collections['bs3'])


        return {'FINISHED'}
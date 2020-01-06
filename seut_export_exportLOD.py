import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_export                 import SEUT_OT_Export

class SEUT_OT_ExportLOD(bpy.types.Operator):
    """Exports all LODs"""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'LOD' collections"""

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
        if collections['lod1'] == None and collections['lod2'] == None and collections['lod3'] == None:
            print("SEUT Error 003: No 'LOD'-type collections found. Export not possible.")
            return {'CANCELLED'}

        # If all collections are empty, error out.
        if len(collections['lod1'].objects) == 0 and len(collections['lod2'].objects) == 0 and len(collections['lod3'].objects) == 0:
            print("SEUT Error 005: All 'LOD'-type collections are empty. Export not possible.")
            return {'CANCELLED'}

        # Export LOD1, if present.
        if collections['lod1'] == None or len(collections['lod1'].objects) == 0:
            print("SEUT Error 002: Collection 'LOD1' not found or empty. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'LOD1'.")
                SEUT_OT_Export.export_XML(context, collections['lod1'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'LOD1'.")
                SEUT_OT_Export.export_FBX(context, collections['lod1'])
        
        # Export LOD2, if present.
        if collections['lod2'] == None or len(collections['lod2'].objects) == 0:
            print("SEUT Error 002: Collection 'LOD2' not found or empty. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'LOD2'.")
                SEUT_OT_Export.export_XML(context, collections['lod2'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'LOD2'.")
                SEUT_OT_Export.export_FBX(context, collections['lod2'])

        # Export LOD3, if present.
        if collections['lod3'] == None or len(collections['lod3'].objects) == 0:
            print("SEUT Error 002: Collection 'LOD3' not found or empty. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'LOD3'.")
                SEUT_OT_Export.export_XML(context, collections['lod3'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'LOD3'.")
                SEUT_OT_Export.export_FBX(context, collections['lod3'])


        return {'FINISHED'}
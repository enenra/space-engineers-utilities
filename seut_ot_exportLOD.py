import bpy

from bpy.types                       import Operator
from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_ot_export                 import SEUT_OT_Export

class SEUT_OT_ExportLOD(Operator):
    """Exports all LODs"""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'LOD' collections"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        collections = SEUT_OT_RecreateCollections.get_Collections()

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        if collections['lod1'] == None and collections['lod2'] == None and collections['lod3'] == None:
            self.report({'ERROR'}, "SEUT: No 'LOD'-type collections found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['lod1'].objects) == 0 and len(collections['lod2'].objects) == 0 and len(collections['lod3'].objects) == 0:
            self.report({'ERROR'}, "SEUT: All 'LOD'-type collections are empty. Export not possible. (005)")
            return {'CANCELLED'}

        if scene.prop_export_lod1Distance > prop_export_lod2Distance or prop_export_lod2Distance > prop_export_lod3Distance:
            self.report({'ERROR'}, "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
            return {'CANCELLED'}

        # Export LOD1, if present.
        if collections['lod1'] == None or len(collections['lod1'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'LOD1' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD1'.")
                SEUT_OT_Export.export_XML(self, context, collections['lod1'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD1'.")
                SEUT_OT_Export.export_FBX(self, context, collections['lod1'])
        
        # Export LOD2, if present.
        if collections['lod2'] == None or len(collections['lod2'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'LOD2' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD2'.")
                SEUT_OT_Export.export_XML(self, context, collections['lod2'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD2'.")
                SEUT_OT_Export.export_FBX(self, context, collections['lod2'])

        # Export LOD3, if present.
        if collections['lod3'] == None or len(collections['lod3'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'LOD3' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD3'.")
                SEUT_OT_Export.export_XML(self, context, collections['lod3'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD3'.")
                SEUT_OT_Export.export_FBX(self, context, collections['lod3'])


        return {'FINISHED'}
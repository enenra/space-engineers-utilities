import bpy
import os

from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_utils                    import isCollectionExcluded, export_XML, export_FBX

class SEUT_OT_ExportLOD(Operator):
    """Exports all LODs"""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.get_Collections()
        return collections['lod1'] is not None or collections['lod2'] is not None or collections['lod3'] is not None


    def execute(self, context):
        """Exports the 'LOD' collections"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_lod'")

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
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
        
        SEUT_OT_ExportLOD.export_LOD(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_lod'")

        return {'FINISHED'}
    
    def export_LOD(self, context, partial):
        """Exports the 'LOD' collections"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        collections = SEUT_OT_RecreateCollections.get_Collections()

        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children
        isExcludedLOD1 = isCollectionExcluded("LOD1", allCurrentViewLayerCollections)
        isExcludedLOD2 = isCollectionExcluded("LOD2", allCurrentViewLayerCollections)
        isExcludedLOD3 = isCollectionExcluded("LOD3", allCurrentViewLayerCollections)

        if isExcludedLOD1 and isExcludedLOD2 and isExcludedLOD3:
            if partial:
                self.report({'WARNING'}, "SEUT: All 'LOD'-type collections excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                print("SEUT Warning: All 'LOD'-type collections excluded from view layer. Re-enable in hierarchy. (019)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: All 'LOD'-type collections excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                print("SEUT Error: All 'LOD'-type collections excluded from view layer. Re-enable in hierarchy. (019)")
                return {'CANCELLED'}

        if collections['lod1'] == None and collections['lod2'] == None and collections['lod3'] == None:
            if partial:
                self.report({'WARNING'}, "SEUT: No 'LOD'-type collections found. Export not possible. (002)")
                print("SEUT Warning: No 'LOD'-type collections found. Export not possible. (002)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: No 'LOD'-type collections found. Export not possible. (002)")
                print("SEUT Error: No 'LOD'-type collections found. Export not possible. (002)")
                return {'CANCELLED'}

        if len(collections['lod1'].objects) == 0 and len(collections['lod2'].objects) == 0 and len(collections['lod3'].objects) == 0:
            if partial:
                self.report({'WARNING'}, "SEUT: All 'LOD'-type collections are empty. Export not possible. (005)")
                print("SEUT Warning: All 'LOD'-type collections are empty. Export not possible. (005)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: All 'LOD'-type collections are empty. Export not possible. (005)")
                print("SEUT Error: All 'LOD'-type collections are empty. Export not possible. (005)")
                return {'CANCELLED'}

        if scene.prop_export_lod1Distance > scene.prop_export_lod2Distance or scene.prop_export_lod2Distance > scene.prop_export_lod3Distance:
            if partial:
                self.report({'WARNING'}, "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                print("SEUT Warning: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                print("SEUT Error: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)")
                return {'CANCELLED'}

        # Export LOD1, if present.
        if collections['lod1'] == None or len(collections['lod1'].objects) == 0 or isExcludedLOD1:
            self.report({'WARNING'}, "SEUT: Collection 'LOD1' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD1'.")
                export_XML(self, context, collections['lod1'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD1'.")
                export_FBX(self, context, collections['lod1'])
        
        # Export LOD2, if present.
        if collections['lod2'] == None or len(collections['lod2'].objects) == 0 or isExcludedLOD2:
            self.report({'WARNING'}, "SEUT: Collection 'LOD2' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD2'.")
                export_XML(self, context, collections['lod2'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD2'.")
                export_FBX(self, context, collections['lod2'])

        # Export LOD3, if present.
        if collections['lod3'] == None or len(collections['lod3'].objects) == 0 or isExcludedLOD3:
            self.report({'WARNING'}, "SEUT: Collection 'LOD3' not found or empty. Export not possible. (002)")
        else:
            if scene.prop_export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'LOD3'.")
                export_XML(self, context, collections['lod3'])
            if scene.prop_export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'LOD3'.")
                export_FBX(self, context, collections['lod3'])
        
        return
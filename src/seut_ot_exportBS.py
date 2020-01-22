import bpy
import os

from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_utils                    import isCollectionExcluded, export_XML, export_FBX

class SEUT_OT_ExportBS(Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_buildstages"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.get_Collections()
        return collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_buildstages'")

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
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

        SEUT_OT_ExportBS.export_BS(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_buildstages'")

        return {'FINISHED'}
    
    def export_BS(self, context, partial):
        """Exports the 'Build Stages' collections"""

        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        collections = SEUT_OT_RecreateCollections.get_Collections()

        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children
        isExcludedBS1 = isCollectionExcluded("BS1", allCurrentViewLayerCollections)
        isExcludedBS2 = isCollectionExcluded("BS2", allCurrentViewLayerCollections)
        isExcludedBS3 = isCollectionExcluded("BS3", allCurrentViewLayerCollections)

        if isExcludedBS1 and isExcludedBS2 and isExcludedBS3:
            if partial:
                self.report({'WARNING'}, "SEUT: All 'BS'-type collections excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                print("SEUT Warning: All 'BS'-type collections excluded from view layer. Re-enable in hierarchy. (019)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: All 'BS'-type collections excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
                print("SEUT Error: All 'BS'-type collections excluded from view layer. Re-enable in hierarchy. (019)")
                return {'CANCELLED'}

        if collections['bs1'] == None and collections['bs2'] == None and collections['bs3'] == None:
            if partial:
                self.report({'WARNING'}, "SEUT: No 'BS'-type collections found. Export not possible. (002)")
                print("SEUT Warning: No 'BS'-type collections found. Export not possible. (002)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: No 'BS'-type collections found. Export not possible. (002)")
                print("SEUT Error: No 'BS'-type collections found. Export not possible. (002)")
                return {'CANCELLED'}

        if len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) == 0:
            if partial:
                self.report({'WARNING'}, "SEUT: All 'BS'-type collections are empty. Export not possible. (005)")
                print("SEUT Warning: All 'BS'-type collections are empty. Export not possible. (005)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: All 'BS'-type collections are empty. Export not possible. (005)")
                print("SEUT Error: All 'BS'-type collections are empty. Export not possible. (005)")
                return {'CANCELLED'}

        if (len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) != 0) or (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
            if partial:
                self.report({'WARNING'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                print("SEUT Warning: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                print("SEUT Error: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
                return {'CANCELLED'}

        # Export BS1, if present.
        if collections['bs1'] == None or len(collections['bs1'].objects) == 0 or isExcludedBS1:
            self.report({'WARNING'}, "SEUT: Collection 'BS1' not found or empty. Export not possible.")
        else:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS1'.")
                export_XML(self, context, collections['bs1'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS1'.")
                export_FBX(self, context, collections['bs1'])
        
        # Export BS2, if present.
        if collections['bs2'] == None or len(collections['bs2'].objects) == 0 or isExcludedBS2:
            self.report({'WARNING'}, "SEUT: Collection 'BS2' not found or empty. Export not possible.")
        else:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS2'.")
                export_XML(self, context, collections['bs2'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS2'.")
                export_FBX(self, context, collections['bs2'])

        # Export BS3, if present.
        if collections['bs3'] == None or len(collections['bs3'].objects) == 0 or isExcludedBS3:
            self.report({'WARNING'}, "SEUT: Collection 'BS3' not found or empty. Export not possible.")
        else:
            if scene.seut.export_xml:
                self.report({'INFO'}, "SEUT: Exporting XML for 'BS3'.")
                export_XML(self, context, collections['bs3'])
            if scene.seut.export_fbx:
                self.report({'INFO'}, "SEUT: Exporting FBX for 'BS3'.")
                export_FBX(self, context, collections['bs3'])
        
        return
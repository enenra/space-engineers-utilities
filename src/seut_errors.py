import bpy
import os

from .export.seut_export_utils  import isCollectionExcluded

def errorExportGeneral(self, context):
    """Basic check for export path and SubtypeId existing"""

    scene = context.scene
    if __package__.find(".") == -1:
        addon = __package__
    else:
        addon = __package__[:__package__.find(".")]
    preferences = bpy.context.preferences.addons.get(addon).preferences
    exportPath = os.path.normpath(bpy.path.abspath(scene.seut.export_exportPath))

    if preferences.looseFilesExportFolder == '1' and scene.seut.export_exportPath == "":
        self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
        print("SEUT Error: No export folder defined. (003)")
        return 'CANCELLED'
    elif preferences.looseFilesExportFolder == '1' and os.path.exists(exportPath) == False:
        self.report({'ERROR'}, "SEUT: Export path '%s' doesn't exist. (003)" % (exportPath))
        print("SEUT Error: Export path '" + exportPath + "' doesn't exist. (003)")
        return 'CANCELLED'

    if preferences.looseFilesExportFolder == '1' and scene.seut.export_exportPath.find("Models\\") == -1:
        self.report({'ERROR'}, "SEUT: Export path '%s' does not contain 'Models\\'. Cannot be transformed into relative path. (014)" % (exportPath))
        print("SEUT Error: Export path '" + exportPath + "' does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
        return 'CANCELLED'

    if scene.seut.subtypeId == "":
        self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
        print("SEUT Error: No SubtypeId set. (004)")
        return 'CANCELLED'

    return 'CONTINUE'

def errorCollection(self, context, collection, partial):
    """Check if collection exists, is not excluded and is not empty"""

    allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children
    isExcluded = isCollectionExcluded(collection.name, allCurrentViewLayerCollections)

    if collection == None:
        if partial:
            self.report({'WARNING'}, "SEUT: Collection '%s' not found. Export not possible. (002)" % (collection.name))
            print("SEUT Warning: Collection '" + collection.name + "' not found. Export not possible. (002)")
            return 'FINISHED'
        else:
            self.report({'ERROR'}, "SEUT: Collection '%s' not found. Export not possible. (002)" % (collection.name))
            print("SEUT Error: Collection '" + collection.name + "' not found. Export not possible. (002)")
            return 'CANCELLED'

    if isExcluded is True:
        if partial:
            self.report({'WARNING'}, "SEUT: Collection '%s' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)" % (collection.name))
            print("SEUT Warning: Collection '" + collection.name + "' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
            return 'FINISHED'
        else:
            self.report({'ERROR'}, "SEUT: Collection '%s' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)" % (collection.name))
            print("SEUT Error: Collection '" + collection.name + "' excluded from view layer. Export not possible. Re-enable in hierarchy. (019)")
            return 'CANCELLED'

    if len(collection.objects) == 0:
        if partial:
            self.report({'WARNING'}, "SEUT: Collection '%s' is empty. Export not possible. (005)" % (collection.name))
            print("SEUT Warning: Collection '" + collection.name + "' is empty. Export not possible. (005)")
            return 'FINISHED'
        else:
            self.report({'ERROR'}, "SEUT: Collection '%s' is empty. Export not possible. (005)" % (collection.name))
            print("SEUT Error: Collection '" + collection.name + "' is empty. Export not possible. (005)")
            return 'CANCELLED'
    
    return 'CONTINUE'
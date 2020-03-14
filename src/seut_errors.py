import bpy
import os


def errorExportGeneral(self, context):
    """Basic check for export path and SubtypeId existing"""

    scene = context.scene
    if __package__.find(".") == -1:
        addon = __package__
    else:
        addon = __package__[:__package__.find(".")]
    preferences = bpy.context.preferences.addons.get(addon).preferences
    exportPath = os.path.normpath(bpy.path.abspath(scene.seut.export_exportPath))

    # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
    if not bpy.data.is_saved:
        self.report({'ERROR'}, "SEUT: BLEND file must be saved before export. (008)")
        print("SEUT Error: BLEND file must be saved before export. (008)")
        return {'CANCELLED'}

    if os.path.exists(exportPath) == False:
        self.report({'ERROR'}, "SEUT: Export path '%s' doesn't exist. (003)" % (exportPath))
        print("SEUT Error: Export path '" + exportPath + "' doesn't exist. (003)")
        return {'CANCELLED'}
    elif scene.seut.export_exportPath == "":
        self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
        print("SEUT Error: No export folder defined. (003)")
        return {'CANCELLED'}

    if scene.seut.export_exportPath.find("Models\\") == -1:
        self.report({'ERROR'}, "SEUT: Export path '%s' does not contain 'Models\\'. Cannot be transformed into relative path. (014)" % (exportPath))
        print("SEUT Error: Export path '" + exportPath + "' does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
        return {'CANCELLED'}

    if scene.seut.subtypeId == "":
        self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
        print("SEUT Error: No SubtypeId set. (004)")
        return {'CANCELLED'}

    return {'CONTINUE'}

def errorCollection(self, scene, collection, partial):
    """Check if collection exists, is not excluded and is not empty"""

    allCurrentViewLayerCollections = scene.view_layers[0].layer_collection.children

    if collection is None:
        if partial:
            print("SEUT Warning: Collection not found. Action not possible.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "SEUT: Collection not found. Action not possible. (002)")
            print("SEUT Error: Collection not found. Action not possible. (002)")
            return {'CANCELLED'}
            
    isExcluded = isCollectionExcluded(collection.name, allCurrentViewLayerCollections)

    if isExcluded or isExcluded is None:
        if partial:
            print("SEUT Warning: Collection '" + collection.name + "' excluded from view layer or cannot be found. Action not possible.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "SEUT: Collection '%s' excluded from view layer or cannot be found. Action not possible. (019)" % (collection.name))
            print("SEUT Error: Collection '" + collection.name + "' excluded from view layer or cannot be found. Action not possible. (019)")
            return {'CANCELLED'}

    if len(collection.objects) == 0:
        if partial:
            print("SEUT Warning: Collection '" + collection.name + "' is empty. Action not possible.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "SEUT: Collection '%s' is empty. Action not possible. (005)" % (collection.name))
            print("SEUT Error: Collection '" + collection.name + "' is empty. Action not possible. (005)")
            return {'CANCELLED'}
    
    return {'CONTINUE'}

def errorToolPath(self, toolPath, toolName, toolFileName):
    """Checks if external tool is correctly linked"""

    if toolPath == "" or toolPath == "." or os.path.exists(toolPath) is False:
        self.report({'ERROR'}, "SEUT: Path to %s '%s' not valid. (012)" % (toolName, toolPath))
        print("SEUT Error: Path to " + toolName + " '" + toolPath + "' not valid. (012)")
        return {'CANCELLED'}

    fileName = os.path.basename(toolPath)
    if toolFileName != fileName:
        self.report({'ERROR'}, "SEUT: Path to %s not valid - wrong target file: Expected '%s' but is set to '%s'. (013)" % (toolName, toolFileName, fileName))
        print("SEUT Error: Path to " + toolName + " not valid - wrong target file: Expected '" + toolFileName + "' but is set to '" + fileName + "'. (013)")
        return {'CANCELLED'}
    
    return {'CONTINUE'}


def isCollectionExcluded(collectionName, allCurrentViewLayerCollections):
    for topLevelCollection in allCurrentViewLayerCollections:
        if topLevelCollection.name == collectionName:
            if topLevelCollection.exclude:
                return True
            else:
                return False
        if collectionName in topLevelCollection.children.keys():
            for collection in topLevelCollection.children:
                if collection.name == collectionName:
                    if collection.exclude:
                        return True
                    else:
                        return False
                        

def draw_error(self, context):
    wm = context.window_manager

    self.layout.label(text=wm.seut.errorText, icon='ERROR')


def showError(context, title, text):

    wm = context.window_manager
    wm.seut.errorText = text

    context.window_manager.popup_menu(draw_error, title=title)
    print(text)

    wm.seut.errorText = ""

    return
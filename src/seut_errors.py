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
    exportPath = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath))

    # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
    if not bpy.data.is_saved:
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT Error: BLEND file must be saved before export. (008)")
        return {'CANCELLED'}

    if os.path.exists(exportPath) == False:
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Export path '%s' doesn't exist. (003)" % exportPath)
        return {'CANCELLED'}
    elif scene.seut.export_exportPath == "":
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT Error: No export folder defined. (003)")
        return {'CANCELLED'}

    if scene.seut.export_exportPath.find("Models\\") == -1:
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Export path '%s' does not contain 'Models\\'. Cannot be transformed into relative path. (014)" % exportPath)
        return {'CANCELLED'}

    if scene.seut.subtypeId == "":
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: No SubtypeId set. (004)")
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
            showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Collection not found. Action not possible. (002)")
            return {'CANCELLED'}
            
    isExcluded = isCollectionExcluded(collection.name, allCurrentViewLayerCollections)

    if isExcluded or isExcluded is None:
        if partial:
            print("SEUT Warning: Collection '%s' excluded from view layer or cannot be found. Action not possible." % collection.name)
            return {'FINISHED'}
        else:
            showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Collection '%s' excluded from view layer or cannot be found. Action not possible. (019)" % collection.name)
            return {'CANCELLED'}

    if len(collection.objects) == 0:
        if partial:
            print("SEUT Warning: Collection '%s' is empty. Action not possible." % collection.name)
            return {'FINISHED'}
        else:
            showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Collection '%s' is empty. Action not possible. (005)" % collection.name)
            return {'CANCELLED'}
    
    return {'CONTINUE'}

def errorToolPath(self, toolPath, toolName, toolFileName):
    """Checks if external tool is correctly linked"""

    if toolPath == "" or toolPath == "." or os.path.exists(toolPath) is False:
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Path to %s '%s' not valid. (012)" % (toolName, toolPath))
        return {'CANCELLED'}

    fileName = os.path.basename(toolPath)
    if toolFileName != fileName:
        showErrorNew(self, context=context, err_type='ERROR', err_message="SEUT: Path to %s not valid - wrong target file: Expected '%s' but is set to '%s'. (013)" % (toolName, toolFileName, fileName))
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

def showErrorNew(self, context, err_type: str, err_message: str, show_link=True):
    def draw(self, context):
        # self.layout.label(text=self.p_text)
        # self.layout.label()
        self.layout.label()
        self.layout.label( )
        self.layout.operator('wm.get_update', icon='IMPORT', text='Open GitHub page')

    self.report({err_type}, err_message)
    print(err_message)
    if show_link: bpy.context.window_manager.popup_menu(draw, title=err_message, icon='NONE')

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
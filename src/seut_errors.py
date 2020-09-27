import bpy
import os
import collections

errors = {
    'E001': "SEUT: Import error. Imported object not found. (E001)",
    'E002': "SEUT: Collection {variable_1} not found, excluded from view layer or empty. Action not possible. (E002)",
    'E003': "SEUT: {variable_1} path '{variable_2}' doesn't exist. (E003)",
    'E004': "SEUT: No SubtypeId set. (E004)",
    'E005': "SEUT: Linking to scene '{variable_1}' from '{variable_2}' would create a subpart instancing loop. (E005)",
    'E006': "SEUT: LOD2 cannot be set if LOD1 is not, or LOD3 if LOD2 is not. (E006)",
    'E007': "SEUT: '{variable_1}' texture filepath in local material '{variable_2}' does not contain 'Textures\\'. Cannot be transformed into relative path. (E007)",
    'E008': "SEUT: BLEND file must be saved before export. (E008)",
    'E009': "SEUT: Cannot create empties for more than one object at a time. (E009)",
    'E010': "SEUT: Cannot run Simple Navigation if no SEUT collections are present. (E010)",
    'E011': "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (E011)",
    'E012': "SEUT: Path to {variable_1} (Addon Preferences) '{variable_2}' not valid. (E012)",
    'E013': "SEUT: Path to {variable_1} (Addon Preferences) not valid - wrong target file: Expected '{variable_2}' but is set to '{variable_3}'. (E013)",
    'E014': "SEUT: Export path '{variable_1}' does not contain 'Models\\'. Cannot be transformed into relative path. (E014)",
    'E015': "SEUT: Invalid {variable_1} setup. Cannot have {variable_1}2 but no {variable_1}1, or {variable_1}3 but no {variable_1}2. (E015)",
    'E016': "SEUT: Preset '{variable_1}' is invalid or cannot be found. Node Tree cannot be created. Re-link 'MatLib_Presets'! (E016)",
    'E017': "SEUT: Path ({variable_1}) does not point to a 'Materials'-folder. (E017)",
    'E018': "SEUT: Cannot set SubtypeId to a SubtypeId that has already been used for another scene in the same BLEND file. (E018)",
    'E019': "SEUT: No export folder defined. (E019)",
    'E020': "SEUT: Deletion of temporary files failed. (E020)",
    'E021': "SEUT: Available MatLibs could not be refreshed. (E021)",
    'E022': "SEUT: Too many objects in Collision collection. Collection contains {variable_1}, but Space Engineers only supports a maximum of 16. (022)",
    'E023': "SEUT: Empty '{variable_1}' has incorrect rotation value: {variable_2} (E023)",
    'E024': "SEUT: Collection 'Mountpoints ({variable_1})' not found. Disable and then re-enable Mountpoint Mode to recreate! (E024)",
    'E025': "SEUT: Cannot create highlight empty for object outside of 'Main' collection. (E025)",
    'E026': "SEUT: Cannot find {variable_1}. Re-link 'MatLib_Presets'! (E026)",
    'E027': "SEUT: 'Mountpoints {variable_1}' not found. Disable and then re-enable Mountpoint Mode to recreate! (E027)",
    'E028': "SEUT: Object is not an Armature. (E028)",
    'E029': "SEUT: No Armature selected. (E029)",
    'E030': "SEUT: Path is directory, not EXE. (E030)",
    'E031': "SEUT: Cannot export collection if it has more than one top-level (unparented) object. (E031)",
    'E032': "SEUT: Object '{variable_1}' does not have any valid UV-Maps. This will crash Space Engineers. (E032)",
    'E033': "SEUT: Invalid character(s) detected. This will prevent a MWM-file from being generated. Please ensure that no special (non ASCII) characters are used in SubtypeIds, Material names or object names. (E033)",
    'E034': "SEUT: Collision object '{variable_1}' has unapplied modifiers. Collision model cannot be created. (E034)",
    'E035': "SEUT: There was an error during export caused by {variable_1}. Please refer to the logs in your export folder for details. (E035)",
    'E036': "SEUT: An error has occurred in the FBX exporter. Try exiting Edit-Mode before exporting. (E036)",
}

warnings = {
    'W001': ""
}


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
        report_error(self, context, True, 'E008')
        return {'CANCELLED'}

    if os.path.exists(exportPath) == False:
        report_error(self, context, True, 'E003', "Export", exportPath)
        return {'CANCELLED'}
    elif scene.seut.export_exportPath == "":
        report_error(self, context, True, 'E019')
        return {'CANCELLED'}

    if scene.seut.export_exportPath.find("Models\\") == -1:
        report_error(self, context, True, 'E014', exportPath)
        return {'CANCELLED'}

    if scene.seut.subtypeId == "":
        report_error(self, context, True, 'E004')
        return {'CANCELLED'}

    return {'CONTINUE'}

def errorCollection(self, context, scene, collection, partial):
    """Check if collection exists, is not excluded and is not empty"""

    allCurrentViewLayerCollections = scene.view_layers[0].layer_collection.children

    if collection is None:
        if partial:
            print("SEUT Warning: Collection not found. Action not possible.")
            return {'FINISHED'}
        else:
            report_error(self, context, False, 'E002')
            return {'CANCELLED'}
            
    isExcluded = isCollectionExcluded(collection.name, allCurrentViewLayerCollections)

    if isExcluded or isExcluded is None:
        if partial:
            print("SEUT Warning: Collection '" + collection.name + "' excluded from view layer or cannot be found. Action not possible.")
            return {'FINISHED'}
        else:
            report_error(self, context, False, 'E019', collection.name)
            return {'CANCELLED'}

    if len(collection.objects) == 0:
        if partial:
            print("SEUT Warning: Collection '" + collection.name + "' is empty. Action not possible.")
            return {'FINISHED'}
        else:
            report_error(self, context, False, 'E002', '"' + collection.name + '"')
            return {'CANCELLED'}
    
    return {'CONTINUE'}

def errorToolPath(self, context, toolPath, toolName, toolFileName):
    """Checks if external tool is correctly linked"""

    if toolPath == "" or toolPath == "." or os.path.exists(toolPath) is False:
        report_error(self, context, True, 'E012', toolName, toolPath)
        return {'CANCELLED'}

    fileName = os.path.basename(toolPath)
    if toolFileName != fileName:
        report_error(self, context, True, 'E013', toolName, toolFileName, fileName)
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
                        

def showError(context, title, message):

    def draw(self, context):
        self.layout.label(text=message)

    context.window_manager.popup_menu(draw, title=title, icon='ERROR')

    return

def report_error(self, context, works, code, variable_1 = None, variable_2 = None, variable_3 = None):

    if not code in errors:
        return

    text = errors[code]

    try:
        text = text.format(variable_1=variable_1, variable_2=variable_2, variable_3=variable_3)
    except KeyError:
        try:
            text = text.format(variable_1=variable_1, variable_2=variable_2)
        except KeyError:
            text = text.format(variable_1=variable_1)

    link = "https://space-engineers-modding.github.io/modding-reference/tools/3d-modelling/seut/troubleshooting.html#" + code.lower()

    # bpy.ops.message.popup_message(p_type='ERROR', p_text=text, p_link=link)

    if works:
        self.report({'ERROR'}, text)
    else:
        showError(context, "Report: Error", text)

    print("Error: " + text)
    
    return
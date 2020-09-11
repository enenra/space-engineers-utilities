import bpy
import os
import collections

errors = {
    '001': "SEUT: Import error. Imported object not found. (001)",
    '002': "SEUT: Collection not found. Action not possible. (002)",
    '003': "SEUT: Export path '{variable_1}' doesn't exist. (003)",
    '004': "SEUT: No SubtypeId set. (004)",
    '005': "SEUT: Collection '{variable_1}' is empty. Action not possible. (005)",
    '006': "SEUT: LOD2 cannot be set if LOD1 is not, or LOD3 if LOD2 is not. (006)",
    '007': "SEUT: '{variable_1}' texture filepath in local material '{variable_2}' does not contain 'Textures\\'. Cannot be transformed into relative path. (007)",
    '008': "SEUT: BLEND file must be saved before export. (008)",
    '009': "SEUT: Cannot create empties for more than one object at a time. (009)",
    '010': "SEUT: Collection 'Main' not found or empty. Not possible to set automatic bounding box. (010)",
    '011': "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2. (011)",
    '012': "SEUT: Path to {variable_1} '{variable_2}' not valid. (012)",
    '013': "SEUT: Path to {variable_1} not valid - wrong target file: Expected '{variable_2}' but is set to '{variable_3}'. (013)",
    '014': "SEUT: Export path '{variable_1}' does not contain 'Models\\'. Cannot be transformed into relative path. (014)",
    '015': "SEUT: Invalid {variable_1} setup. Cannot have {variable_1}2 but no {variable_1}1, or {variable_1}3 but no {variable_1}2. (015)",
    '016': "SEUT: Cannot find preset '{variable_1}' source material. Node Tree cannot be created. Re-link 'MatLib_Presets'! (016)",
    '017': "SEUT: Path to Materials Folder (Addon Preferences) '{variable_1}' not valid. (017)",
    '018': "SEUT: Cannot set SubtypeId to a SubtypeId that already exists in the file for another scene. (018)",
    '019': "SEUT: Collection '{variable_1}' excluded from view layer or cannot be found. Action not possible. (019)",
    '020': "SEUT: Deletion of loose files failed. (020)",
    '021': "SEUT: Available MatLibs could not be refreshed. (021)",
    '022': "SEUT: Collection not found, excluded or empty. Action not possible. (022)",
    '023': "SEUT: Empty '{variable_1}' has incorrect rotation value: {variable_2} (023)",
    '024': "SEUT: Cannot create empty without 'Main' collection existing. (024)",
    '025': "SEUT: Cannot create highlight empty for object outside of 'Main' collection. (025)",
    '026': "SEUT: Cannot find mirror axis materials. Re-link 'MatLib_Presets'! (026)",
    '027': "SEUT: Cannot find mountpoint material. Re-link 'MatLib_Presets'! (027)",
    '028': "SEUT: Object is not an Armature. (028)",
    '029': "SEUT: No Armature selected. (029)",
    '030': "SEUT: Path is directory, not EXE. (030)",
    '031': "SEUT: Cannot export collection if it has more than one top-level (unparented) object. (031)",
    '032': "SEUT: Object '{variable_1}' does not have any valid UV-Maps. This will crash Space Engineers. (032)",
    '033': "SEUT: Invalid character(s) detected. This will prevent a MWM-file from being generated. Please ensure that no special (non ASCII) characters are used in SubtypeIds, Material names or object names. (033)",
    '034': "SEUT: Collision object '{variable_1}' has unapplied modifiers. Collision model cannot be created. (034)",
    '035': "SEUT: There was an error during export caused by {variable_1}. Please refer to the logs in your export folder for details. (035)",
    '036': "SEUT: 'Mountpoints {variable_1}' not found. Disable and then re-enable Mountpoint Mode to recreate! (036)",
    '037': "SEUT: Collection 'Mountpoints ({variable_1})' not found. Disable and then re-enable Mountpoint Mode to recreate! (037)",
    '038': "SEUT: Too many objects in Collision collection. Collection contains {variable_1}, but Space Engineers only supports a maximum of 16. (038)",
    '039': "SEUT: Path '{variable_1}' does not exist (039)",
    '040': "SEUT: Preset '{variable_1}' is invalid. Node Tree cannot be created. Re-link 'MatLib_Presets'! (040)",
    '041': "SEUT: No export folder defined. (041)",
    '042': "SEUT: Collection 'SEUT ({variable_1})' not found. Action not possible. (042)",
    '043': "SEUT: Path ({variable_1}) does not point to a 'Materials'-folder. (043)",
    '044': "SEUT: Incorrect file linked. Link '{variable_1}' (044)",
    '045': "SEUT: Cannot run Simple Navigation if no SEUT collections are present. (045)",
    '046': "SEUT: Linking to scene '{variable_1}' from '{variable_2}' would create a subpart instancing loop. (046)"
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
        report_error(self, context, True, '008')
        return {'CANCELLED'}

    if os.path.exists(exportPath) == False:
        report_error(self, context, True, '003', exportPath)
        return {'CANCELLED'}
    elif scene.seut.export_exportPath == "":
        report_error(self, context, True, '041')
        return {'CANCELLED'}

    if scene.seut.export_exportPath.find("Models\\") == -1:
        report_error(self, context, True, '014', exportPath)
        return {'CANCELLED'}

    if scene.seut.subtypeId == "":
        report_error(self, context, True, '004')
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
            report_error(self, context, True, '002')
            return {'CANCELLED'}
            
    isExcluded = isCollectionExcluded(collection.name, allCurrentViewLayerCollections)

    if isExcluded or isExcluded is None:
        if partial:
            print("SEUT Warning: Collection '" + collection.name + "' excluded from view layer or cannot be found. Action not possible.")
            return {'FINISHED'}
        else:
            report_error(self, context, True, '019', collection.name)
            return {'CANCELLED'}

    if len(collection.objects) == 0:
        if partial:
            print("SEUT Warning: Collection '" + collection.name + "' is empty. Action not possible.")
            return {'FINISHED'}
        else:
            report_error(self, context, True, '005', collection.name)
            return {'CANCELLED'}
    
    return {'CONTINUE'}

def errorToolPath(self, toolPath, toolName, toolFileName):
    """Checks if external tool is correctly linked"""

    if toolPath == "" or toolPath == "." or os.path.exists(toolPath) is False:
        report_error(self, context, True, '012', toolName, toolPath)
        return {'CANCELLED'}

    fileName = os.path.basename(toolPath)
    if toolFileName != fileName:
        report_error(self, context, True, '013', toolName, toolFileName, fileName)
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

    if not variable_1 is None:
        text = text.format(variable_1=variable_1)
    if not variable_2 is None:
        text = text.format(variable_2=variable_2)
    if not variable_3 is None:
        text = text.format(variable_3=variable_3)

    link = "https://space-engineers-modding.github.io/modding-reference/tools/3d-modelling/seut/troubleshooting.html#" + code

    bpy.ops.message.popup_message(p_type='ERROR', p_text=text, p_link=link)

    if works:
        self.report({'ERROR'}, text)
    else:
        showError(context, "Report: Error", text)

    print("Error: " + text)
    
    return
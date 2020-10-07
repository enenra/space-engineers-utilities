import bpy
import os
import collections

from .libraries.easybpy import *

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
    'W001': "Collection not found. Action not possible.",
    'W002': "Collection '{variable_1}' excluded from view layer or cannot be found. Action not possible.",
    'W003': "Collection '{variable_1}' is empty. Action not possible.",
    'W004': "",
    'W005': "",
    'W006': "",
    'W007': "",
    'W008': "",
    'W009': "",
    'W010': "",
    'W011': "",
    'W012': "",
    'W013': "",
    'W014': "",
    'W015': "",
    'W016': "",
    'W017': "",
    'W018': "",
    'W019': "",
    'W020': "",
}


def check_export(self, context, can_report=True):
    """Basic check for export path and SubtypeId existing"""

    scene = context.scene
    path = get_abs_path(scene.seut.export_exportPath)

    # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
    if not bpy.data.is_saved:
        report_error(self, context, can_report, 'E008')
        return {'CANCELLED'}

    if os.path.exists(path) == False:
        report_error(self, context, can_report, 'E003', "Export", path)
        return {'CANCELLED'}
    elif path == "":
        report_error(self, context, can_report, 'E019')
        return {'CANCELLED'}

    if path.find("Models\\") != -1 or (path + "\\").find("Models\\") != -1:
        return {'CONTINUE'}
    else:
        report_error(self, context, can_report, 'E014', path)
        return {'CANCELLED'}

    if scene.seut.subtypeId == "":
        report_error(self, context, can_report, 'E004')
        return {'CANCELLED'}

    return {'CONTINUE'}


def check_collection(self, context, scene, collection, partial_check=True):
    """Check if collection exists, is not excluded and is not empty"""

    if collection is None:
        if partial_check:
            report_warning(self, context, False, 'W001')
            return {'FINISHED'}
        else:
            report_error(self, context, False, 'E002')
            return {'CANCELLED'}
            
    is_excluded = check_collection_excluded(scene, collection)
    if is_excluded or is_excluded is None:
        if partial_check:
            report_warning(self, context, False, 'W002', collection.name)
            return {'FINISHED'}
        else:
            report_error(self, context, False, 'E019', collection.name)
            return {'CANCELLED'}

    if len(get_objects_from_collection(collection)) == 0:
        if partial_check:
            report_warning(self, context, False, 'W003', collection.name)
            return {'FINISHED'}
        else:
            report_error(self, context, False, 'E002', '"' + collection.name + '"')
            return {'CANCELLED'}
    
    return {'CONTINUE'}


def check_toolpath(self, context, tool_path: str, tool_name: str, tool_filename: str):
    """Checks if external tool is correctly linked"""

    if not os.path.exists(tool_path):
        report_error(self, context, True, 'E012', tool_name, tool_path)
        return {'CANCELLED'}

    file_name = os.path.basename(tool_path)
    if tool_filename != tool_name:
        report_error(self, context, True, 'E013', tool_name, tool_filename, file_name)
        return {'CANCELLED'}
    
    return {'CONTINUE'}


def check_collection_excluded(scene, collection) -> bool:
    """Returns True if the collection is excluded in the view layer"""

    for col in scene.view_layers['SEUT'].layer_collection.children:
        if col.name == collection.name:
            return col.exclude
            
        if collection.name in col.children.keys():
            for child in col.children:
                if child.name == collection.name:
                    return child.exclude
    
    return False
                        

def show_popup_report(context, title, text):
    """Displays a popup message that looks like an error report"""

    def draw(self, context):
        self.layout.label(text=text)

    context.window_manager.popup_menu(draw, title=title, icon='ERROR')

    return

def report_error(self, context, can_report=True, code='E001', variable_1=None, variable_2=None, variable_3=None):
    """Shows a popup error message to the user"""

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

    if can_report:
        self.report({'ERROR'}, text)
    else:
        show_popup_report(context, "Report: Error", text)

    print("Error: " + text)
    
    return


def report_warning(self, context, can_report=True, code='W001', variable_1=None, variable_2=None, variable_3=None):
    """Prints a warning to INFO if possible, else prints to console"""

    if not code in errors:
        return

    text = warnings[code]

    try:
        text = text.format(variable_1=variable_1, variable_2=variable_2, variable_3=variable_3)
    except KeyError:
        try:
            text = text.format(variable_1=variable_1, variable_2=variable_2)
        except KeyError:
            text = text.format(variable_1=variable_1)

    if can_report:
        self.report({'WARNING'}, text)

    print("Warning: " + text)
    
    return


def get_abs_path(path: str) -> str:
    """Returns the absolute path"""
    return os.path.abspath(bpy.path.abspath(path))
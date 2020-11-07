import bpy
import os
import collections
import time


errors = {
    'E001': "SEUT: Import error. Imported object not found.",
    'E002': "SEUT: Collection {variable_1} not found, excluded from view layer or empty. Action not possible.",
    'E003': "SEUT: {variable_1} path '{variable_2}' doesn't exist.",
    'E004': "SEUT: No SubtypeId set.",
    'E005': "SEUT: Linking to scene '{variable_1}' from '{variable_2}' would create a subpart instancing loop.",
    'E006': "SEUT: LOD2 cannot be set if LOD1 is not, or LOD3 if LOD2 is not.",
    'E007': "SEUT: '{variable_1}' texture filepath in local material '{variable_2}' does not contain 'Textures\\'. Cannot be transformed into relative path.",
    'E008': "SEUT: BLEND file must be saved before export.",
    'E009': "SEUT: Cannot create empties for more than one object at a time.",
    'E010': "SEUT: Cannot run Simple Navigation if no SEUT collections are present.",
    'E011': "SEUT: Invalid LOD distances. LOD2 cannot be set to be displayed before LOD1 or LOD3 before LOD2.",
    'E012': "SEUT: Path to {variable_1} (Addon Preferences) '{variable_2}' not valid.",
    'E013': "SEUT: Path to {variable_1} (Addon Preferences) not valid - wrong target file: Expected '{variable_2}' but is set to '{variable_3}'.",
    'E014': "SEUT: Export path '{variable_1}' in scene '{variable_2}' does not contain 'Models\\'. Cannot be transformed into relative path.",
    'E015': "SEUT: Invalid {variable_1} setup. Cannot have {variable_1}2 but no {variable_1}1, or {variable_1}3 but no {variable_1}2.",
    'E016': "SEUT: Preset '{variable_1}' is invalid or cannot be found. Node Tree cannot be created. Re-link 'MatLib_Presets'!",
    'E017': "SEUT: Path ({variable_1}) does not point to a 'Materials'-folder.",
    'E018': "SEUT: Cannot set SubtypeId to a SubtypeId that has already been used for another scene in the same BLEND file.",
    'E019': "SEUT: No export folder defined.",
    'E020': "SEUT: Deletion of temporary files failed.",
    'E021': "SEUT: Available MatLibs could not be refreshed.",
    'E022': "SEUT: Too many objects in Collision collection. Collection contains {variable_1}, but Space Engineers only supports a maximum of 16.",
    'E023': "SEUT: Empty '{variable_1}' has incorrect rotation value: {variable_2}",
    'E024': "SEUT: Collection 'Mountpoints ({variable_1})' not found. Disable and then re-enable Mountpoint Mode to recreate!",
    'E025': "SEUT: Cannot create highlight empty for object outside of 'Main' collection.",
    'E026': "SEUT: Filename incorrect: BLEND-filename must start with 'MatLib_' to create a valid MatLib.",
    'E027': "SEUT: 'Mountpoints {variable_1}' not found. Disable and then re-enable Mountpoint Mode to recreate!",
    'E028': "SEUT: Object is not an Armature.",
    'E029': "SEUT: No Armature selected.",
    'E030': "SEUT: Path is directory, not EXE.",
    'E031': "SEUT: Cannot export collection if it has more than one top-level (unparented) object.",
    'E032': "SEUT: Object '{variable_1}' does not have any valid UV-Maps. This will crash Space Engineers.",
    'E033': "SEUT: Invalid character(s) detected. This will prevent a MWM-file from being generated. Please ensure that no special (non ASCII) characters are used in SubtypeIds, Material names or object names.",
    'E034': "SEUT: Collision object '{variable_1}' has unapplied modifiers. Collision model cannot be created.",
    'E035': "SEUT: There was an error during export caused by {variable_1}. Please refer to the logs in your export folder for details.",
    'E036': "SEUT: An error has occurred in the FBX exporter. Try exiting Edit-Mode before exporting.",
    'E037': "SEUT: Scene '{variable_1}' could not be exported.",
}

warnings = {
    'W001': "SEUT: Collection not found. Action not possible.",
    'W002': "SEUT: Collection '{variable_1}' excluded from view layer or cannot be found. Action not possible.",
    'W003': "SEUT: Collection '{variable_1}' is empty. Action not possible.",
    'W004': "SEUT: '{variable_1}' texture of local material '{variable_2}' is not of a valid resolution ({variable_3}). May not display correctly ingame.",
    'W005': "SEUT: Empty '{variable_1}' (numbering might differ) in collection '{variable_2}' has no parent object. This may prevent it from working properly ingame.",
    'W006': "SEUT: Parent of empty '{variable_1}' (numbering might differ), '{variable_2}', in collection '{variable_3}' has a parent object. This may prevent the empty from working properly ingame.",
    'W007': "SEUT: Highlight empty '{variable_1}' and its linked object '{variable_2}' have different parent objects. This may prevent the empty from working properly ingame.",
    'W008': "SEUT: Scene is of type '{variable_1}' but does not contain any armatures.",
    'W009': "SEUT: Scene is of type '{variable_1}' but contains armatures.",
    'W010': "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2.",
    'W011': "SEUT: Library '{variable_1}' could not be relocated in '{variable_2}'.",
    'W012': "SEUT: Could not remove unused material slots for object '{variable_1}'.",
}

infos = {
    'I001': "SEUT: Local material '{variable_1}' does not contain any valid textures. Skipping XML entry.",
    'I002': "SEUT: Local material '{variable_1}' saved. Don't forget to include relevant DDS texture files in mod!",
    'I003': "SEUT: Collection '{variable_1}' not found or empty. Skipping XML entry.",
    'I004': "SEUT: '{variable_1}' has been created.",
    'I005': "SEUT: IndexError at material '{variable_1}'.",
    'I006': "SEUT: Export Options successfully copied to all scenes.",
    'I007': "SEUT: FBX and XML files of scene '{variable_1}' have been compiled to MWM.",
    'I008': "SEUT: {variable_1} of {variable_2} scenes successfully exported. Refer to Blender System Console for details.",
    'I009': "SEUT: Collision files have been created.",
    'I010': "SEUT: {variable_1} '{variable_2}' created.",
    'I011': "SEUT: Highlight '{variable_1}' created for object '{variable_2}'.",
    'I012': "SEUT: Structure conversion successfully completed.",
    'I013': "SEUT: Attempt to Fix Positioning completed.",
    'I014': "SEUT: Import successfully completed.",
    'I015': "SEUT: Bounding Box set for dimensions X: {variable_1} Y: {variable_2} Z: {variable_3}",
    'I016': "SEUT: Empty '{variable_1}' rotation {variable_2} registered as: {variable_3}",
    'I017': "SEUT: Mountpoint Area {variable_1} saved. {variable_2} {variable_3}",
    'I018': "SEUT: Icon successfully saved to '{variable_1}'.",
}


def check_export(self, context, can_report=True):
    """Basic check for export path and SubtypeId existing."""

    scene = context.scene
    path = get_abs_path(scene.seut.export_exportPath)

    # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
    if not bpy.data.is_saved:
        seut_report(self, context, 'ERROR', can_report, 'E008')
        return {'CANCELLED'}

    if os.path.exists(path) == False:
        seut_report(self, context, 'ERROR', can_report, 'E003', "Export", path)
        return {'CANCELLED'}
    elif path == "":
        seut_report(self, context, 'ERROR', can_report, 'E019')
        return {'CANCELLED'}

    if path.find("Models\\") != -1 or (path + "\\").find("Models\\") != -1:
        pass
    else:
        seut_report(self, context, 'ERROR', can_report, 'E014', path, scene.name)
        return {'CANCELLED'}

    if scene.seut.subtypeId == "":
        seut_report(self, context, 'ERROR', can_report, 'E004')
        return {'CANCELLED'}

    return {'CONTINUE'}


def check_collection(self, context, scene, collection, partial_check=True):
    """Check if collection exists, is not excluded and is not empty."""

    if collection is None:
        if partial_check:
            seut_report(self, context, 'WARNING', False, 'W001')
            return {'FINISHED'}
        else:
            seut_report(self, context, 'ERROR', False, 'E002')
            return {'CANCELLED'}
            
    is_excluded = check_collection_excluded(scene, collection)
    if is_excluded or is_excluded is None:
        if partial_check:
            seut_report(self, context, 'WARNING', False, 'W002', collection.name)
            return {'FINISHED'}
        else:
            seut_report(self, context, 'ERROR', False, 'E019', collection.name)
            return {'CANCELLED'}

    if len(collection.objects) == 0 and collection.name[:4] != 'SEUT':
        if partial_check:
            seut_report(self, context, 'WARNING', False, 'W003', collection.name)
            return {'FINISHED'}
        else:
            seut_report(self, context, 'ERROR', False, 'E002', '"' + collection.name + '"')
            return {'CANCELLED'}
    
    return {'CONTINUE'}


def check_toolpath(self, context, tool_path: str, tool_name: str, tool_filename: str):
    """Checks if external tool is correctly linked."""

    path = get_abs_path(tool_path)
    if not os.path.exists(path):
        seut_report(self, context, 'ERROR', True, 'E012', tool_name, path)
        return {'CANCELLED'}

    file_name = os.path.basename(tool_path)
    if tool_filename != file_name:
        seut_report(self, context, 'ERROR', True, 'E013', tool_name, tool_filename, file_name)
        return {'CANCELLED'}
    
    return {'CONTINUE'}


def check_collection_excluded(scene, collection) -> bool:
    """Returns True if the collection is excluded in the view layer."""

    for col in scene.view_layers['SEUT'].layer_collection.children:
        if col.name == collection.name:
            return col.exclude
            
        if collection.name in col.children.keys():
            for child in col.children:
                if child.name == collection.name:
                    return child.exclude
    
    return False


def check_uvms(self, context, obj):
    """Checks whether object has UV layers"""

    if obj is not None and obj.type == 'MESH' and len(obj.data.uv_layers) < 1:
        seut_report(self, context, 'ERROR', True, 'E032', obj.name)
        return {'CANCELLED'}
    
    return {'CONTINUE'}


def get_abs_path(path: str) -> str:
    """Returns the absolute path"""
    return os.path.abspath(bpy.path.abspath(path))
                        

def show_popup_report(context, title, text: str):
    """Displays a popup message that looks like an error report."""

    def draw(self, context):
        self.layout.label(text=text)

    context.window_manager.popup_menu(draw, title=title, icon='ERROR')


def seut_report(self, context, report_type: str, can_report: bool, code: str, variable_1=None, variable_2=None, variable_3=None):
    """Displays a report as a popup message and / or writes it into INFO, if possible."""

    if report_type == 'ERROR':
        if not code in errors:
            return
        text = errors[code]
    elif report_type == 'WARNING':
        if not code in warnings:
            return
        text = warnings[code]
    elif report_type == 'INFO':
        if not code in infos:
            return
        text = infos[code]

    try:
        text = text.format(variable_1=variable_1, variable_2=variable_2, variable_3=variable_3)
    except KeyError:
        try:
            text = text.format(variable_1=variable_1, variable_2=variable_2)
        except KeyError:
            text = text.format(variable_1=variable_1)

    link = "https://space-engineers-modding.github.io/modding-reference/tools/3d-modelling/seut/troubleshooting.html#" + code.lower()

    # bpy.ops.message.popup_message(p_type='ERROR', p_text=text, p_link=link)

    # if can_report:
    #     self.report({report_type}, text)

    # else:
    if report_type == 'ERROR':
        show_popup_report(context, "Report: Error", text)
        print("Error: " + text + " (" + code + ")")
    elif report_type == 'WARNING':
        print("Warning: " + text + " (" + code + ")")
    elif report_type == 'INFO':
        print("Info: " + text + " (" + code + ")")
    
    add_to_issues(context, report_type, text, code, None)


def add_to_issues(context, issue_type: str, text: str, code: str, reference: str):
    """Adds an entry to the SEUT issues list"""

    wm = context.window_manager
    issues = wm.seut.issues

    while len(issues) > 19:
        oldest = None
        for index in range(0, len(issues)):
            if oldest == None:
                oldest = index
            elif issues[index].timestamp < oldest:
                oldest = index
    
        issues.remove(oldest)
    
    issue = issues.add()
    issue.timestamp = time.time()
    issue.issue_type = issue_type
    issue.text = text[len("SEUT: "):]
    if code is not None:
        issue.code = code
    if reference is not None:
        issue.reference = reference
    if issue_type == 'ERROR':
        wm.seut.issue_alert = True
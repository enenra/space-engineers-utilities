import bpy
import os
import re

from bpy.types  import Operator

from ..seut_errors              import seut_report, get_abs_path
from ..seut_utils               import get_preferences


class SEUT_OT_RefreshMatLibs(Operator):
    """Refresh available MatLibs"""
    bl_idname = "wm.refresh_matlibs"
    bl_label = "Refresh MatLibs"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        result = refresh_matlibs(self, context)

        return result
    

def refresh_matlibs(self, context):
    """Refresh available MatLibs"""

    wm = context.window_manager
    preferences = get_preferences()
    materials_path = get_abs_path(preferences.materials_path)

    if preferences.materials_path == "" or os.path.isdir(materials_path) == False:
        seut_report(self, context, 'ERROR', True, 'E012', "Materials Folder", materials_path)
        return {'CANCELLED'}

    # Find all MatLibs in directory, save to set, then add to matlibs list
    new_set = set()

    for file in os.listdir(materials_path):
        if file is not None and file.endswith(".blend") and file.lower().find("matlib_") != -1:
            new_set.add(file)

    # Add everything in the directory that is not already in the set to the set
    for lib in new_set:
        if lib in wm.seut.matlibs:
            continue
        else:
            item = wm.seut.matlibs.add()
            item.name = lib

    # If the set has entries that don't exist in the directory, remove them
    for lib in wm.seut.matlibs:
        if lib.name in new_set:
            for mat in bpy.data.materials:
                if mat.library is not None and mat.library.name == lib.name:
                    wm.seut.matlibs[wm.seut.matlibs.find(lib.name)].enabled = True
                    break
            continue
        else:
            for index in range(0, len(wm.seut.matlibs)):
                try:
                    if wm.seut.matlibs[index].name == lib.name:
                        wm.seut.matlibs.remove(index)
                except IndexError:
                    pass
    
    # Finally, attempt to re-link any MatLibs with broken paths
    try:
        currentArea = context.area.type
        context.area.type = 'OUTLINER'
    except AttributeError:
        try:
            context.area.type = 'OUTLINER'
            currentArea = context.area.type
        # If it fails here it generally means that this is on startup before context.area is even set.
        except AttributeError:
            pass

    for lib in bpy.data.libraries:
        if os.path.exists(lib.filepath) == False:
            
            if re.search("\.[0-9]{3}", lib.name[-4:]) != None:
                lib.name = lib.name[:-4]

            try:
                bpy.ops.wm.lib_relocate(
                    library=lib.name,
                    directory=materials_path,
                    filename=lib.name
                )
            except:
                seut_report(self, context, 'WARNING', False, 'W010', lib.name, materials_path)

    try:
        context.area.type = currentArea
    except UnboundLocalError:
        pass

    return {'FINISHED'}
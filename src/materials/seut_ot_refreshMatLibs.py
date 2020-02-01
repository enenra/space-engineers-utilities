import bpy
import os

from bpy.types  import Operator

class SEUT_OT_RefreshMatLibs(Operator):
    """Refresh available MatLibs"""
    bl_idname = "scene.refresh_matlibs"
    bl_label = "Refresh MatLibs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        SEUT_OT_RefreshMatLibs.refreshMatLibs(self, context)

        return {'FINISHED'}
    
    def refreshMatLibs(self, context):
        """Refresh available MatLibs"""

        wm = context.window_manager

        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences
        materialsPath = os.path.normpath(bpy.path.abspath(preferences.materialsPath))

        if preferences.materialsPath == "" or os.path.exists(materialsPath) == False:
            self.report({'ERROR'}, "SEUT: Path to Materials Folder not valid. (017)")
            print("SEUT Info: Path to Materials Folder not valid. (017)")
            return {'CANCELLED'}

        # Find all MatLibs in directory, save to set, then add to matlibs list
        path = bpy.path.abspath(preferences.materialsPath)
        newSet = set()

        for file in os.listdir(path):
            if file is not None and file.endswith(".blend") and file.find("MatLib_") != -1:
                newSet.add(file)

        # Add everything in the directory that is not already in the set to the set
        for libNew in newSet:
            if libNew in wm.matlibs:
                continue
            else:
                item = wm.matlibs.add()
                item.name = libNew

        # If the set has entries that don't exist in the directory, remove them
        for libOld in wm.matlibs:
            if libOld.name in newSet:
                continue
            else:
                for idx in range(0, len(wm.matlibs)):
                    if wm.matlibs[idx].name == libOld.name:
                        wm.matlibs.remove(idx)

        return {'FINISHED'}
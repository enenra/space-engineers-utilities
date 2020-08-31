import bpy
import os

from bpy.types  import Operator, AddonPreferences
from bpy.props  import BoolProperty, StringProperty, EnumProperty

from .seut_errors   import showError

def set_dev_tools_paths(self, context):
    scene = context.scene

    if not self.set_dev_tools_paths:
        return
    else:
        if os.path.isdir("E:\\Games\\Modding\\SE\\models\\Materials\\"):
            self.materialsPath = "E:\\Games\\Modding\\SE\\models\\Materials\\"
            self.mwmbPath = "E:\\Games\\Modding\\SE\\tools\\MwmBuilder\\MwmBuilder.exe"
            self.fbxImporterPath = "E:\\Games\\Modding\\SE\\tools\\FBXImporter.exe"
            self.havokPath="E:\\Games\\Modding\\SE\\tools\\Havok\\HavokContentTools\\hctStandAloneFilterManager.exe"
            
        elif os.path.isdir("C:\\3D_Projects\\SpaceEngineers\\MaterialLibraries\\Materials\\"):
            self.materialsPath = "C:\\3D_Projects\\SpaceEngineers\\MaterialLibraries\\Materials\\"
            self.mwmbPath = "C:\\3D_Projects\\BlenderPlugins\\StollieMWMBuilder\\MwmBuilder.exe"
            self.fbxImporterPath = "C:\\3D_Projects\\BlenderPlugins\\HavokFBXImporter\\FBXImporter.exe"
            self.havokPath="C:\\3D_Projects\\BlenderPlugins\\Havok\\HavokContentTools\\hctStandAloneFilterManager.exe"
        
        self.set_dev_tools_paths = False

def update_materialsPath(self, context):
    scene = context.scene

    if self.materialsPath == "":
        return

    if os.path.isdir(os.path.abspath(bpy.path.abspath(self.materialsPath))):
        if not bpy.path.abspath(self.materialsPath[-10:-1]) == 'Materials':
            showError(context, "Report: Error", "SEUT Error: Path (" + bpy.path.abspath(self.materialsPath[-10:-1]) + ")" + 
                " does not point to a 'Materials'-folder. (017)")
            self.materialsPath = ""
        else:
            bpy.ops.scene.refresh_matlibs()
    else:
        showError(context, "Report: Error", "SEUT Error: Path '" + os.path.abspath(bpy.path.abspath(self.materialsPath)) + "' does not exist (039)")
        self.materialsPath = ""
    

def update_fbxImporterPath(self, context):
    name = 'FBXImporter.exe'

    if self.fbxImporterPath == "":
        return
    elif self.fbxImporterPath == self.fbxImporterPath_Before:
        return

    path = os.path.abspath(bpy.path.abspath(self.fbxImporterPath))
    
    # If it's a directory but appending the name gives a valid path, do that. Else, error.
    if os.path.isdir(path):
        if os.path.exists(path + "\\" + name):
            self.fbxImporterPath_Before = path + "\\" + name
            self.fbxImporterPath = path + "\\" + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.fbxImporterPath = ""

    # If it's not a directory and the path doesn't exist, error. If the basename is equal to the name, use the path. If the basename is not equal, error.
    elif not os.path.isdir(path):
        
        if not os.path.exists(path):
            showError(context, "Report: Error", "SEUT Error: Path '" + os.path.abspath(bpy.path.abspath(self.fbxImporterPath)) + "' does not exist (039)")
            self.havokPfbxImporterPathath = ""

        else:
            if os.path.basename(self.fbxImporterPath) == name:
                self.fbxImporterPath_Before = path
                self.fbxImporterPath = path
            else:
                showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
                self.fbxImporterPath = ""


def update_havokPath(self, context):
    name = 'hctStandAloneFilterManager.exe'

    if self.havokPath == "":
        return
    elif self.havokPath == self.havokPath_Before:
        return

    path = os.path.abspath(bpy.path.abspath(self.havokPath))
    
    # If it's a directory but appending the name gives a valid path, do that. Else, error.
    if os.path.isdir(path):
        if os.path.exists(path + "\\" + name):
            self.havokPath_Before = path + "\\" + name
            self.havokPath = path + "\\" + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.havokPath = ""

    # If it's not a directory and the path doesn't exist, error. If the basename is equal to the name, use the path. If the basename is not equal, error.
    elif not os.path.isdir(path):
        
        if not os.path.exists(path):
            showError(context, "Report: Error", "SEUT Error: Path '" + os.path.abspath(bpy.path.abspath(self.havokPath)) + "' does not exist (039)")
            self.havokPath = ""

        else:
            if os.path.basename(self.havokPath) == name:
                self.havokPath_Before = path
                self.havokPath = path
            else:
                showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
                self.havokPath = ""


def update_mwmbPath(self, context):
    name = str('MwmBuilder.exe')

    if self.mwmbPath == "":
        return
    elif self.mwmbPath == self.mwmbPath_Before:
        return

    path = os.path.abspath(bpy.path.abspath(self.mwmbPath))
    
    # If it's a directory but appending the name gives a valid path, do that. Else, error.
    if os.path.isdir(path):
        if os.path.exists(path + "\\" + name):
            self.mwmbPath_Before = path + "\\" + name
            self.mwmbPath = path + "\\" + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.mwmbPath = ""

    # If it's not a directory and the path doesn't exist, error. If the basename is equal to the name, use the path. If the basename is not equal, error.
    elif not os.path.isdir(path):

        if not os.path.exists(path):
            showError(context, "Report: Error", "SEUT Error: Path '" + os.path.abspath(bpy.path.abspath(self.mwmbPath)) + "' does not exist (039)")
            self.mwmbPath = ""

        else:
            if os.path.basename(self.mwmbPath) == name:
                self.mwmbPath_Before = path
                self.mwmbPath = path
            else:
                showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
                self.mwmbPath = ""


def get_addon_version():
    return addon_version
    

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__
    set_dev_tools_paths: BoolProperty(
        name = "Set Dev Paths",
        description = "Set Dev Paths",
        default = False,
        update=set_dev_tools_paths
    )
    materialsPath: StringProperty(
        name="Materials Folder",
        description="This folder contains material information in the form of XML libraries as well as BLEND MatLibs",
        subtype='FILE_PATH',
        update=update_materialsPath
    )
    fbxImporterPath: StringProperty(
        name="Custom FBX Importer",
        description="Despite its name, this tool is mainly used to export models to the FBX format",
        subtype='FILE_PATH',
        update=update_fbxImporterPath
    )
    fbxImporterPath_Before: StringProperty(
        subtype='FILE_PATH'
    )
    havokPath: StringProperty(
        name="Havok Standalone Filter Manager",
        description="This tool is required to create Space Engineers collision models",
        subtype='FILE_PATH',
        update=update_havokPath
    )
    havokPath_Before: StringProperty(
        subtype='FILE_PATH'
    )
    mwmbPath: StringProperty(
        name="MWM Builder",
        description="This tool converts the individual 'loose files' that the export yields into MWM files the game can read",
        subtype='FILE_PATH',
        update=update_mwmbPath
    )
    mwmbPath_Before: StringProperty(
        subtype='FILE_PATH'
    )

    def draw(self, context):
        layout = self.layout

        # layout.prop(self, "set_dev_tools_paths")

        layout.prop(self, "materialsPath", expand=True)
        box = layout.box()
        box.label(text="External Tools")
        box.prop(self, "mwmbPath", expand=True)
        box.prop(self, "fbxImporterPath", expand=True)
        box.prop(self, "havokPath", expand=True)

        return
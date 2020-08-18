import bpy
import os

from bpy.types  import Operator, AddonPreferences
from bpy.props  import BoolProperty, StringProperty, EnumProperty

from .seut_errors   import showError

def set_stollie_tools_paths(self, context):
    scene = context.scene

    if not self.set_stollie_tools_paths:
        return
    else:
        self.materialsPath = "C:\\3D_Projects\\SpaceEngineers\\MaterialLibraries\\Materials\\"
        self.mwmbPath = "C:\\3D_Projects\\BlenderPlugins\\StollieMWMBuilder\\MwmBuilder.exe"
        self.fbxImporterPath = "C:\\3D_Projects\\BlenderPlugins\\HavokFBXImporter\\FBXImporter.exe"
        self.havokPath = "C:\\3D_Projects\\BlenderPlugins\\Havok\\HavokContentTools\\hctStandAloneFilterManager.exe"

def update_materialsPath(self, context):
    scene = context.scene

    if self.materialsPath == "":
        return

    if os.path.isdir(bpy.path.abspath(self.materialsPath)):
        if not bpy.path.abspath(self.materialsPath[-10:-1]) == 'Materials':
            showError(context, "Report: Error", "SEUT Error: Path (" + bpy.path.abspath(self.materialsPath[-10:-1]) + ")" + 
                " does not point to a 'Materials'-folder. (017)")
            self.materialsPath = ""
        else:
            bpy.ops.scene.refresh_matlibs()
    

def update_fbxImporterPath(self, context):
    name = 'FBXImporter.exe'

    if self.fbxImporterPath == "":
        return

    if os.path.isdir(bpy.path.abspath(self.fbxImporterPath)):
        if os.path.exists(bpy.path.abspath(self.fbxImporterPath) + name):
            self.fbxImporterPath = bpy.path.abspath(self.fbxImporterPath) + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.fbxImporterPath = ""

    elif os.path.basename(self.fbxImporterPath) != name:
        showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
        self.fbxImporterPath = ""


def update_havokPath(self, context):
    name = 'hctStandAloneFilterManager.exe'

    if self.havokPath == "":
        return

    if os.path.isdir(bpy.path.abspath(self.havokPath)):
        if os.path.exists(bpy.path.abspath(self.havokPath) + name):
            self.havokPath = bpy.path.abspath(self.havokPath) + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.havokPath = ""

    elif os.path.basename(self.havokPath) != name:
        showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
        self.havokPath = ""


def update_mwmbPath(self, context):
    name = str('MwmBuilder.exe')

    if self.mwmbPath == "":
        return

    if os.path.isdir(bpy.path.abspath(self.mwmbPath)):
        if os.path.exists(bpy.path.abspath(self.mwmbPath) + name):
            self.mwmbPath = bpy.path.abspath(self.mwmbPath) + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.mwmbPath = ""

    elif os.path.basename(self.mwmbPath) != name:
        showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
        self.mwmbPath = ""
    

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__
    set_stollie_tools_paths: BoolProperty(
        name = "Set Stollie Paths",
        description = "Set Stollie Paths",
        default = False,
        update=set_stollie_tools_paths
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
    havokPath: StringProperty(
        name="Havok Standalone Filter Manager",
        description="This tool is required to create Space Engineers collision models",
        subtype='FILE_PATH',
        update=update_havokPath
    )
    mwmbPath: StringProperty(
        name="MWM Builder",
        description="This tool converts the individual 'loose files' that the export yields into MWM files the game can read",
        subtype='FILE_PATH',
        update=update_mwmbPath
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "materialsPath", expand=True)
        box = layout.box()
        box.label(text="External Tools")
        box.prop(self, "mwmbPath", expand=True)
        box.prop(self, "fbxImporterPath", expand=True)
        box.prop(self, "havokPath", expand=True)

        return
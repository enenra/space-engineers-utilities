import bpy
import os

from bpy.types  import Operator, AddonPreferences
from bpy.props  import (StringProperty,
                       EnumProperty
                       )

from .seut_errors   import showError

from . import addon_updater_ops

def update_fbxImporterPath(self, context):
    name = 'FBXImporter.exe'

    if self.fbxImporterPath == "":
        return

    if os.path.isdir(self.fbxImporterPath):
        if os.path.exists(self.fbxImporterPath + name):
            self.fbxImporterPath = self.fbxImporterPath + name
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

    if os.path.isdir(self.havokPath):
        if os.path.exists(self.havokPath + name):
            self.havokPath = self.havokPath + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.havokPath = ""

    elif os.path.basename(self.havokPath) != name:
        showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
        self.havokPath = ""


def update_materialsPath(self, context):
    scene = context.scene

    if self.materialsPath == "":
        return

    if os.path.isdir(self.materialsPath):
        if not self.materialsPath[-10:-1] == 'Materials':
            showError(context, "Report: Error", "SEUT Error: Path does not point to a 'Materials'-folder. (017)")
            self.materialsPath = ""
        else:
            bpy.ops.scene.refresh_matlibs()
    

def update_mwmbPath(self, context):
    name = str('MwmBuilder.exe')

    if self.mwmbPath == "":
        return

    if os.path.isdir(self.mwmbPath):
        if os.path.exists(self.mwmbPath + name):
            self.mwmbPath = self.mwmbPath + name
        else:
            showError(context, "Report: Error", "SEUT Error: Path is directory, not EXE. (030)")
            self.mwmbPath = ""

    elif os.path.basename(self.mwmbPath) != name:
        showError(context, "Report: Error", "SEUT Error: Incorrect file linked. Link '" + name + "' (030)")
        self.mwmbPath = ""
    

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

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
    materialsPath: StringProperty(
        name="Materials Folder",
        description="This folder contains material information in the form of XML libraries as well as BLEND MatLibs",
        subtype='FILE_PATH',
        update=update_materialsPath
    )

    # addon updater preferences from `__init__`, be sure to copy all of them
    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = True,
    )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=0,
        min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=23,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "materialsPath", expand=True)
        box = layout.box()
        box.label(text="External Tools")
        box.prop(self, "mwmbPath", expand=True)
        box.prop(self, "fbxImporterPath", expand=True)
        box.prop(self, "havokPath", expand=True)


        addon_updater_ops.update_settings_ui(self,context)

        return
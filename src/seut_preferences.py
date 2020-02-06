import bpy

from bpy.types  import Operator, AddonPreferences
from bpy.props  import (StringProperty,
                       EnumProperty
                       )

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    fbxImporterPath: StringProperty(
        name="Custom FBX Importer",
        description="Despite its name, this tool is mainly used to export models to the FBX format",
        subtype='FILE_PATH',
    )
    havokPath: StringProperty(
        name="Havok Standalone Filter Manager",
        description="This tool is required to create Space Engineers collision models",
        subtype='FILE_PATH',
    )
    mwmbPath: StringProperty(
        name="MWM Builder",
        description="This tool converts the individual 'loose files' that the export yields into MWM files the game can read",
        subtype='FILE_PATH',
    )
    materialsPath: StringProperty(
        name="Materials Folder",
        description="This folder contains material information in the form of XML libraries as well as BLEND MatLibs",
        subtype='FILE_PATH',
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
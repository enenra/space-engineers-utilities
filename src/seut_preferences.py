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
        subtype='FILE_PATH',
    )
    havokPath: StringProperty(
        name="Havok Standalone Filter Manager",
        subtype='FILE_PATH',
    )
    mwmbPath: StringProperty(
        name="MWM Builder",
        subtype='FILE_PATH',
    )
    materialsPath: StringProperty(
        name="Materials Folder",
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
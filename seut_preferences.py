import bpy

from bpy.types  import Operator, AddonPreferences
from bpy.props  import StringProperty

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    pref_mwmbPath: StringProperty(
        name="MWM Builder",
        subtype='FILE_PATH',
    )
    pref_fbxImporterPath: StringProperty(
        name="Custom FBX Importer",
        subtype='FILE_PATH',
    )
    pref_havokPath: StringProperty(
        name="Standalone File Manager",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pref_mwmbPath", expand=True)
        box = layout.box()
        box.label(text="Havok")
        box.prop(self, "pref_fbxImporterPath", expand=True)
        box.prop(self, "pref_havokPath", expand=True)

        return
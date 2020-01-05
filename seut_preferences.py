import bpy

from bpy.types  import Operator, AddonPreferences
from bpy.props  import StringProperty

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    pref_havokPath: StringProperty(
        name="Havok Standalone File Manager",
        subtype='FILE_PATH',
    )
    pref_mwmbPath: StringProperty(
        name="MWM Builder",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="External Executables")
        box.prop(self, "pref_havokPath", expand=True)
        box.prop(self, "pref_mwmbPath", expand=True)

        return
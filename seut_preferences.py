import bpy

from bpy.types  import Operator, AddonPreferences
from bpy.props  import (StringProperty,
                       EnumProperty
                       )

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    pref_looseFilesExportFolder: EnumProperty(
        name='Loose Files Export Folder',
        items=(
            ('0', '.blend Folder', 'Directory containing the current .blend file.'),
            ('1', 'Export Folder', 'Directory set as the export folder. (Normally only used for MWM file.)')
            ),
        default='0'
    )

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
        layout.prop(self, "pref_looseFilesExportFolder")
        layout.prop(self, "pref_mwmbPath", expand=True)
        box = layout.box()
        box.label(text="Havok")
        box.prop(self, "pref_fbxImporterPath", expand=True)
        box.prop(self, "pref_havokPath", expand=True)

        return
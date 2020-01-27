import bpy

from bpy.types  import Operator, AddonPreferences
from bpy.props  import (StringProperty,
                       EnumProperty
                       )

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    looseFilesExportFolder: EnumProperty(
        name='Loose Files Export Folder',
        items=(
            ('0', '.blend Folder', 'Directory containing the current .blend file.'),
            ('1', 'Export Folder', 'Directory set as the export folder. (Normally only used for MWM file.)')
            ),
        default='0'
    )

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
        layout.prop(self, "looseFilesExportFolder")
        layout.prop(self, "mwmbPath", expand=True)
        layout.prop(self, "materialsPath", expand=True)
        box = layout.box()
        box.label(text="Havok")
        box.prop(self, "fbxImporterPath", expand=True)
        box.prop(self, "havokPath", expand=True)

        return
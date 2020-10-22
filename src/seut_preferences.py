import bpy
import os

from bpy.types  import Operator, AddonPreferences
from bpy.props  import BoolProperty, StringProperty, EnumProperty

from .seut_errors   import seut_report, get_abs_path
        

def update_set_dev_paths(self, context):
    scene = context.scene

    if not self.set_dev_paths:
        return
    else:
        # enenra
        if os.path.isdir("E:\\Games\\Modding\\SE\\models\\Materials\\"):
            self.materials_path = "E:\\Games\\Modding\\SE\\models\\Materials\\"
            self.mwmb_path = "E:\\Games\\Modding\\SE\\tools\\MwmBuilder\\MwmBuilder.exe"
            self.fbx_importer_path = "E:\\Games\\Modding\\SE\\tools\\FBXImporter.exe"
            self.havok_path="E:\\Games\\Modding\\SE\\tools\\Havok\\HavokContentTools\\hctStandAloneFilterManager.exe"
        
        # Stollie
        elif os.path.isdir("C:\\3D_Projects\\SpaceEngineers\\MaterialLibraries\\Materials\\"):
            self.materials_path = "C:\\3D_Projects\\SpaceEngineers\\MaterialLibraries\\Materials\\"
            self.mwmb_path = "C:\\3D_Projects\\BlenderPlugins\\StollieMWMBuilder\\MwmBuilder.exe"
            self.fbx_importer_path = "C:\\3D_Projects\\BlenderPlugins\\HavokFBXImporter\\FBXImporter.exe"
            self.havok_path="C:\\3D_Projects\\BlenderPlugins\\Havok\\HavokContentTools\\hctStandAloneFilterManager.exe"
        
        self.set_dev_paths = False


def update_materials_path(self, context):
    scene = context.scene

    if self.materials_path == "":
        return
    
    path = get_abs_path(self.materials_path)

    if os.path.isdir(path):
        if not path[-9:] == 'Materials':
            seut_report(self, context, 'ERROR', False, 'E017', self.materials_path)
            self.materials_path = ""
        else:
            bpy.ops.scene.refresh_matlibs()
    else:
        seut_report(self, context, 'ERROR', False, 'E003', 'Materials', os.path.abspath(bpy.path.abspath(self.materials_path)))
        self.materials_path = ""
    

def update_fbx_importer_path(self, context):
    filename = 'FBXImporter.exe'

    if self.fbx_importer_path == "":
        return
    elif self.fbx_importer_path == self.fbx_importer_path_before:
        return
    
    path = get_abs_path(self.fbx_importer_path)
    
    self.fbx_importer_path_before = verify_tool_path(self, context, path, "Custom FBX Importer", filename)
    self.fbx_importer_path = verify_tool_path(self, context, path, "Custom FBX Importer", filename)


def update_havok_path(self, context):
    filename = 'hctStandAloneFilterManager.exe'

    if self.havok_path == "":
        return
    elif self.havok_path == self.havok_path_before:
        return

    path = get_abs_path(self.havok_path)
    
    self.havok_path_before = verify_tool_path(self, context, path, "Havok Stand Alone Filter Manager", filename)
    self.havok_path = verify_tool_path(self, context, path, "Havok Stand Alone Filter Manager", filename)


def update_mwmb_path(self, context):
    name = str('MwmBuilder.exe')

    if self.mwmb_path == "":
        return
    elif self.mwmb_path == self.mwmb_path_before:
        return

    path = get_abs_path(self.mwmb_path)
    
    self.mwmb_path_before = verify_tool_path(self, context, path, "MWM Builder", name)
    self.mwmb_path = verify_tool_path(self, context, path, "MWM Builder", name)
    

class SEUT_AddonPreferences(AddonPreferences):
    """Saves the preferences set by the user"""
    bl_idname = __package__

    set_dev_paths: BoolProperty(
        name = "Set Dev Paths",
        description = "Set Dev Paths",
        default = False,
        update=update_set_dev_paths
    )
    materials_path: StringProperty(
        name="Materials Folder",
        description="This folder contains material information in the form of XML libraries as well as BLEND MatLibs",
        subtype='FILE_PATH',
        update=update_materials_path
    )
    fbx_importer_path: StringProperty(
        name="Custom FBX Importer",
        description="Despite its name, this tool is mainly used to export models to the FBX format",
        subtype='FILE_PATH',
        update=update_fbx_importer_path
    )
    fbx_importer_path_before: StringProperty(
        subtype='FILE_PATH'
    )
    havok_path: StringProperty(
        name="Havok Standalone Filter Manager",
        description="This tool is required to create Space Engineers collision models",
        subtype='FILE_PATH',
        update=update_havok_path
    )
    havok_path_before: StringProperty(
        subtype='FILE_PATH'
    )
    mwmb_path: StringProperty(
        name="MWM Builder",
        description="This tool converts the individual 'loose files' that the export yields into MWM files the game can read",
        subtype='FILE_PATH',
        update=update_mwmb_path
    )
    mwmb_path_before: StringProperty(
        subtype='FILE_PATH'
    )

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        current_version_name = 'v' + str(get_addon_version()).replace("(", "").replace(")", "").replace(", ", ".")

        split = layout.split(factor=0.95)
        split.label(text="")
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'reference'
        link.page = 'preferences'

        row = layout.row()
        row.label(text="Update Status:")

        if tuple(current_version_name[1:]) < tuple(wm.seut.latest_version[1:]):
            row.alert = True
            row.label(text=wm.seut.needs_update, icon='ERROR')
            row.operator('wm.get_update', icon='IMPORT')
        else:
            row.label(text=wm.seut.needs_update, icon='CHECKMARK')
            row.operator('wm.get_update', text="Releases", icon='IMPORT')

        layout.prop(self, "set_dev_paths", icon='FILEBROWSER')

        layout.prop(self, "materials_path", expand=True)
        box = layout.box()
        box.label(text="External Tools")
        box.prop(self, "mwmb_path", expand=True)
        box.prop(self, "fbx_importer_path", expand=True)
        box.prop(self, "havok_path", expand=True)


def verify_tool_path(self, context, path: str, name: str, filename: str) -> str:
    """Verifies the path of an external tool"""

    # If it's a directory but appending the name gives a valid path, do that. Else, error.
    if os.path.isdir(path):
        if os.path.exists(path + "\\" + filename):
            return path + "\\" + filename
        else:
            seut_report(self, context, 'ERROR', False, 'E030')
            return ""

    # If it's not a directory and the path doesn't exist, error. If the basename is equal to the name, use the path. If the basename is not equal, error.
    elif not os.path.isdir(path):
        if not os.path.exists(path):
            seut_report(self, context, 'ERROR', False, 'E003', name, path)
            return ""
        else:
            if os.path.basename(path) == filename:
                return path
            else:
                seut_report(self, context, 'ERROR', False, 'E013', name, filename, os.path.basename(path))
                return ""


def get_addon_version():
    return addon_version
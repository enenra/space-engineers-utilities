from enum import Enum
import bpy
import os

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty,
                        CollectionProperty
                        )

from .seut_errors   import seut_report, get_abs_path
from .seut_utils    import get_preferences


def update_BBox(self, context):
    bpy.ops.object.bbox('INVOKE_DEFAULT')


def update_simpleNavigationToggle(self, context):
    bpy.ops.wm.simple_navigation('INVOKE_DEFAULT')
    

def update_enabled(self, context):
    wm = context.window_manager
    preferences = get_preferences()
    materials_path = os.path.join(get_abs_path(preferences.asset_path), 'Materials')

    if preferences.asset_path == "":
        seut_report(self, context, 'ERROR', True, 'E012', "Asset Directory", get_abs_path(preferences.asset_path))
        return
    elif not os.path.isdir(materials_path):
        os.makedirs(materials_path, exist_ok=True)

    if self.enabled:
        with bpy.data.libraries.load(os.path.join(materials_path, self.name), link=True) as (data_from, data_to):
            data_to.materials = data_from.materials

    else:
        with bpy.data.libraries.load(os.path.join(materials_path, self.name), link=True) as (data_from, data_to):
            keep_img = []
            for mat in data_from.materials:
                material = bpy.data.materials[mat]

                if material.name in bpy.data.materials and material.library is not None and material.library.name == self.name:
                    bpy.data.materials.remove(material, do_unlink=True)

                elif material.name in bpy.data.materials and material.library is None:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and (node.label == 'CM' or node.label == 'ADD' or node.label == 'NG' or node.label == 'ALPHAMASK'):
                            keep_img.append(node.image.name)

            for img in data_from.images:
                if img in bpy.data.images and img is not None:
                    image = bpy.data.images[img]
                    if image.name in bpy.data.images and image.library is not None and image.library.name == self.name:
                        if image.name in keep_img:
                            image.make_local()
                        else:
                            bpy.data.images.remove(image, do_unlink=True)

            for ng in data_from.node_groups:
                node_group = bpy.data.node_groups[ng]
                if node_group.name in bpy.data.node_groups and node_group.library is not None and node_group.library.name == self.name:
                    bpy.data.node_groups.remove(node_group, do_unlink=True)


def update_texconv_preset(self, context):
    wm = context.window_manager

    if self.texconv_preset == 'icon':
        self.texconv_output_filetype = 'dds'
        self.texconv_input_filetype = 'png'
        self.texconv_format = 'BC7_UNORM_SRGB'
        self.texconv_pmalpha = True
        self.texconv_sepalpha = False
        self.texconv_pdd = False

    elif self.texconv_preset == 'cm':
        self.texconv_output_filetype = 'dds'
        self.texconv_input_filetype = 'tif'
        self.texconv_format = 'BC7_UNORM_SRGB'
        self.texconv_pmalpha = False
        self.texconv_sepalpha = True
        self.texconv_pdd = False

    elif self.texconv_preset == 'add':
        self.texconv_output_filetype = 'dds'
        self.texconv_input_filetype = 'tif'
        self.texconv_format = 'BC7_UNORM_SRGB'
        self.texconv_pmalpha = False
        self.texconv_sepalpha = True
        self.texconv_pdd = True

    elif self.texconv_preset == 'ng':
        self.texconv_output_filetype = 'dds'
        self.texconv_input_filetype = 'tif'
        self.texconv_format = 'BC7_UNORM'
        self.texconv_pmalpha = False
        self.texconv_sepalpha = True
        self.texconv_pdd = False

    elif self.texconv_preset == 'alphamask':
        self.texconv_output_filetype = 'dds'
        self.texconv_input_filetype = 'tif'
        self.texconv_format == 'BC7_UNORM'
        self.texconv_pmalpha == False
        self.texconv_sepalpha == False
        self.texconv_pdd == True

    elif self.texconv_preset == 'tif':
        self.texconv_output_filetype = 'tif'
        self.texconv_input_filetype = 'dds'
        self.texconv_format == 'NONE'
        self.texconv_pmalpha == False
        self.texconv_sepalpha == False
        self.texconv_pdd == False


def update_texconv_input_file(self, context):

    if self.texconv_input_file == "":
        return
    
    if not self.texconv_input_file.endswith(self.texconv_input_filetype) and not self.texconv_input_file.endswith(self.texconv_input_filetype.upper()):
        self.texconv_input_file = ""
        seut_report(self, context, 'ERROR', False, 'E015', 'Input', self.texconv_input_filetype)

class SEUT_IssueProperty(PropertyGroup):
    """Holder for issue information"""

    timestamp: FloatProperty(
        subtype='TIME',
        unit='TIME'
    )
    issue_type: EnumProperty(
        name='Info Type',
        items=(
            ('INFO', 'INFO', ''),
            ('WARNING', 'WARNING', ''),
            ('ERROR', 'ERROR', '')
            ),
        default='INFO'
    )
    text: StringProperty(
        name="Text"
    )
    code: StringProperty(
        name="Code"
    )
    reference: StringProperty(
        name="Reference Name"
    )


class SEUT_MatLibProps(PropertyGroup):
    """Holder for the various MatLib properties"""

    name: StringProperty(
        name="Name of MatLib"
    )
    enabled: BoolProperty(
        name="Enable or Disable MatLibs in the Materials folder",
        default=False,
        update=update_enabled
    )


class SEUT_WindowManager(PropertyGroup):
    """Holder for the various properties saved to the BLEND file"""

    version: IntProperty(
        name="SEUT WM Version",
        description="Used as a reference to patch the SEUT window manager properties to newer versions",
        default=0
    )

    simpleNavigationToggle: BoolProperty(
        name="Simple Navigation",
        description="Automatically sets all non-active collections to hidden",
        default=False,
        update=update_simpleNavigationToggle
    )

    better_fbx: BoolProperty(
        name = "Better FBX",
        description = "Whether SEUT should be using the Better FBX Importer",
        default = False
    )

    bBoxToggle: EnumProperty(
        name='Bounding Box',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_BBox
    )
    bboxColor: FloatVectorProperty(
        name="Color",
        description="The color of the Bounding Box",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.42, 0.827, 1, 0.3)
    )

    fix_scratched_materials: BoolProperty(
        name = "Fix Scratched Materials",
        description = "Numerous SDK models have a scratched paint material assigned to their bevels in the FBX but don't have them ingame. This switches those surfaces to the non-scratched material",
        default = True
    )

    # Materials
    matlibs: CollectionProperty(
        type=SEUT_MatLibProps
    )
    matlib_index: IntProperty(
        name="Enable or Disable MatLibs in the Materials folder",
        default=0
    )

    # Texture Conversion
    texconv_preset: EnumProperty(
        name="Preset",
        items=(
            ('icon', 'Icon', ''),
            ('cm', 'Color Metal', ''),
            ('add', 'Add Maps', ''),
            ('ng', 'Normal Gloss', ''),
            ('alphamask', 'Alphamask', ''),
            ('tif', 'TIF', ''),
            ('custom', 'Custom', '')
            ),
        default='custom',
        update=update_texconv_preset,
    )
    texconv_input_type: EnumProperty(
        name="Input Type",
        items=(
            ('file', 'File', ''),
            ('directory', 'Directory', '')
            ),
        default='directory',
    )
    texconv_input_dir: StringProperty(
        name="Input Directory",
        subtype="DIR_PATH",
    )
    texconv_input_file: StringProperty(
        name="Input File",
        subtype="FILE_PATH",
        update=update_texconv_input_file,
    )
    texconv_input_filetype: EnumProperty(
        name="Input Type",
        items=(
            ('dds', 'DDS', ''),
            ('png', 'PNG', ''),
            ('tif', 'TIF', '')
            ),
        default='tif',
    )
    texconv_output_dir: StringProperty(
        name="Output Folder",
        subtype="DIR_PATH",
    )
    texconv_output_filetype: EnumProperty(
        name="Output Type",
        items=(
            ('dds', 'DDS', ''),
            ('tif', 'TIF', '')
            ),
        default='dds',
    )
    texconv_format: EnumProperty(
        name="Format",
        items=(
            ('NONE', 'None', ''),
            ('BC7_UNORM', 'BC7_UNORM', ''),
            ('BC7_UNORM_SRGB', 'BC7_UNORM_SRGB', '')
            ),
        default='BC7_UNORM_SRGB',
    )
    texconv_pmalpha: BoolProperty(
        name="PM Alpha",
        description="Convert final texture to use premultiplied alpha",
        default=True,
    )
    texconv_sepalpha: BoolProperty(
        name="Separate Alpha",
        description="Resize / generate mips alpha channel separately from color channels",
        default=True,
    )
    texconv_pdd: BoolProperty(
        name="Point Dither Diffusion",
        default=False,
    )

    # Updater
    needs_update: BoolProperty(
        default = False
    )
    update_message: StringProperty(
        name="Update Message"
    )
    latest_version: StringProperty(
        name="Latest Version"
    )

    # Issues
    issues: CollectionProperty(
        type=SEUT_IssueProperty
    )
    issue_index: IntProperty(
        default=0
    )
    issue_alert: BoolProperty(
        default=False
    )
    display_errors: BoolProperty(
        name="Display Errors",
        description="Toggles whether errors are visible in the SEUT Notifications screen",
        default=True
    )
    display_warnings: BoolProperty(
        name="Display Warnings",
        description="Toggles whether warnings are visible in the SEUT Notifications screen",
        default=True
    )
    display_infos: BoolProperty(
        name="Display Infos",
        description="Toggles whether infos are visible in the SEUT Notifications screen",
        default=True
    )
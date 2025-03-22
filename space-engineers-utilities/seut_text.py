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

from .seut_errors                   import seut_report, get_abs_path
from .seut_utils                    import get_preferences, get_seut_blend_data, to_radians
from .animations.seut_animations    import SEUT_Animations


supported_image_types = ['DDS', 'TIF', 'TIFF', 'PNG', 'TGA']


def update_BBox(self, context):
    bpy.ops.object.bbox('INVOKE_DEFAULT')


def update_simple_navigation(self, context):
    bpy.ops.wm.simple_navigation('INVOKE_DEFAULT')


def update_texconv_preset(self, context):

    if self.texconv_preset != 'custom':
        presets = {
            'icon': {'o': 'dds', 'f': 'BC7_UNORM_SRGB', 'pmalpha': True, 'sepalpha': False, 'pdd': False},
            'cm': {'o': 'dds', 'f': 'BC7_UNORM_SRGB', 'pmalpha': False, 'sepalpha': True, 'pdd': False},
            'add': {'o': 'dds', 'f': 'BC7_UNORM_SRGB', 'pmalpha': False, 'sepalpha': True, 'pdd': True},
            'ng': {'o': 'dds', 'f': 'BC7_UNORM', 'pmalpha': False, 'sepalpha': True, 'pdd': False},
            'alphamask': {'o': 'dds', 'f': 'BC7_UNORM', 'pmalpha': False, 'sepalpha': False, 'pdd': True},
            'tif': {'o': 'tif', 'f': 'NONE', 'pmalpha': False, 'sepalpha': False, 'pdd': False},
            'tga': {'o': 'tga', 'f': 'NONE', 'pmalpha': False, 'sepalpha': False, 'pdd': False}
        }

        self.texconv_output_filetype = presets[self.texconv_preset]['o']
        self.texconv_format = presets[self.texconv_preset]['f']
        self.texconv_pmalpha = presets[self.texconv_preset]['pmalpha']
        self.texconv_sepalpha = presets[self.texconv_preset]['sepalpha']
        self.texconv_pdd = presets[self.texconv_preset]['pdd']


def update_texconv_input_file(self, context):
    if self.texconv_input_file == "":
        return
    if os.path.splitext(self.texconv_input_file)[1].upper()[1:] not in supported_image_types:
        self.texconv_input_file = ""
        seut_report(self, context, 'ERROR', False, 'E015', 'Input', "DDS', 'TIF', 'PNG' or 'TGA")


def update_animations_index(self, context):
    data = get_seut_blend_data()
    animation_set = data.seut.animations[data.seut.animations_index]

    for scn in bpy.data.scenes:
        scn.frame_current = 0
        scn.render.fps = 60
        for vl in scn.view_layers:
            vl.update()

    for sp in animation_set.subparts:
        if sp is None or sp.obj is None:
            continue
        if sp.obj.animation_data is None:
            sp.obj.animation_data_create()
        if sp.obj.animation_data.action is not sp.action:
            sp.obj.animation_data.action = sp.action

    for obj in bpy.data.objects:
        if obj is not None and obj.type == 'EMPTY' and obj.seut.linked and obj.seut.linkedScene is not None and obj.seut.linkedScene.name in bpy.data.scenes:
            for sp in animation_set.subparts:
                if sp.obj.seut.linkedScene == obj.seut.linkedScene:
                    if obj.animation_data is not None and obj.animation_data.action.name[:-4] in bpy.data.actions:
                        bpy.data.actions.remove(obj.animation_data.action)
                    obj.animation_data.action = sp.obj.animation_data.action
                    break


def update_qt_lod_view(self, context):
    scene = context.scene

    if self.qt_lod_view:
        active_obj = context.view_layer.objects.active
        col = context.view_layer.active_layer_collection.collection

        bpy.ops.object.add(type='EMPTY', location=(0.0, 0.0, 0.0), rotation=(to_radians(-20), 0.0, to_radians(45)))
        empty = bpy.context.view_layer.objects.active
        empty.name = 'LOD_VIEW_ANGLE'
        empty.empty_display_type = 'SPHERE'

        bpy.ops.object.camera_add(location=(0.0, -col.seut.lod_distance, 0.0), rotation=(to_radians(90), 0.0, 0.0))
        camera = bpy.context.view_layer.objects.active
        scene.camera = camera
        camera.parent = empty
        camera.name = 'LOD_VIEW'
        camera.data.name = 'LOD_VIEW'
        camera.data.angle = 1.22173

        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        context.view_layer.objects.active = active_obj

    else:
        if 'LOD_VIEW' in bpy.data.objects:
            camera = bpy.data.objects['LOD_VIEW']
            bpy.data.objects.remove(camera)
        if 'LOD_VIEW_ANGLE' in bpy.data.objects:
            empty = bpy.data.objects['LOD_VIEW_ANGLE']
            bpy.data.objects.remove(empty)


class SEUT_RepositoryProperty(PropertyGroup):
    """Holder for information about repositories and their status"""

    name: StringProperty()
    text_name: StringProperty()
    git_url: StringProperty()
    cfg_path: StringProperty()
    needs_update: BoolProperty(
        default=False
    )
    update_message: StringProperty()
    current_version: StringProperty()
    latest_version: StringProperty()
    last_check: FloatProperty(
        subtype='TIME',
        unit='TIME',
        default=0.0
    )
    cache_releases: StringProperty()
    cache_tags: StringProperty()
    dev_mode: BoolProperty(
        default=False
    )
    dev_tag: StringProperty()
    dev_version: IntProperty()


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


class SEUT_Text(PropertyGroup):
    """Holder for the various properties saved to the BLEND file"""

    version: IntProperty(
        name="SEUT Text Data Holder Version",
        description="Used as a reference to patch the SEUT blend data properties to newer versions",
        default=0 # current: 1
    )

    simple_navigation: BoolProperty(
        name="Simple Navigation",
        description="Automatically sets all non-active collections to hidden",
        default=False,
        update=update_simple_navigation
    )

    convert_textures: BoolProperty(
        name = "Convert Textures",
        description = "Whether SEUT should convert textures to DDS and place them in the mod directory as needed",
        default = True
    )

    remap_all: BoolProperty(
        name = "Remap All Scenes",
        description = "Whether to run remap materials on all objects in all scenes or only the current scene",
        default = False
    )

    bBox: EnumProperty(
        name='Bounding Box',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_BBox
    )
    bBox_color: FloatVectorProperty(
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

    use_alt_importer: BoolProperty(
        name = "Use Alternate Importer",
        description = "Whether SEUT should use the alternative importer that works better on newer models (also applies for Complete Import)",
        default = False
    )

    # Texture Conversion
    setup_conversion_filetype: EnumProperty(
        name="Output Type",
        description="The filetype to convert the game's 'DDS'-Textures to for Blender to read.",
        items=(
            ('tif', 'TIF', ''),
            ('tga', 'TGA', ''),
            ('png', 'PNG', '')
            ),
        default='tif',
    )
    texconv_preset: EnumProperty(
        name="Preset",
        items=(
            ('icon', 'Icon', ''),
            ('cm', 'Color Metal', ''),
            ('add', 'Add Maps', ''),
            ('ng', 'Normal Gloss', ''),
            ('alphamask', 'Alphamask', ''),
            ('tif', 'TIF', ''),
            ('tga', 'TGA', ''),
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
    texconv_output_dir: StringProperty(
        name="Output Folder",
        subtype="DIR_PATH",
    )
    texconv_output_filetype: EnumProperty(
        name="Output Type",
        items=(
            ('dds', 'DDS', ''),
            ('tif', 'TIF', ''),
            ('tga', 'TGA', ''),
            ('png', 'PNG', '')
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
    repos: CollectionProperty(
        type=SEUT_RepositoryProperty
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

    # Animations
    animations: CollectionProperty(
        type = SEUT_Animations
    )
    animations_index: IntProperty(
        default = 0,
        update = update_animations_index
    )

    # QuickTools
    qt_lod_view: BoolProperty(
        name="LOD Distance View",
        description="Visualizes the distance set for the active LOD collection",
        default=False,
        update=update_qt_lod_view
    )
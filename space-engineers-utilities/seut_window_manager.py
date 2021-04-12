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
    materials_path = get_abs_path(preferences.materials_path)

    if preferences.materials_path == "" or os.path.isdir(materials_path) == False:
        seut_report(self, context, 'ERROR', True, 'E012', "Materials Folder", materials_path)
        return

    if self.enabled:
        with bpy.data.libraries.load(materials_path + "\\" + self.name, link=True) as (data_from, data_to):
            data_to.materials = data_from.materials

    else:
        with bpy.data.libraries.load(materials_path + "\\" + self.name, link=True) as (data_from, data_to):
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
                if img in bpy.data.images:
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
        subtype='COLOR',
        default=(0.42, 0.827, 1),
        update=update_BBox
    )
    bboxTransparency: FloatProperty(
        name="Transparency",
        description="The transparency of the Bounding Box",
        default=0.3,
        max=1,
        min=0,
        step=10.0,
        update=update_BBox
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
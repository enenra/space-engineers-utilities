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

from .seut_errors  import showError


def update_BBox(self, context):
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_simpleNavigationToggle(self, context):
    bpy.ops.scene.simple_navigation('INVOKE_DEFAULT')
    

def update_enabled(self, context):
    wm = context.window_manager

    addon = __package__
    preferences = bpy.context.preferences.addons.get(addon).preferences
    materialsPath = os.path.abspath(bpy.path.abspath(preferences.materialsPath))

    if preferences.materialsPath == "" or preferences.materialsPath == "." or os.path.isdir(materialsPath) == False:
        showError(context, "Report: Error", "SEUT Error: Path to Materials Folder (Addon Preferences) '" + materialsPath + "' not valid. (017)")
        return

    if self.enabled:
        with bpy.data.libraries.load(materialsPath + "\\" + self.name, link=True) as (data_from, data_to):
            data_to.materials=data_from.materials

    else:
        with bpy.data.libraries.load(materialsPath + "\\" + self.name, link=True) as (data_from, data_to):
                for mat in data_from.materials:
                    if mat in bpy.data.materials and bpy.data.materials[mat].library is not None and bpy.data.materials[mat].library.name == self.name:
                        bpy.data.materials.remove(bpy.data.materials[mat], do_unlink=True)
                for img in data_from.images:
                    if img in bpy.data.images and bpy.data.images[img].library is not None and bpy.data.images[img].library.name == self.name:
                        bpy.data.images.remove(bpy.data.images[img], do_unlink=True)
                for ngroup in data_from.node_groups:
                    if ngroup in bpy.data.node_groups and bpy.data.node_groups[ngroup].library is not None and bpy.data.node_groups[ngroup].library.name == self.name:
                        bpy.data.node_groups.remove(bpy.data.node_groups[ngroup], do_unlink=True)
                        

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
      
    # Mountpoints
    mountpointSide: EnumProperty(
    name='Side',
    items=(
        ('front', 'Front', ''),
        ('back', 'Back', ''),
        ('left', 'Left', ''),
        ('right', 'Right', ''),
        ('top', 'Top', ''),
        ('bottom', 'Bottom', '')
        ),
    default='front'
    )
    
    # Materials
    matPreset: EnumProperty(
        name='Preset',
        description="Select a nodetree preset for your material",
        items=(
            ('SMAT_Preset_Full', 'Full', '[X] CM\n[X] Emissive\n[X] ADD\n[X] NG\n[X] Alpha'),
            ('SMAT_Preset_Full_NoEmissive', 'No Emissive', '[X] CM\n[_] Emissive\n[X] ADD\n[X] NG\n[X] Alpha'),
            ('SMAT_Preset_Full_NoADD', 'Full, No ADD', '[X] CM\n[_] Emissive\n[_] ADD\n[X] NG\n[X] Alpha'),
            ('SMAT_Preset_NoAlpha', 'No Alpha', '[X] CM\n[X] Emissive\n[X] ADD\n[X] NG\n[_] Alpha'),
            ('SMAT_Preset_NoAlpha_NoEmissive', 'No Alpha, No Emissive', '[X] CM\n[_] Emissive\n[X] ADD\n[X] NG\n[_] Alpha'),
            ('SMAT_Preset_NoADD', 'No ADD', '[X] CM\n[_] Emissive\n[_] ADD\n[X] NG\n[_] Alpha'),
            ('SMAT_Preset_NoCM_NoADD', 'No CM, No ADD', '[_] CM\n[_] Emissive\n[_] ADD\n[X] NG\n[X] Alpha')
            ),
        default='SMAT_Preset_Full'
    )
    matlibs: CollectionProperty(
        type=SEUT_MatLibProps
    )
    matlib_index: IntProperty(
        name="Enable or Disable MatLibs in the Materials folder",
        default=0
    )

    # Errors
    errorText: StringProperty(
        name="Error"
    )
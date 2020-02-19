import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty
                        )


def update_BBox(self, context):
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_simpleNavigationToggle(self, context):
    bpy.ops.scene.simple_navigation('INVOKE_DEFAULT')
    

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

    # Errors
    errorText: StringProperty(
        name="Error"
    )
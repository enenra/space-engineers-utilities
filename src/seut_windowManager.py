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
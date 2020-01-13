import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        IntProperty,
                        StringProperty)

class SEUT_Materials(PropertyGroup):
    technique: bpy.props.EnumProperty(
        name='Technique',
        description="",
        items=(
            ('MESH', 'MESH', ''),
            ('DECAL', 'DECAL', ''),
            ('DECAL_CUTOUT', 'DECAL_CUTOUT', ''),
            ('GLASS', 'GLASS', ''),
            ('ALPHA_MASKED', 'ALPHA_MASKED', ''),
            ('HOLO', 'HOLO', '')
            ),
        default='MESH'
    )
    specularIntensity: FloatProperty(
        name="Intensity:",
        description="",
        default=0,
        min=0,
        max=1
    )
    specularPower: FloatProperty(
        name="Power:",
        description="",
        default=0,
        min=0,
        max=1
    )
    diffuseColorX: IntProperty(
        name="Color X:",
        description="",
        default=0,
        min=0,
        max=255
    )
    diffuseColorY: IntProperty(
        name="Color Y:",
        description="",
        default=0,
        min=0,
        max=255
    )
    diffuseColorZ: IntProperty(
        name="Color Z:",
        description="",
        default=0,
        min=0,
        max=255
    )
    diffuseTexture: StringProperty(
        name="Diffuse Texture:",
        description="",
        subtype="FILE_PATH"
    )
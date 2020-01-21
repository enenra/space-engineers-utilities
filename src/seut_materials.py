import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty)

class SEUT_Materials(PropertyGroup):
    
    overrideMatLib: BoolProperty(
        name="Override MatLib",
        description="Whether the material should replace its MatLib counterpart during export of this file (non-destructively)",
        default=False
    )
    technique: EnumProperty(
        name='Technique',
        description="The technique with which the material is rendered ingame",
        items=(
            ('MESH', 'MESH', 'The standard technique'),
            ('DECAL', 'DECAL', ''),
            ('DECAL_CUTOUT', 'DECAL_CUTOUT', ''),
            ('GLASS', 'GLASS', 'Transparent material - requires additional values to be set'),
            ('ALPHA_MASKED', 'ALPHA_MASKED', 'Has an alphamask texture'),
            ('HOLO', 'HOLO', 'Transparent LCD screen texture')
            ),
        default='MESH'
    )
    specularIntensity: FloatProperty(
        name="Intensity:",
        description="Determines the intensity of the transparent material's specularity",
        default=0,
        min=0,
        max=100
    )
    specularPower: FloatProperty(
        name="Power:",
        description="Determines the power of the transparent material's specularity",
        default=0,
        min=0,
        max=100
    )
    diffuseColor: FloatVectorProperty(
        name="Color",
        description="The color of the tint when looking through this transparent material",
        subtype='COLOR',
        default=(0, 0, 0)
    )

    diffuseTexture: StringProperty(
        name="Diffuse Texture:",
        description="",
        subtype="FILE_PATH",
        default=""
    )

    nodeLinkedToOutputName: StringProperty(
        name="Node Linked to Output",
        default=""
    )

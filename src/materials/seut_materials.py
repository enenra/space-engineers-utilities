import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty)

class SEUT_Materials(PropertyGroup):
    """Holder for the varios material properties"""
    
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
            ('DECAL', 'DECAL', "Makes the material look like it's part of the model behind it"),
            ('DECAL_NOPREMULT', 'DECAL_NOPREMULT', "Higher accuracy of transparency than 'DECAL', but same visual style"),
            ('DECAL_CUTOUT', 'DECAL_CUTOUT', "Makes the material look like it cuts into the model behind it"),
            ('GLASS', 'GLASS', 'Transparent material - requires additional values to be set in TransparentMaterials.sbc'),
            ('ALPHA_MASKED', 'ALPHA_MASKED', 'Has an alphamask texture'),
            ('SHIELD', 'SHIELD', 'Animated material used on SafeZone shield - currently limited to default one'),
            ('HOLO', 'HOLO', 'Transparent LCD screen texture')
            ),
        default='MESH'
    )
    facing: EnumProperty(
        name='Facing',
        description="The facing mode of the material",
        items=(
            ('None', 'None', 'No facing mode (standard)'),
            ('Vertical', 'Vertical', 'Vertical facing mode'),
            ('Full', 'Full', 'Full facing mode'),
            ('Impostor', 'Imposter', 'Imposter facing mode')
            ),
        default='None'
    )
    windScale: FloatProperty(
        name="Wind Scale:",
        description="Only relevant for trees and bushes",
        default=0,
        min=0,
        max=1
    )
    windFrequency: FloatProperty(
        name="Wind Frequency:",
        description="Only relevant for trees and bushes",
        default=0,
        min=0,
        max=100
    )

    nodeLinkedToOutputName: StringProperty(
        name="Node Linked to Output",
        default=""
    )

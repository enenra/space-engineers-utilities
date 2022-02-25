import bpy
import os

from collections import OrderedDict

from bpy.types  import UIList
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

from ..seut_preferences     import particles


class SEUT_ParticlePropertyKeys(PropertyGroup):
    """Holder for the various Particle Generation Property Keys"""

    time: FloatProperty(
        name="Time"
    )
    value_bool: BoolProperty(
        name="ValueBool"
    )
    value_int: IntProperty(
        name="ValueInt"
    )
    value_float: FloatProperty(
        name="ValueFloat"
    )
    value_string: StringProperty(
        name="ValueString"
    )
    value_vector_3: FloatVectorProperty(
        name="ValueVector3",
        description="TBD",
        subtype='XYZ'
    )
    value_vector_4: FloatVectorProperty(
        name="ValueVector4",
        description="TBD",
        subtype='COLOR_GAMMA'
    )


class SEUT_ParticlePropertyValue2D(PropertyGroup):
    """Holder for the various Particle Generation Property Keys"""

    time: FloatProperty(
        name="Time"
    )
    value_bool: BoolProperty(
        name="ValueBool"
    )
    value_int: IntProperty(
        name="ValueInt"
    )
    value_float: FloatProperty(
        name="ValueFloat"
    )
    value_string: StringProperty(
        name="ValueString"
    )
    value_vector_3: FloatVectorProperty(
        name="ValueVector3",
        description="TBD",
        subtype='XYZ'
    )
    value_vector_4: FloatVectorProperty(
        name="ValueVector4",
        description="TBD",
        subtype='COLOR_GAMMA'
    )
    
    keys: CollectionProperty(
        type=SEUT_ParticlePropertyKeys
    )
    keys_index: IntProperty(
        name="Values 2D Index",
        default=0
    )


def items_properties(context, scene):

    items = []
    for key, entry in particles['properties'].items():   # NOTE: This will error after a reload of the addon.
        items.append((key, entry['name'], entry['description']))
    
    return items


def update_property_name(self, context):
    self.name = self.name_internal
    self.prop_animation_type = properties[self.name]['animation_type']
    self.prop_type = properties[self.name]['type']


class SEUT_ParticleProperty(PropertyGroup):
    """Holder for the various Particle Generation properties"""

    name: StringProperty(
        name="Name"
    )
    # There's some wonkyness when using an enum as the name so instead they're just connected.
    # Switch this to dynamically use the list below. This one is out of date.
    name_internal: EnumProperty(
        name="Name",
        description="The name of the property",
        items=items_properties,
        update=update_property_name
    )
    prop_animation_type: EnumProperty(
        name="AnimationType",
        description="TBD",
        items=(
            ('Const', 'Constant', 'TBD'),
            ('Animated', 'Animated', 'TBD'),
            ('Animated2D', 'Animated2D', 'TBD')
            ),
        default='Const'
    )
    prop_type: EnumProperty(
        name="Type",
        description="TBD",
        items=(
            ('Bool', 'Bool', 'TBD'),
            ('Int', 'Int', 'TBD'),
            ('Float', 'Float', 'TBD'),
            ('Vector3', 'Vector3', 'TBD'),
            ('Vector4', 'Vector4', 'TBD'),
            ('MyTransparentMaterial', 'MyTransparentMaterial', 'TBD')
            ),
        default='Bool'
    )

    value_bool: BoolProperty(
        name="ValueBool"
    )
    value_int: IntProperty(
        name="ValueInt"
    )
    value_float: FloatProperty(
        name="ValueFloat"
    )
    value_string: StringProperty(
        name="ValueString"
    )
    value_vector_3: FloatVectorProperty(
        name="ValueVector3",
        description="TBD",
        subtype='XYZ'
    )
    value_vector_4: FloatVectorProperty(
        name="ValueVector4",
        description="TBD",
        subtype='COLOR_GAMMA'
    )

    keys: CollectionProperty(
        type=SEUT_ParticlePropertyValue2D
    )
    keys_index: IntProperty(
        name="Values 2D Index",
        default=0
    )


class SEUT_ParticleSettings(PropertyGroup):
    """Holder for the various particle generation properties"""
    
    properties: CollectionProperty(
        type=SEUT_ParticleProperty
    )
    properties_index: IntProperty(
        name="Properties Index",
        default=0
    )


class SEUT_UL_ParticleProperties(UIList):
    """Creates the Particle Properties UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=item.name, icon='PROPERTIES')

    def invoke(self, context, event):
        pass


class SEUT_UL_ParticlePropertyValues2D(UIList):
    """Creates the Particle Properties UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=item.name, icon='PROPERTIES')

    def invoke(self, context, event):
        pass
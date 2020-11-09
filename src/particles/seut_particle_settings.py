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
    value_2d: CollectionProperty(
        type=SEUT_ParticlePropertyKeys
    )


def update_property_name(self, context):
    self.name = self.name_internal
    self.prop_animation_type = name_animationType[self.name]
    self.prop_type = name_type[self.name]


class SEUT_ParticleProperty(PropertyGroup):
    """Holder for the various Particle Generation properties"""

    name: StringProperty(
        name="Name"
    )
    # There's some wonkyness when using an enum as the name so instead they're just connected.
    name_internal: EnumProperty(
        name="Name",
        description="The name of the property",
        items=(
            ('Array size', 'Array Size', 'The size of the texture atlas used by this particle'),
            ('Array offset', 'Array Offset', 'The first frame on the atlas to use, with top left being 1'),
            ('Array modulo', 'Array Modulo', 'The amount of frames to be played'),
            ('Color', 'Color', 'The color of the particle (applied over its material)'),
            ('Color intensity', 'Color Intensity', 'The color intensity of the particle'),
            ('Bounciness', 'Bounciness', 'How strongly the particle bounces off of surfaces'),
            ('Emitter size', 'Emitter Size', 'The size of the area in which particles are spawned'),
            ('Emitter inner size', 'Emitter Inner Size', 'The size of the exclusion zone within the area in which particles are spawned'),
            ('Direction', 'Direction', 'The direction to which particles will align.\nNote: (0,0,0) disables the particle'),
            ('Velocity', 'Velocity', 'The velocity of the particle on an axis'),
            ('Velocity var', 'Velocity Variation', 'The value by which the velocity of the particle varies randomly'),
            ('Direction inner cone', 'Direction Inner Cone', 'The direction of the inner particle emitter'),
            ('Direction cone', 'Direction Cone', 'The direction of the outer particle emitter'),
            ('Acceleration', 'Acceleration', 'The acceleration of the particle from the emitter'),
            ('Acceleration factor [m/s^2]', 'Acceleration Factor [m/s^2]', 'The factor by which the acceleration of the particle changes over time'),
            ('Rotation velocity', 'Rotation Velocity', 'The speed of the particle rotation on the Z axis'),
            ('Radius', 'Radius', 'The radius / scale of the particle'),
            ('Life', 'Life', 'The duration of the individual particle'),
            ('Soft particle distance scale', 'Soft Particle Distance Scale', 'UNKNOWN'),
            ('Streak multiplier', 'Streak Multiplier', 'The amount of trails per particle'),
            ('Animation frame time', 'Animation Frame Time', 'The time each frame is displayed per loop'),
            ('Enabled', 'Enabled', 'Whether the effect is enabled or disabled'),
            ('Particles per second', 'Particles Per Second', 'How many particles are spawned per second'),
            ('Material', 'Material', 'The reference to the TransparentMaterials.sbc entry of the texture'),
            ('OIT weight factor', 'OIT Weight Factor', '(TBI) Likely smooths the transitions between frames of the particle'),
            ('Collide', 'Collide', 'Whether the particle collides with objects'),
            ('SleepState', 'Sleep State', 'UNKNOWN'),
            ('Light', 'Light', 'Whether the particle is a light source'),
            ('VolumetricLight', 'Volumetric Light', 'Whether the particle emits volumetric light (casts shadows)'),
            ('Target coverage', 'Target Coverage', 'UNKNOWN'),
            ('Gravity', 'Gravity', 'How strongly the particle is affected by gravity'),
            ('Offset', 'Offset', 'The offset of the particle from the emitter location'),
            ('Rotation velocity var', 'Rotation Velocity Variation', 'The value by which the rotation velocity of the particle varies randomly'),
            ('Hue var', 'Hue Variation', 'The value by which the color hue of the particle varies randomly'),
            ('Rotation enabled', 'Rotation Enabled', 'Whether the particle can rotate separately from the object it is attached to'),
            ('Motion inheritance', 'Motion Inheritance', 'The degree to which the particle inherits motion from the object it is attached to'),
            ('Life var', 'Life Variation', 'The value by which the life of the particle varies randomly'),
            ('Streaks', 'Streaks', 'Whether the particle has a trail'),
            ('Rotation reference', 'Rotation Reference', 'TBD'),
            ('Angle', 'Angle', 'The rotation difference to the reference object on which the particle is rotated'),
            ('Angle var', 'Angle Variation', 'The value by which the angle of the particle varies randomly'),
            ('Thickness', 'Thickness', 'Determines the width of the particle'),
            ('Particles per frame', 'Particles Per Frame', 'The amount of particle instances displayed per frame'),
            ('Camera bias', 'Camera Bias', 'The distance to the view point of observing players that the particle is more likely to spawn in'),
            ('Emissivity', 'Emissivity', 'The degree to which the particle is emissive'),
            ('Shadow alpha multiplier', 'Shadow Alpha Multiplier', 'UNKNOWN'),
            ('Use Emissivity Channel', 'Use Emissivity Channel', 'Whether the particle uses the emissivity channel in the texture'),
            ('Use Alpha Anisotropy', 'Use Alpha Anisotropy', 'UNKNOWN'),
            ('Ambient light factor', 'Ambient Light Factor', 'UNKNOWN'),
            ('Radius var', 'Radius Variation', 'The degree to which the particle\'s radius varies randomly'),
            ('Rotation velocity collision multiplier', 'Rotation Velocity Collision Multiplier', 'The multiplier for the rotation speed of the particle after colliding with an object'),
            ('Collision count to kill particle', 'Collision Count To Kill Particle', 'The amount of times the particles can collide with an object before it disappears'),
            ('Distance scaling factor', 'Distance Scaling Factor', 'The factor by which the particle is scaled at a distance'),
            ('Motion interpolation', 'Motion Interpolation', 'UNKNOWN')
            ),
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


class SEUT_ParticleSettings(PropertyGroup):
    """Holder for the various particle generation properties"""
    
    properties: CollectionProperty(
        type=SEUT_ParticleProperty
    )
    properties_index: IntProperty(
        name="Properties Index",
        default=0
    )


name_animationType = OrderedDict([
    ('Array size', 'Const'),
    ('Array offset', 'Const'),
    ('Array modulo', 'Const'),
    ('Color', 'Animated2D'),
    ('Color intensity', 'Animated2D'),
    ('Bounciness', 'Const'),
    ('Emitter size', 'Animated'),
    ('Emitter inner size', 'Animated'),
    ('Direction', 'Const'),
    ('Velocity', 'Animated'),
    ('Velocity var', 'Animated'),
    ('Direction inner cone', 'Animated'),
    ('Direction cone', 'Animated'),
    ('Acceleration', 'Const'),
    ('Acceleration factor [m/s^2]', 'Animated2D'),
    ('Rotation velocity', 'Const'),
    ('Radius', 'Animated2D'),
    ('Life', 'Const'),
    ('Soft particle distance scale', 'Const'),
    ('Streak multiplier', 'Const'),
    ('Animation frame time', 'Const'),
    ('Enabled', 'Const'),
    ('Particles per second', 'Animated'),
    ('Material', 'Const'),
    ('OIT weight factor', 'Const'),
    ('Collide', 'Const'),
    ('SleepState', 'Const'),
    ('Light', 'Const'),
    ('VolumetricLight', 'Const'),
    ('Target coverage', 'Const'),
    ('Gravity', 'Const'),
    ('Offset', 'Const'),
    ('Rotation velocity var', 'Const'),
    ('Hue var', 'Const'),
    ('Rotation enabled', 'Const'),
    ('Motion inheritance', 'Const'),
    ('Life var', 'Const'),
    ('Streaks', 'Const'),
    ('Rotation reference', 'Const'),
    ('Angle', 'Const'),
    ('Angle var', 'Const'),
    ('Thickness', 'Animated2D'),
    ('Particles per frame', 'Animated'),
    ('Camera bias', 'Const'),
    ('Emissivity', 'Animated2D'),
    ('Shadow alpha multiplier', 'Const'),
    ('Use Emissivity Channel', 'Const'),
    ('Use Alpha Anisotropy', 'Const'),
    ('Ambient light factor', 'Const'),
    ('Radius var', 'Const'),
    ('Rotation velocity collision multiplier', 'Const'),
    ('Collision count to kill particle', 'Const'),
    ('Distance scaling factor', 'Const'),
    ('Motion interpolation', 'Const'),
])

name_type = OrderedDict([
    ('Array size', 'Vector3'),
    ('Array offset', 'Int'),
    ('Array modulo', 'Int'),
    ('Color', 'Vector4'),
    ('Color intensity', 'Float'),
    ('Bounciness', 'Float'),
    ('Emitter size', 'Vector3'),
    ('Emitter inner size', 'Float'),
    ('Direction', 'Vector3'),
    ('Velocity', 'Float'),
    ('Velocity var', 'Float'),
    ('Direction inner cone', 'Float'),
    ('Direction cone', 'Float'),
    ('Acceleration', 'Vector3'),
    ('Acceleration factor [m/s^2]', 'Float'),
    ('Rotation velocity', 'Float'),
    ('Radius', 'Float'),
    ('Life', 'Float'),
    ('Soft particle distance scale', 'Float'),
    ('Streak multiplier', 'Float'),
    ('Animation frame time', 'Float'),
    ('Enabled', 'Bool'),
    ('Particles per second', 'Float'),
    ('Material', 'MyTransparentMaterial'),
    ('OIT weight factor', 'Float'),
    ('Collide', 'Bool'),
    ('SleepState', 'Bool'),
    ('Light', 'Bool'),
    ('VolumetricLight', 'Bool'),
    ('Target coverage', 'Float'),
    ('Gravity', 'Float'),
    ('Offset', 'Vector3'),
    ('Rotation velocity var', 'Float'),
    ('Hue var', 'Float'),
    ('Rotation enabled', 'Bool'),
    ('Motion inheritance', 'Float'),
    ('Life var', 'Float'),
    ('Streaks', 'Bool'),
    ('Rotation reference', 'Int'),
    ('Angle', 'Vector3'),
    ('Angle var', 'Vector3'),
    ('Thickness', 'Float'),
    ('Particles per frame', 'Float'),
    ('Camera bias', 'Float'),
    ('Emissivity', 'Float'),
    ('Shadow alpha multiplier', 'Float'),
    ('Use Emissivity Channel', 'Bool'),
    ('Use Alpha Anisotropy', 'Bool'),
    ('Ambient light factor', 'Float'),
    ('Radius var', 'Float'),
    ('Rotation velocity collision multiplier', 'Float'),
    ('Collision count to kill particle', 'Int'),
    ('Distance scaling factor', 'Float'),
    ('Motion interpolation', 'Bool'),
])


class SEUT_UL_ParticleProperties(UIList):
    """Creates the Particle Properties UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=item.name, icon='PROPERTIES')

    def invoke(self, context, event):
        pass
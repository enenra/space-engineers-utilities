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
    self.prop_animation_type = properties[self.name]['animation_type']
    self.prop_type = properties[self.name]['type']


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
            ('Collision count to kill particle', 'Collision Count To Kill Particle', 'The amount of times the particle can collide with an object before it disappears'),
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


properties = {
    'Array size': {'name': 'Array Size', 'description': "The size of the texture atlas used by this particle.", 'animation_type': 'Const', 'type': 'Vector3'},
    'Array offset': {'name': 'Array Offset', 'description': "The first frame on the atlas to use, with top left being 1.", 'animation_type': 'Const', 'type': 'Int'},
    'Array modulo': {'name': 'Array Modulo', 'description': "The amount of frames to be played.", 'animation_type': 'Const', 'type': 'Int'},
    'Color': {'name': 'Color', 'description': "The color of the particle (applied over its material).", 'animation_type': 'Animated2D', 'type': 'Vector4'},
    'Color intensity': {'name': 'Color Intensity', 'description': "The color intensity of the particle.", 'animation_type': 'Animated2D', 'type': 'Float'},
    'Bounciness': {'name': 'Bounciness', 'description': "How strongly the particle bounces off of surfaces.", 'animation_type': 'Const', 'type': 'Float'},
    'Emitter size': {'name': 'Emitter Size', 'description': "The size of the area in which particles are spawned.", 'animation_type': 'Animated', 'type': 'Vector3'},
    'Emitter inner size': {'name': 'Emitter Inner Size', 'description': "The size of the exclusion zone within the area in which particles are spawned.", 'animation_type': 'Animated', 'type': 'Float'},
    'Direction': {'name': 'Direction', 'description': "The direction to which particles will align.\nNote: (0,0,0) disables the particle.", 'animation_type': 'Const', 'type': 'Vector3'},
    'Velocity': {'name': 'Velocity', 'description': "The velocity of the particle on an axis.", 'animation_type': 'Animated', 'type': 'Float'},
    'Velocity var': {'name': 'Velocity Variation', 'description': "The value by which the velocity of the particle varies randomly.", 'animation_type': 'Animated', 'type': 'Float'},
    'Direction inner cone': {'name': 'Direction Inner Cone', 'description': "The direction of the inner particle emitter.", 'animation_type': 'Animated', 'type': 'Float'},
    'Direction cone': {'name': 'Direction Cone', 'description': "The direction of the outer particle emitter.", 'animation_type': 'Animated', 'type': 'Float'},
    'Acceleration': {'name': 'Acceleration', 'description': "The acceleration of the particle from the emitter.", 'animation_type': 'Const', 'type': 'Vector3'},
    'Acceleration factor [m/s^2]': {'name': 'Acceleration Factor [m/s^2]', 'description': "The factor by which the acceleration of the particle changes over time.", 'animation_type': 'Animated2D', 'type': 'Float'},
    'Rotation velocity': {'name': 'Rotation Velocity', 'description': "The speed of the particle rotation on the Z axis.", 'animation_type': 'Const', 'type': 'Float'},
    'Radius': {'name': 'Radius', 'description': "The radius / scale of the particle.", 'animation_type': 'Animated2D', 'type': 'Float'},
    'Life': {'name': 'Life', 'description': "The duration of the individual particle.", 'animation_type': 'Const', 'type': 'Float'},
    'Soft particle distance scale': {'name': 'Soft Particle Distance Scale', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Float'},
    'Streak multiplier': {'name': 'Streak Multiplier', 'description': "The amount of trails per particle.", 'animation_type': 'Const', 'type': 'Float'},
    'Animation frame time': {'name': 'Animation Frame Time', 'description': "The time each frame is displayed per loop.", 'animation_type': 'Const', 'type': 'Float'},
    'Enabled': {'name': 'Enabled', 'description': "Whether the effect is enabled or disabled.", 'animation_type': 'Const', 'type': 'Bool'},
    'Particles per second': {'name': 'Particles Per Second', 'description': "How many particles are spawned per second.", 'animation_type': 'Animated', 'type': 'Float'},
    'Material': {'name': 'Material', 'description': "The reference to the TransparentMaterials.sbc entry of the texture.", 'animation_type': 'Const', 'type': 'MyTransparentMaterial'},
    'OIT weight factor': {'name': 'OIT Weight Factor', 'description': "(TBI) Likely smooths the transitions between frames of the particle.", 'animation_type': 'Const', 'type': 'Float'},
    'Collide': {'name': 'Collide', 'description': "Whether the particle collides with objects.", 'animation_type': 'Const', 'type': 'Bool'},
    'SleepState': {'name': 'Sleep State', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Bool'},
    'Light': {'name': 'Light', 'description': "Whether the particle is a light source.", 'animation_type': 'Const', 'type': 'Bool'},
    'VolumetricLight': {'name': 'Volumetric Light', 'description': "Whether the particle emits volumetric light (casts shadows).", 'animation_type': 'Const', 'type': 'Bool'},
    'Target coverage': {'name': 'Target Coverage', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Float'},
    'Gravity': {'name': 'Gravity', 'description': "How strongly the particle is affected by gravity.", 'animation_type': 'Const', 'type': 'Float'},
    'Offset': {'name': 'Offset', 'description': "The offset of the particle from the emitter location.", 'animation_type': 'Const', 'type': 'Vector3'},
    'Rotation velocity var': {'name': 'Rotation Velocity Variation', 'description': "The value by which the rotation velocity of the particle varies randomly.", 'animation_type': 'Const', 'type': 'Float'},
    'Hue var': {'name': 'Hue Variation', 'description': "The value by which the color hue of the particle varies randomly.", 'animation_type': 'Const', 'type': 'Float'},
    'Rotation enabled': {'name': 'Rotation Enabled', 'description': "Whether the particle can rotate separately from the object it is attached to.", 'animation_type': 'Const', 'type': 'Bool'},
    'Motion inheritance': {'name': 'Motion Inheritance', 'description': "The degree to which the particle inherits motion from the object it is attached to.", 'animation_type': 'Const', 'type': 'Float'},
    'Life var': {'name': 'Life Variation', 'description': "The value by which the life of the particle varies randomly.", 'animation_type': 'Const', 'type': 'Float'},
    'Streaks': {'name': 'Streaks', 'description': "Whether the particle has a trail.", 'animation_type': 'Const', 'type': 'Bool'},
    'Rotation reference': {'name': 'Rotation Reference', 'description': "TBD.", 'animation_type': 'Const', 'type': 'Int'},
    'Angle': {'name': 'Angle', 'description': "The rotation difference to the reference object on which the particle is rotated.", 'animation_type': 'Const', 'type': 'Vector3'},
    'Angle var': {'name': 'Angle Variation', 'description': "The value by which the angle of the particle varies randomly.", 'animation_type': 'Const', 'type': 'Vector3'},
    'Thickness': {'name': 'Thickness', 'description': "Determines the width of the particle.", 'animation_type': 'Animated2D', 'type': 'Float'},
    'Particles per frame': {'name': 'Particles Per Frame', 'description': "The amount of particle instances displayed per frame.", 'animation_type': 'Animated', 'type': 'Float'},
    'Camera bias': {'name': 'Camera Bias', 'description': "The distance to the view point of observing players that the particle is more likely to spawn in.", 'animation_type': 'Const', 'type': 'Float'},
    'Emissivity': {'name': 'Emissivity', 'description': "The degree to which the particle is emissive.", 'animation_type': 'Animated2D', 'type': 'Float'},
    'Shadow alpha multiplier': {'name': 'Shadow Alpha Multiplier', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Float'},
    'Use Emissivity Channel': {'name': 'Use Emissivity Channel', 'description': "Whether the particle uses the emissivity channel in the texture.", 'animation_type': 'Const', 'type': 'Bool'},
    'Use Alpha Anisotropy': {'name': 'Use Alpha Anisotropy', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Bool'},
    'Ambient light factor': {'name': 'Ambient Light Factor', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Float'},
    'Radius var': {'name': 'Radius Variation', 'description': "The degree to which the particle\'s radius varies randomly.", 'animation_type': 'Const', 'type': 'Float'},
    'Rotation velocity collision multiplier': {'name': 'Rotation Velocity Collision Multiplier', 'description': "The multiplier for the rotation speed of the particle after colliding with an object.", 'animation_type': 'Const', 'type': 'Float'},
    'Collision count to kill particle': {'name': 'Collision Count To Kill Particle', 'description': "The amount of times the particle can collide with an object before it disappears.", 'animation_type': 'Const', 'type': 'Int'},
    'Distance scaling factor': {'name': 'Distance Scaling Factor', 'description': "The factor by which the particle is scaled at a distance.", 'animation_type': 'Const', 'type': 'Float'},
    'Motion interpolation': {'name': 'Motion Interpolation', 'description': "UNKNOWN.", 'animation_type': 'Const', 'type': 'Bool'}
}


class SEUT_UL_ParticleProperties(UIList):
    """Creates the Particle Properties UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.label(text=item.name, icon='PROPERTIES')

    def invoke(self, context, event):
        pass
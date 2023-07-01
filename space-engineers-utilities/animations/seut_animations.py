import bpy

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

from ..seut_preferences     import animation_engine
from ..seut_utils           import get_seut_blend_data
from .seut_animation_utils  import update_vars

def items_trigger_types(self, context):
    items = []
    counter = 0
    for key, entry in animation_engine['triggers'].items():
        if entry['type'] == 'event':
            icon = 'STYLUS_PRESSURE'
        else:
            icon = 'RECOVER_LAST'

        items.append((key, entry['name'], entry['description'], icon, counter))
        counter += 1

    return items


def poll_animation_objects_obj(self, object):
    data = get_seut_blend_data()
    animation_set = data.seut.animations[data.seut.animations_index]
    in_use = any(sp.obj == object for sp in animation_set.subparts)

    return object.type == 'EMPTY' and 'file' in object and not in_use and not object.seut.linked


def update_animation_object_action(self, context):
    if self.action is not None:
        self.action.use_fake_user = True


def update_trigger_type(self, context):
    self.name = self.trigger_type
    update_vars(self, 'triggers', animation_engine)


def poll_trigger_pressed_empty(self, object):
    return object.type == 'EMPTY' and 'highlight' in object and not object.seut.linked


def update_animation_name(self, context):
    if self.name == self.name_prev:
        return
    
    data = get_seut_blend_data()
    for anim in data.seut.animations:
        if self != anim and anim.name == self.name:
            self.name = self.name_prev
            return
    
    self.name_prev = self.name


def items_function_types(self, context):
    items = []
    for key, entry in animation_engine['functions'].items():
        items.append((key, entry['name'], entry['description']))

    return items


def update_function_type(self, context):
    self.name = self.function_type
    update_vars(self, 'functions', animation_engine)


def poll_setVisible_empty(self, object):
    return object.type == 'EMPTY' and 'file' in object and not object.seut.linked


def poll_playParticle_empty(self, object):
    return object.type == 'EMPTY' and not 'file' in object and not 'highlight' in object and not object.seut.linked


class SEUT_AnimationObjects(PropertyGroup):
    """SEUT Animation Object prop holder"""

    name: StringProperty()

    obj: PointerProperty(
        type = bpy.types.Object,
        poll = poll_animation_objects_obj
    )

    action: PointerProperty(
        name = "Action",
        description = "The Action that should be played for the current subpart empty as part of the Animation Set",
        type = bpy.types.Action,
        update = update_animation_object_action
    )


class SEUT_AnimationTriggers(PropertyGroup):
    """SEUT Animation Trigger prop holder"""

    name: StringProperty()
    
    trigger_type: EnumProperty(
        name = "Type",
        description = "Triggers determine when an animation will play ingame",
        items = items_trigger_types,
        default = 0,
        update = update_trigger_type
    )
    vars: StringProperty(
        default = "[]"
    )

    Pressed_empty: PointerProperty(
        name = "Highlight Empty",
        description = "The Highlight Empty that should be monitored",
        type = bpy.types.Object,
        poll = poll_trigger_pressed_empty
    )
    distance: FloatProperty(
        name = "Distance",
        description = "Distance of player from block",
        min = 0,
        max = 20000,
        unit = 'LENGTH'
    )
    Working_bool: BoolProperty(
        name = "Bool",
        description = "Whether the animation should trigger with the State in effect or not in effect",
        default = True
    )
    Working_loop: BoolProperty(
        name = "Loop",
        description = "Whether the animation should loop as long as the State trigger is in effect / not in effect",
        default = True
    )
    Producing_bool: BoolProperty(
        name = "Bool",
        description = "Whether the animation should trigger with the State in effect or not in effect",
        default = True
    )
    Producing_loop: BoolProperty(
        name = "Loop",
        description = "Whether the animation should loop as long as the State trigger is in effect / not in effect",
        default = True
    )


class SEUT_Animations(PropertyGroup):
    """SEUT Animation prop holder"""

    name: StringProperty(
        update = update_animation_name
    )
    name_prev: StringProperty()
    
    triggers: CollectionProperty(
        type = SEUT_AnimationTriggers
    )
    triggers_index: IntProperty(
        default = 0
    )
    subparts: CollectionProperty(
        type = SEUT_AnimationObjects
    )
    subparts_index: IntProperty(
        default = 0
    )


class SEUT_AnimationFunctions(PropertyGroup):
    """SEUT Animation Function prop holder"""

    name: StringProperty()
    
    function_type: EnumProperty(
        name = "Type",
        description = "Functions allow the animation to cause ingame effects at the containing keyframe's point in time",
        items = items_function_types,
        default = 0,
        update = update_function_type
    )
    vars: StringProperty(
        default = "[]"
    )
    
    setVisible_bool: BoolProperty(
        name = "Visible",
        description = "Whether to hide or show the specified subpart"
    )
    setVisible_empty: PointerProperty( 
        name = "Subpart Empty",
        description = "The subpart empty (and subpart) whose visibility is determined",
        type = bpy.types.Object,
        poll = poll_setVisible_empty
    )
    
    setEmissiveColor_material: PointerProperty(
        name = "Emissive Material",
        description = "The emissive material to alter",
        type = bpy.types.Material
    )
    setEmissiveColor_rgb: bpy.props.FloatVectorProperty(
        name="Color",
        description="The color the emissive material is set to",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        size=3,
        min=0,
        max=1.0
    )
    setEmissiveColor_brightness: FloatProperty(
        name = "Brightness",
        description = "The brightness of the emissive material glow",
        min = 0,
        max = 100
    )

    playParticle_empty: PointerProperty( 
        name = "Emitter Empty",
        description = "The particle emitter empty that a particle is played on",
        type = bpy.types.Object,
        poll = poll_playParticle_empty
    )
    playParticle_subtypeid: StringProperty(
        name = "Particle SubtypeId",
        description = "The SubtypeId of the particle to play"
    )

    stopParticle_empty: PointerProperty( 
        name = "Emitter Empty",
        description = "The particle emitter empty that a particle is stopped on",
        type = bpy.types.Object,
        poll = poll_playParticle_empty
    )
    stopParticle_subtypeid: StringProperty(
        name = "Particle SubtypeId",
        description = "The SubtypeId of the particle to stop"
    )

    playSound_subtypeid: StringProperty(
        name = "Sound SubtypeId",
        description = "The SubtypeId of the sound to play"
    )
    stopSound_subtypeid: StringProperty(
        name = "Sound SubtypeId",
        description = "The SubtypeId of the sound to stop"
    )
    
    setLightColor_empty: PointerProperty( 
        name = "Light Empty",
        description = "The light empty whose color is set",
        type = bpy.types.Object,
        poll = poll_playParticle_empty
    )
    setLightColor_rgb: bpy.props.FloatVectorProperty(
        name="Color",
        description="The color the light is set to",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        size=3,
        min=0,
        max=1.0
    )
    
    light_empty: PointerProperty( 
        name = "Light Empty",
        description = "The light empty to affect",
        type = bpy.types.Object,
        poll = poll_playParticle_empty
    )


class SEUT_Keyframes(PropertyGroup):
    """Holder for the various Keyframe properties"""

    name: StringProperty()

    functions: CollectionProperty(
        type = SEUT_AnimationFunctions
    )
    functions_index: IntProperty(
        default = 0
    )


class SEUT_Actions(PropertyGroup):
    """Holder for the various Action properties"""

    keyframes: CollectionProperty(
        type = SEUT_Keyframes
    )
    keyframes_index: IntProperty(
        default = 0
    )
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


def items_trigger_types(self, context):

    items = [
        ('Create', 'Event: Create', "Triggers when block is placed", 'STYLUS_PRESSURE', 0),
        ('Build', 'Event: Build', "Triggers when block switches from last build stage to main model", 'STYLUS_PRESSURE', 1),
        ('Open', 'Event: Open', "Triggers when a door is opened", 'STYLUS_PRESSURE', 2),
        ('Close', 'Event: Close', "Triggers when a door is closed", 'STYLUS_PRESSURE', 3),
        ('Enter', 'Event: Enter', "Triggers when the player enters a cockpit or seat", 'STYLUS_PRESSURE', 4),
        ('Exit', 'Event: Exit', "Triggers when the player exits a cockpit or seat", 'STYLUS_PRESSURE', 5),
        ('Lock', 'Event: Lock', "Triggers when a landing gear locks to a surface", 'STYLUS_PRESSURE', 6),
        ('Unlock', 'Event: Unlock', "Triggers when a landing gear unlocks", 'STYLUS_PRESSURE', 7),
        ('ReadyLock', 'Event: ReadyLock', "Triggers when a landing gear is ready to lock", 'STYLUS_PRESSURE', 8),
        ('PressedOn', 'Event: PressedOn', "Triggers when a button is set to the 'on' state", 'STYLUS_PRESSURE', 9),
        ('PressedOff', 'Event: PressedOff', "Triggers when a button is set to the 'off' state", 'STYLUS_PRESSURE', 10),
        ('Pressed', 'Event: Pressed', "Triggers when a button is interacted with", 'STYLUS_PRESSURE', 11),
        ('Arrive', 'Event: Arrive', "Triggers when a player approaches the block to below a given distance", 'STYLUS_PRESSURE', 12),
        ('Leave', 'Event: Leave', "Triggers when a player leaves a given distance from the block", 'STYLUS_PRESSURE', 13),
        ('Working', 'State: Working', "Triggers while the block is in working order (fully built and not disabled by damage)", 'RECOVER_LAST', 14),
        ('Producing', 'State: Producing', "Triggers while the block is producing", 'RECOVER_LAST', 15)
    ]

    return items


def poll_animation_objects_obj(self, object):
    wm = bpy.context.window_manager
    animation_set = wm.seut.animations[wm.seut.animations_index]
    in_use = any(sp.obj == object for sp in animation_set.subparts)

    return object.type == 'EMPTY' and 'file' in object and not in_use and not object.seut.linked


def update_animation_object_action(self, context):
    self.action.use_fake_user = True


def update_trigger_type(self, context):
    self.name = self.trigger_type


def poll_trigger_pressed_empty(self, object):
    return object.type == 'EMPTY' and 'highlight' in object and not object.seut.linked


def items_function_types(self, context):

    items = [
        ('reset', 'Reset', "Resets the subpart location to its default position"),
        ('resetPos', 'Reset Position', "Resets the subpart to its reset position"),
        ('setResetPos', 'Set Reset Position', "Sets the current location as the new reset position"),
        ('setVisible', 'Set Visible', "Defines the visibility of a subpart"),
        ('setEmissiveColor', 'Set Emissive Color', "Sets the color and brightness of an emissive material"),
        ('setLightColor', 'Set Light Color', "Sets the color of a light empty"),
        ('lightOn', 'Turn Light On', "Turns a specified light empty on"),
        ('lightOff', 'Turn Light Off', "Turns a specified light empty off"),
        ('toggleLight', 'Toggle Light', "Toggles a specified light empty"),
        ('playParticle', 'Play Particle', "Plays a specified particle on a specified particle emitter empty"),
        ('stopParticle', 'Stop Particle', "Stops a specified particle from playing on a specified particle emitter empty"),
        ('playSound', 'Play Sound', "Plays a specified sound"),
        ('stopSound', 'Stop Sound', "Stops playing a specified sound")
    ]

    return items


def update_function_type(self, context):
    self.name = self.function_type


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
        description = "Triggers determind when an animation will play ingame",
        items = items_trigger_types,
        default = 0,
        update = update_trigger_type
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
        name = "Name"
    )
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
        description = "",
        items = items_function_types,
        default = 0,
        update = update_function_type
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


class SEUT_Fcurves(PropertyGroup):
    """Holder for the various Keyframe properties"""

    name: StringProperty()
    
    keyframes: CollectionProperty(
        type = SEUT_Keyframes
    )
    keyframes_index: IntProperty(
        default = 0
    )


class SEUT_Actions(PropertyGroup):
    """Holder for the various Action properties"""

    fcurves: CollectionProperty(
        type = SEUT_Fcurves
    )
    fcurves_index: IntProperty(
        default = 0
    )
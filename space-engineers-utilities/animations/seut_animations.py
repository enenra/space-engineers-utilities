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


from ..seut_utils           import get_seut_blend_data


def poll_animation_objects_obj(self, object):
    data = get_seut_blend_data()
    animation_set = data.seut.animations[data.seut.animations_index]
    in_use = any(sp.obj == object for sp in animation_set.subparts)

    return object.type == 'EMPTY' and 'file' in object and not in_use and not object.seut.linked


def update_animation_object_action(self, context):
    if self.action is not None:
        self.action.use_fake_user = True


def update_animation_name(self, context):
    if self.name == self.name_prev:
        return
    
    data = get_seut_blend_data()
    for anim in data.seut.animations:
        if self != anim and anim.name == self.name:
            self.name = self.name_prev
            return
    
    self.name_prev = self.name


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


class SEUT_Animations(PropertyGroup):
    """SEUT Animation prop holder"""

    name: StringProperty(
        update = update_animation_name
    )
    name_prev: StringProperty()
    
    subparts: CollectionProperty(
        type = SEUT_AnimationObjects
    )
    subparts_index: IntProperty(
        default = 0
    )
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

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import report_error
from .seut_utils                    import linkSubpartScene, unlinkSubpartScene, getParentCollection


def update_linkedScene(self, context):
    scene = context.scene
    empty = context.view_layer.objects.active
    collections = SEUT_OT_RecreateCollections.getCollections(scene)

    if collections['main'] is None:
        return

    if empty is not None:
        
        parentCollection = getParentCollection(context, empty)
        if parentCollection == collections['main']:
            if 'file' in empty:
                empty['file'] = ""
            unlinkSubpartScene(empty)

            if empty.seut.linkedScene is not None:
                empty['file'] = empty.seut.linkedScene.seut.subtypeId
                if scene.seut.linkSubpartInstances:
                    try:
                        linkSubpartScene(self, scene, empty, None)
                    except AttributeError:
                        report_error(self, context, False, 'E002')
                        empty.seut.linkedScene = None


def update_linkedObject(self, context):
    scene = context.scene
    empty = context.view_layer.objects.active

    if empty is not None:
        if 'highlight' in empty:
            empty['highlight'] = None

        if empty.seut.linkedObject is not None:
            empty['highlight'] = empty.seut.linkedObject.name


def update_default(self, context):
    scene = context.scene

    if not context.active_object.seut.default:
        return

    objects = bpy.data.collections['Mountpoints (' + scene.seut.subtypeId + ')'].objects
    
    if context.active_object.seut.default and context.active_object.name in objects:
        for obj in objects:
            if obj is context.active_object:
                pass
            elif obj.seut.default:
                obj.seut.default = False


# These prevent the selected scene from being the current scene and the selected object being the current object
def poll_linkedScene(self, object):
    return object != bpy.context.scene and object.seut.sceneType == 'subpart'


def poll_linkedObject(self, object):
    return object != bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.parent == object.parent and object.type != 'EMPTY'


class SEUT_Object(PropertyGroup):
    """Holder for the various object properties"""
    
    linkedScene: PointerProperty(
        name='Subpart Scene',
        description="Which subpart scene this empty links to. Scene must be of type 'Subpart'",
        type=bpy.types.Scene,
        poll=poll_linkedScene,
        update=update_linkedScene
    )
    
    linkedObject: PointerProperty(
        name='Highlight Object',
        description="Which object this empty links to",
        type=bpy.types.Object,
        poll=poll_linkedObject,
        update=update_linkedObject
    )
    
    default: BoolProperty(
        name='Default',
        description="Whether a Mountpoint Area is the one where a block is first attempted to be placed on",
        default=False,
        update=update_default
    )
    
    pressurized: BoolProperty(
        name='Pressurized When Open',
        description="Whether a mountpoint on a door block stays pressurized when the door is opened",
        default=False
    )
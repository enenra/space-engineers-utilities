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
from .seut_utils                    import linkSubpartScene, unlinkSubpartScene


def update_linkedScene(self, context):
    scene = context.scene
    empty = context.view_layer.objects.active

    if empty is not None:
        if 'file' in empty:
            empty['file'] = ""
        unlinkSubpartScene(empty)

        if empty.seut.linkedScene is not None:
            empty['file'] = empty.seut.linkedScene.name
            if scene.seut.linkSubpartInstances:
                linkSubpartScene(self, scene, empty, empty.seut.linkedScene)


def update_linkedObject(self, context):
    scene = context.scene
    empty = context.view_layer.objects.active

    if empty is not None:
        if 'highlight' in empty:
            empty['highlight'] = None

        if empty.seut.linkedObject is not None:
            empty['highlight'] = empty.seut.linkedObject.name


# These prevent the selected scene from being the current scene and the selected object being the current object
def poll_linkedScene(self, object):
    return object != bpy.context.scene and object.seut.sceneType == 'subpart'


def poll_linkedObject(self, object):
    return object != bpy.context.view_layer.objects.active


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
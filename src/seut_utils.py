import bpy
import os

from math   import pi

from .seut_collections              import get_collections
from .seut_errors                   import check_collection, seut_report


def link_subpart_scene(self, origin_scene, empty, target_collection, collection_type = 'main'):
    """Link instances of subpart scene objects as children to empty"""

    context = bpy.context
    current_scene = context.window.scene
    subpart_scene = empty.seut.linkedScene
    parent_collections = get_collections(origin_scene)
    subpart_collections = get_collections(subpart_scene)

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, subpart_scene, subpart_collections[collection_type], False)
    if not result == {'CONTINUE'}:
        empty.seut.linkedScene = None
        empty['file'] = None
        return
    
    # This prevents instancing loops.
    for obj in subpart_collections[collection_type].objects:
        if obj is not None and obj.type == 'EMPTY' and obj.seut.linkedScene == origin_scene:
            seut_report(self, context, 'ERROR', False, 'E005', subpart_scene.name, current_scene.name)
            empty.seut.linkedScene = None
            empty['file'] = None
            return
    
    # Switch to subpart_scene to get collections
    context.window.scene = subpart_scene
    current_area = prep_context(context)

    subpart_objects = set(subpart_collections[collection_type].objects)

    for obj in subpart_objects:

        # The following is done only on a first-level subpart as
        # further-nested subparts already have empties as parents.
        # Needs to account for empties being parents that aren't subpart empties.
        if obj is not None and (obj.parent is None or obj.parent.type != 'EMPTY' or not 'file' in obj.parent) and obj.name.find("(L)") == -1:

            obj.hide_viewport = False
            existing_objects = set(subpart_collections[collection_type].objects)
            
            # Create instance of object
            try:
                context.window.view_layer.objects.active.select_set(state=False, view_layer=context.window.view_layer)
            except AttributeError:
                pass
            context.window.view_layer.objects.active = obj
            obj.select_set(state=True, view_layer=context.window.view_layer)

            bpy.ops.object.duplicate(linked=True)
        
            new_objects = set(subpart_collections[collection_type].objects)
            created_objects = new_objects.copy()
            delete_objects = set()

            for new_obj in new_objects:
                for existing_obj in existing_objects:
                    if new_obj == existing_obj:
                        created_objects.remove(new_obj)

                if new_obj in created_objects and new_obj.name.find("(L)") != -1:
                    created_objects.remove(new_obj)
                    delete_objects.add(new_obj)
            
            for obj in delete_objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Rename instance
            linked_object = None
            for obj in created_objects:
                obj.name = obj.name + " (L)"
                linked_object = obj

            if linked_object is not None:
                # Link instance to empty
                try:
                    if target_collection is None:
                        parent_collections[collection_type].objects.link(linked_object)
                    else:
                        target_collection.objects.link(linked_object)
                except RuntimeError:
                    pass
                subpart_collections[collection_type].objects.unlink(linked_object)
                linked_object.parent = empty

                if linked_object.type == 'EMPTY' and linked_object.seut.linkedScene is not None and linked_object.seut.linkedScene.name in bpy.data.scenes and origin_scene.seut.linkSubpartInstances:
                    link_subpart_scene(self, origin_scene, linked_object, target_collection)

    # Switch back to previous scene
    context.area.type = current_area
    context.window.scene = current_scene


def unlink_subpart_scene(empty):
    """Unlinks all subpart instances from an empty"""

    for obj in empty.children:
        unlink_objects_in_hierarchy(obj)


def unlink_objects_in_hierarchy(obj):
    """Unlinks all objects in hierarchy of an object"""

    for child in obj.children:
        unlink_objects_in_hierarchy(child)

    bpy.data.objects.remove(obj, do_unlink=True)


def get_parent_collection(context, child):
    scene = context.scene

    collections = get_collections(scene)
    
    for key, value in collections.items():
        if value is not None:
            for obj in value.objects:
                if obj is not None and obj == child:
                    return value
    
    return None


def to_radians(number):
    """Converts degrees to radians"""
    return pi * number / 180


def get_preferences():
    """Returns the preferences of the addon"""

    if __package__.find(".") == -1:
        addon = __package__
    else:
        addon = __package__[:__package__.find(".")]

    return bpy.context.preferences.addons.get(addon).preferences


def prep_context(context):
    """Prep context for doing larger alterations, returns previous area"""

    try:
        current_area = context.area.type
        context.area.type = 'VIEW_3D'
    except AttributeError:
        context.area.type = 'VIEW_3D'
        current_area = context.area.type

    clear_selection(context)
    
    return current_area


def clear_selection(context):
    """Deselects object and sets active object to None."""

    if context.object is not None:
        context.object.select_set(False)
        context.view_layer.objects.active = None


def toggle_scene_modes(context, mirroring, mountpoints, icon_render):
    """Sets modes in all scenes."""

    original_scene = context.scene

    for scn in bpy.data.scenes:
        context.window.scene = scn

        if scn == original_scene:
            if scn.seut.mirroringToggle != mirroring:
                scn.seut.mirroringToggle = mirroring
            if scn.seut.mountpointToggle != mountpoints:
                scn.seut.mountpointToggle = mountpoints
            if scn.seut.renderToggle != icon_render:
                scn.seut.renderToggle = icon_render

        else:
            if scn.seut.mirroringToggle == 'on':
                scn.seut.mirroringToggle = 'off'
            if scn.seut.mountpointToggle == 'on':
                scn.seut.mountpointToggle = 'off'
            if scn.seut.renderToggle == 'on':
                scn.seut.renderToggle = 'off'

    context.window.scene = original_scene


def create_seut_collection(seut_collection, name: str):
    """Creates a new SEUT collection if it doesn't exist yet, else returns the existing one."""

    if not name in bpy.data.collections:
        collection = bpy.data.collections.new(name)
        seut_collection.children.link(collection)

    else:
        collection = bpy.data.collections[name]
        try:
            seut_collection.children.link(collection)
        except:
            pass
    
    return collection


def lock_object(target):
    """Locks the specified object's location, rotation and scale"""

    target.lock_location = (True, True, True)
    target.lock_rotation = (True, True, True)
    target.lock_scale = (True, True, True)
import bpy

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection

def linkSubpartScene(self, scene, empty, subpartScene):
    """Link instances of subpart scene objects as children to empty"""

    context = bpy.context
    parentCollections = SEUT_OT_RecreateCollections.get_Collections(scene)
    
    # Switch to subpartScene to get collections
    currentScene = bpy.context.window.scene
    context.window.scene = subpartScene

    subpartCollections = SEUT_OT_RecreateCollections.get_Collections(subpartScene)
    # Checks whether collection exists, is excluded or is empty
    result = errorCollection(self, context, subpartCollections['main'], False)
    if not result == 'CONTINUE':
        return {result}
    
    # This prevents instancing loops.
    for o in subpartCollections['main'].objects:
        if o is not None and o.type == 'EMPTY' and o.seut.linkedScene == scene:
            print("SEUT Error: Linking to scene '" + subpartScene.name + "' from '" + currentScene.name + "' would create a subpart instancing loop.")
            empty.seut.linkedScene = None
            empty['file'] = None
            context.window.scene = currentScene
            return 'CANCEL'

    objectsToIterate = set(subpartCollections['main'].objects)

    for obj in objectsToIterate:
        
        existingObjects = set(subpartCollections['main'].objects)
        
        # Create instance of object
        context.window.view_layer.objects.active = obj
        obj.select_set(state=True, view_layer=context.window.view_layer)

        # Without overriding, it runs in the main scene
        override = {'scene': subpartScene}
        bpy.ops.object.duplicate(override, linked=True)
    
        newObjects = set(subpartCollections['main'].objects)
        createdObjects = newObjects.copy()

        for obj1 in newObjects:
            for obj2 in existingObjects:
                if obj1 == obj2:
                    createdObjects.remove(obj1)
        
        # Rename instance
        linkedObject = None
        for createdObj in createdObjects:
            createdObj.name = obj.name + " (L)"
            linkedObject = createdObj

        # Link instance to empty
        parentCollections['main'].objects.link(linkedObject)
        subpartCollections['main'].objects.unlink(linkedObject)
        linkedObject.parent = empty

    # Switch back to previous scene
    context.window.scene = currentScene
    
    return 'CONTINUE'

def unlinkSubpartScene(empty):
    """Unlinks all subpart instances from an empty"""

    for obj in empty.children:
        bpy.data.objects.remove(obj, do_unlink=True)

    return 'CONTINUE'

def getParentCollection(context, childObject):
    scene = context.scene

    collections = SEUT_OT_RecreateCollections.get_Collections(scene)
    
    for key, value in collections.items():
        if value is not None:
            for obj in value.objects:
                if obj is not None and obj == childObject:
                    return value
    
    return None
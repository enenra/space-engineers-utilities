import bpy

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection

def linkSubpartScene(self, originScene, empty):
    """Link instances of subpart scene objects as children to empty"""

    context = bpy.context
    parentCollections = SEUT_OT_RecreateCollections.get_Collections(originScene)
    
    # Switch to subpartScene to get collections
    currentScene = bpy.context.window.scene
    subpartScene = empty.seut.linkedScene
    context.window.scene = subpartScene

    subpartCollections = SEUT_OT_RecreateCollections.get_Collections(subpartScene)
    # Checks whether collection exists, is excluded or is empty
    result = errorCollection(self, context, subpartCollections['main'], False)
    if not result == 'CONTINUE':
        return {result}
    
    # This prevents instancing loops.
    for o in subpartCollections['main'].objects:
        if o is not None and o.type == 'EMPTY' and o.seut.linkedScene == originScene:
            print("SEUT Error: Linking to scene '" + subpartScene.name + "' from '" + currentScene.name + "' would create a subpart instancing loop.")
            empty.seut.linkedScene = None
            empty['file'] = None
            context.window.scene = currentScene
            return 'CANCEL'

    objectsToIterate = set(subpartCollections['main'].objects)

    for obj in objectsToIterate:

        # The following is done only on a first-level subpart as
        # further-nested subparts already have empties as parents.
        # Needs to account for empties being parents that aren't subpart empties.
        if (obj.parent is None or obj.parent.type != 'EMPTY' or not 'file' in obj.parent) and obj.name.find("(L)") == -1:

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

            if linkedObject.type == 'EMPTY' and linkedObject.seut.linkedScene is not None and linkedObject.seut.linkedScene.name in bpy.data.scenes:
                linkSubpartScene(self, originScene, linkedObject)
        
    # Switch back to previous scene
    context.window.scene = currentScene
    
    return 'CONTINUE'


def unlinkSubpartScene(empty):
    """Unlinks all subpart instances from an empty"""

    for obj in empty.children:
        unlinkObjectsInHierarchy(obj)

    return 'CONTINUE'


def unlinkObjectsInHierarchy(obj):
    """Unlinks all objects in hierarchy of an object"""

    for child in obj.children:
        unlinkObjectsInHierarchy(child)

    bpy.data.objects.remove(obj, do_unlink=True)


def getParentCollection(context, childObject):
    scene = context.scene

    collections = SEUT_OT_RecreateCollections.get_Collections(scene)
    
    for key, value in collections.items():
        if value is not None:
            for obj in value.objects:
                if obj is not None and obj == childObject:
                    return value
    
    return None
import bpy

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection

def linkSubpartScene(self, originScene, empty, targetCollection):
    """Link instances of subpart scene objects as children to empty"""

    context = bpy.context
    parentCollections = SEUT_OT_RecreateCollections.getCollections(originScene)
    
    # Switch to subpartScene to get collections
    currentScene = bpy.context.window.scene
    subpartScene = empty.seut.linkedScene
    context.window.scene = subpartScene

    subpartCollections = SEUT_OT_RecreateCollections.getCollections(subpartScene)
    # Checks whether collection exists, is excluded or is empty
    result = errorCollection(self, context, subpartCollections['main'], False)
    if not result == {'CONTINUE'}:
        return result
    
    # This prevents instancing loops.
    for o in subpartCollections['main'].objects:
        if o is not None and o.type == 'EMPTY' and o.seut.linkedScene == originScene:
            print("SEUT Error: Linking to scene '" + subpartScene.name + "' from '" + currentScene.name + "' would create a subpart instancing loop.")
            empty.seut.linkedScene = None
            empty['file'] = None
            context.window.scene = currentScene
            return {'CANCEL'}

    objectsToIterate = set(subpartCollections['main'].objects)

    for obj in objectsToIterate:

        # The following is done only on a first-level subpart as
        # further-nested subparts already have empties as parents.
        # Needs to account for empties being parents that aren't subpart empties.
        if obj is not None and (obj.parent is None or obj.parent.type != 'EMPTY' or not 'file' in obj.parent) and obj.name.find("(L)") == -1:

            obj.hide_viewport = False

            existingObjects = set(subpartCollections['main'].objects)
            
            # Create instance of object
            try:
                context.window.view_layer.objects.active.select_set(state=False, view_layer=context.window.view_layer)
            except AttributeError:
                pass
            context.window.view_layer.objects.active = obj
            obj.select_set(state=True, view_layer=context.window.view_layer)

            bpy.ops.object.duplicate(linked=True)
        
            newObjects = set(subpartCollections['main'].objects)
            createdObjects = newObjects.copy()
            deleteObjects = set()

            for obj1 in newObjects:
                for obj2 in existingObjects:
                    if obj1 == obj2:
                        createdObjects.remove(obj1)
                if obj1 in createdObjects and obj1.name.find("(L)") != -1:
                    createdObjects.remove(obj1)
                    deleteObjects.add(obj1)
            
            for delObj in deleteObjects:
                bpy.data.objects.remove(delObj, do_unlink=True)
            
            # Rename instance
            linkedObject = None
            for createdObj in createdObjects:
                createdObj.name = obj.name + " (L)"
                linkedObject = createdObj

            if linkedObject is not None:
                # Link instance to empty
                try:
                    if targetCollection is None:
                        parentCollections['main'].objects.link(linkedObject)
                    else:
                        targetCollection.objects.link(linkedObject)
                except RuntimeError:
                    pass
                subpartCollections['main'].objects.unlink(linkedObject)
                linkedObject.parent = empty

                if linkedObject.type == 'EMPTY' and linkedObject.seut.linkedScene is not None and linkedObject.seut.linkedScene.name in bpy.data.scenes and originScene.seut.linkSubpartInstances:
                    linkSubpartScene(self, originScene, linkedObject, targetCollection)
        
    # Switch back to previous scene
    context.window.scene = currentScene
    
    return {'CONTINUE'}


def unlinkSubpartScene(empty):
    """Unlinks all subpart instances from an empty"""

    for obj in empty.children:
        unlinkObjectsInHierarchy(obj)

    return {'CONTINUE'}


def unlinkObjectsInHierarchy(obj):
    """Unlinks all objects in hierarchy of an object"""

    for child in obj.children:
        unlinkObjectsInHierarchy(child)

    bpy.data.objects.remove(obj, do_unlink=True)


def getParentCollection(context, childObject):
    scene = context.scene

    collections = SEUT_OT_RecreateCollections.getCollections(scene)
    
    for key, value in collections.items():
        if value is not None:
            for obj in value.objects:
                if obj is not None and obj == childObject:
                    return value
    
    return None
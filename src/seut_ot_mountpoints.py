import bpy

from bpy.types import Operator

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection, isCollectionExcluded
from .seut_utils                    import getParentCollection

class SEUT_OT_Mountpoints(Operator):
    """Handles everything related to mountpoint functionality"""
    bl_idname = "scene.mountpoints"
    bl_label = "Mountpoints"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.mountpointToggle == 'on':
            if scene.seut.mirroringToggle == 'on':
                scene.seut.mirroringToggle = 'off'
            result = SEUT_OT_Mountpoints.mountpointSetup(self, context)

        elif scene.seut.mountpointToggle == 'off':
            result = SEUT_OT_Mountpoints.cleanMountpointSetup(self, context)

        return result
    

    def mountpointSetup(self, context):
        """Sets up mountpoint utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children

        if collections['seut'] is None:
            print("SEUT Warning: Collection 'SEUT " + scene.name + "' not found. Action not possible. (002)")
            scene.seut.mountpointToggle = 'off'
            return {'CANCELLED'}

        isExcluded = isCollectionExcluded(collections['seut'].name, allCurrentViewLayerCollections)
        if isExcluded or isExcluded is None:
            print("SEUT Warning: Collection 'SEUT " + scene.name + "' excluded from view layer. Action not possible. (019)")
            scene.seut.mountpointToggle = 'off'
            return {'CANCELLED'}
            
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Check if entries for sides exist. If not, add them.
        front = SEUT_OT_Mountpoints.recreateSide(context, 'front')
        back = SEUT_OT_Mountpoints.recreateSide(context, 'back')
        left = SEUT_OT_Mountpoints.recreateSide(context, 'left')
        right = SEUT_OT_Mountpoints.recreateSide(context, 'right')
        top = SEUT_OT_Mountpoints.recreateSide(context, 'top')
        bottom = SEUT_OT_Mountpoints.recreateSide(context, 'bottom')

        # Check if entries for blocks exist. Compare to bounding box. Cull and add.
        SEUT_OT_Mountpoints.recreateBlocks(context, front, scene.seut.bBox_X, scene.seut.bBox_Z)
        SEUT_OT_Mountpoints.recreateBlocks(context, back, scene.seut.bBox_X, scene.seut.bBox_Z)
        SEUT_OT_Mountpoints.recreateBlocks(context, left, scene.seut.bBox_Y, scene.seut.bBox_Z)
        SEUT_OT_Mountpoints.recreateBlocks(context, right, scene.seut.bBox_Y, scene.seut.bBox_Z)
        SEUT_OT_Mountpoints.recreateBlocks(context, top, scene.seut.bBox_X, scene.seut.bBox_Y)
        SEUT_OT_Mountpoints.recreateBlocks(context, bottom, scene.seut.bBox_X, scene.seut.bBox_Y)

        print("<<================================================================>>")

        """
        # Check if entries for squares exist. If not, add them.
        for mp in scene.seut.mountpoints:
            for block in mp.blocks:
                SEUT_OT_Mountpoints.recreateSquares(context, block, 5)      # Defining the amount of squares like so allows me to later implement inversely scaling the amount of squares with bbox size
        """

        # Create collection if it doesn't exist already
        if not 'Mountpoints' + tag in bpy.data.collections:
            collection = bpy.data.collections.new('Mountpoints' + tag)
            collections['seut'].children.link(collection)
        else:
            collection = bpy.data.collections['Mountpoints' + tag]
            try:
                collections['seut'].children.link(collection)
            except:
                pass

        # Create empty tree for sides
        bpy.ops.object.add(type='EMPTY')
        emptyFront = bpy.context.view_layer.objects.active
        emptyFront.name = 'Mountpoints Front'
        bpy.ops.object.add(type='EMPTY')
        emptyBack = bpy.context.view_layer.objects.active
        emptyBack.name = 'Mountpoints Back'
        bpy.ops.object.add(type='EMPTY')
        emptyLeft = bpy.context.view_layer.objects.active
        emptyLeft.name = 'Mountpoints Left'
        bpy.ops.object.add(type='EMPTY')
        emptyRight = bpy.context.view_layer.objects.active
        emptyRight.name = 'Mountpoints Right'
        bpy.ops.object.add(type='EMPTY')
        emptyTop = bpy.context.view_layer.objects.active
        emptyTop.name = 'Mountpoints Top'
        bpy.ops.object.add(type='EMPTY')
        emptyBottom = bpy.context.view_layer.objects.active
        emptyBottom.name = 'Mountpoints Bottom'


        parentCollection = getParentCollection(context, emptyFront)
        if parentCollection != collection:
            collection.objects.link(emptyFront)
            collection.objects.link(emptyBack)
            collection.objects.link(emptyLeft)
            collection.objects.link(emptyRight)
            collection.objects.link(emptyTop)
            collection.objects.link(emptyBottom)

            if parentCollection is None:
                scene.collection.objects.unlink(emptyFront)
                scene.collection.objects.unlink(emptyBack)
                scene.collection.objects.unlink(emptyLeft)
                scene.collection.objects.unlink(emptyRight)
                scene.collection.objects.unlink(emptyTop)
                scene.collection.objects.unlink(emptyBottom)
            else:
                parentCollection.objects.unlink(emptyFront)
                parentCollection.objects.unlink(emptyBack)
                parentCollection.objects.unlink(emptyLeft)
                parentCollection.objects.unlink(emptyRight)
                parentCollection.objects.unlink(emptyTop)
                parentCollection.objects.unlink(emptyBottom)

        # Add the planes to the empties

        # Start the loop to check for selection

        return {'FINISHED'}
        """Cleans up mountpoint utilities"""
    

    def cleanMountpointSetup(self, context):

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # stop the loop

        # Save empty rotation values to properties, delete children instances, remove empty
        for obj in scene.objects:
            if obj is not None and obj.type == 'EMPTY':
                if obj.name == 'Mountpoints Front' or obj.name == 'Mountpoints Back' or obj.name == 'Mountpoints Left' or obj.name == 'Mountpoints Right' or obj.name == 'Mountpoints Top' or obj.name == 'Mountpoints Bottom':
                    for child in obj.children:
                        child.select_set(state=False, view_layer=context.window.view_layer)
                        bpy.data.objects.remove(child)
                    obj.select_set(state=False, view_layer=context.window.view_layer)
                    bpy.data.objects.remove(obj)

        # delete planes
    
        # Delete collection
        if 'Mountpoints' + tag in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections['Mountpoints' + tag])

        return {'FINISHED'}
    

    def toggleSquare(self, context, square):

        scene = context.scene

        # Change plane material

        # Change square bool

        return {'FINISHED'}
    

    def recreateSide(context, sideName):
        """Searches scene for a mountpoint side. If it exists, return it, else create it and then return it"""

        scene = context.scene

        for mp in scene.seut.mountpoints:
            if mp is not None and mp.side == sideName:
                return mp
        
        item = scene.seut.mountpoints.add()
        item.side = sideName
        return item
    

    def recreateBlocks(context, sideObject, x, y):
        """Iterates through blocks associated with a mountpoint side, removes ones that are not valid anymore and adds new ones in gaps"""

        scene = context.scene
        
        print("---------------------------------------------")
        print(sideObject.side.upper() + " OLD: " + str(len(sideObject.blocks)))
        
        # Register existing blocks and remove blocks that are out of bounds
        existingBlocks = set(sideObject.blocks)

        """
        print("removing...")
        for  b in existingBlocks:
            temp = " x: " + str(b.x) + " y: " + str(b.y)
            found = False
            for xIdx in range(x):
                for yIdx in range(y):
                    if b.x == xIdx and b.y == yIdx:
                        found = True
                        print(temp + " existing")
            if not found:
                print(temp + " removed")
                sideObject.blocks.remove(sideObject.blocks.find(b.name))
        """

        sideObject.blocks.clear()

        print("adding...")
        for xIdx in range(x):
            for yIdx in range(y):
                temp = " x: " + str(xIdx) + " y: " + str(yIdx)
                found = False
                for b in sideObject.blocks:
                    if b.x == xIdx and b.y == yIdx:
                        found = True
                        print(temp + " existing")
                if not found:
                    print(temp + " added")
                    item = sideObject.blocks.add()
                    item.x = xIdx
                    item.y = yIdx

        print(sideObject.side.upper() + " NEW: " + str(len(sideObject.blocks)))
    

    def recreateSquares(context, block, squaresPerAxis):
        """Iterates through squares of a mountpoint side's blocks and adds their entries if necessary"""

        scene = context.scene

        # Create matrix with given dimensions
        matrix = [[False] * squaresPerAxis for r in range(squaresPerAxis)]

        # Register existing square entries and remove squares out of bounds
        for s in block.squares:
            if s is not None:
                if s.x <= squaresPerAxis - 1 and s.y <= squaresPerAxis - 1:
                    matrix[s.x][s.y] = True
                else:
                    block.squares.remove(block.squares.find(s.name))

        # Recreate missing squares
        for row in range(squaresPerAxis):
            for col in range(squaresPerAxis):
                if matrix[row][col] == False:
                    matrix[row][col] = True
                    item = block.squares.add()
                    item.x = row
                    item.y = col
                    item.valid = False
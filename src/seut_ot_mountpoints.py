import bpy

from math           import pi
from bpy.types      import Operator

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

        # print("<<================================================================>>")

        # Check if entries for squares exist. If not, add them.
        for mp in scene.seut.mountpoints:
            for block in mp.blocks:
                SEUT_OT_Mountpoints.recreateSquares(context, block, 5)      # Defining the amount of squares like so allows me to later implement inversely scaling the amount of squares with bbox size

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
        if scene.seut.gridScale == 'small':
            scale = 0.5
        else:
            scale = 2.5

        bboxX = scene.seut.bBox_X * scale
        bboxY = scene.seut.bBox_Y * scale
        bboxZ = scene.seut.bBox_Z * scale

        # Create and position side empties
        emptyFront = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints Front', collection, None)
        emptyFront.empty_display_type = 'SINGLE_ARROW'
        emptyFront.rotation_euler.x = pi * -90 / 180
        emptyFront.rotation_euler.z = pi * -180 / 180
        emptyFront.location.y = -(bboxY / 2 * 1.1)
        emptyFront.location.x = -(scale / 2 * (scene.seut.bBox_X - 1))
        emptyFront.location.z = -(scale / 2 * (scene.seut.bBox_Z - 1))

        emptyBack = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints Back', collection, None)
        emptyBack.empty_display_type = 'SINGLE_ARROW'
        emptyBack.rotation_euler.x = pi * -90 / 180
        emptyBack.location.y = bboxY / 2 * 1.1
        emptyBack.location.x = (scale / 2 * (scene.seut.bBox_X - 1))
        emptyBack.location.z = -(scale / 2 * (scene.seut.bBox_Z - 1))

        emptyLeft = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints Left', collection, None)
        emptyLeft.empty_display_type = 'SINGLE_ARROW'
        emptyLeft.rotation_euler.z = pi * -270 / 180
        emptyLeft.rotation_euler.x = pi * -90 / 180
        emptyLeft.location.x = -(bboxX / 2 * 1.1)
        emptyLeft.location.y = (scale / 2 * (scene.seut.bBox_Y - 1))
        emptyLeft.location.z = -(scale / 2 * (scene.seut.bBox_Z - 1))

        emptyRight = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints Right', collection, None)
        emptyRight.empty_display_type = 'SINGLE_ARROW'
        emptyRight.rotation_euler.z = pi * 270 / 180
        emptyRight.rotation_euler.x = pi * -90 / 180
        emptyRight.location.x = bboxX / 2 * 1.1
        emptyRight.location.y = -(scale / 2 * (scene.seut.bBox_Y - 1))
        emptyRight.location.z = -(scale / 2 * (scene.seut.bBox_Z - 1))

        emptyTop = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints Top', collection, None)
        emptyTop.empty_display_type = 'SINGLE_ARROW'
        emptyTop.location.z = bboxZ / 2 * 1.1
        emptyTop.location.x = (scale / 2 * (scene.seut.bBox_X - 1))
        emptyTop.location.y = (scale / 2 * (scene.seut.bBox_Y - 1))

        emptyBottom = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints Bottom', collection, None)
        emptyBottom.empty_display_type = 'SINGLE_ARROW'
        # emptyBottom.rotation_euler.x = pi * 180 / 180
        # emptyBottom.rotation_euler.y = pi * 180 / 180
        emptyBottom.location.z = -(bboxZ / 2 * 1.1)
        emptyBottom.location.x = -(scale / 2 * (scene.seut.bBox_X - 1))
        emptyBottom.location.y = -(scale / 2 * (scene.seut.bBox_Y - 1))

        #   Create empties for blocks
        for mp in scene.seut.mountpoints:
            for block in mp.blocks:
                if mp.side == 'front':
                    blockEmpty = SEUT_OT_Mountpoints.createEmpty(context, mp.side + ' Block ' + block.name, collection, emptyFront)
                elif mp.side == 'back':
                    blockEmpty = SEUT_OT_Mountpoints.createEmpty(context, mp.side + ' Block ' + block.name, collection, emptyBack)
                elif mp.side == 'left':
                    blockEmpty = SEUT_OT_Mountpoints.createEmpty(context, mp.side + ' Block ' + block.name, collection, emptyLeft)
                elif mp.side == 'right':
                    blockEmpty = SEUT_OT_Mountpoints.createEmpty(context, mp.side + ' Block ' + block.name, collection, emptyRight)
                elif mp.side == 'top':
                    blockEmpty = SEUT_OT_Mountpoints.createEmpty(context, mp.side + ' Block ' + block.name, collection, emptyTop)
                elif mp.side == 'bottom':
                    blockEmpty = SEUT_OT_Mountpoints.createEmpty(context, mp.side + ' Block ' + block.name, collection, emptyBottom)
                blockEmpty.location.x = -(block.x * scale)
                blockEmpty.location.y = -(block.y * scale)

        # Add the planes to the empties

        #   Determine offset from center per side

        #   

        # Start the loop to check for selection

        return {'FINISHED'}
        """Cleans up mountpoint utilities"""
    

    def createEmpty(context, name, collection, parent):
        """Creates empty with given name, links it to specified collection and assigns it to a parent, if available"""

        scene = context.scene

        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active
        empty.name = name

        parentCollection = getParentCollection(context, empty)
        if parentCollection != collection:
            collection.objects.link(empty)

            if parentCollection is None:
                scene.collection.objects.unlink(empty)
            else:
                parentCollection.objects.unlink(empty)
        
        if parent is not None:
            empty.parent = parent

        return empty
    

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
        
        # print("---------------------------------------------")
        # print(sideObject.side.upper() + " OLD: " + str(len(sideObject.blocks)))
        
        # Iterate through existing blocks and mark the ones out of scope for deletion
        deleteBlocks = set()

        for b in sideObject.blocks:
            found = False
            for xIdx in range(x):
                for yIdx in range(y):
                    if b.x == xIdx and b.y == yIdx:
                        found = True
            if not found:
                deleteBlocks.add(b.name)

        # Delete the blocks that are out of scope
        for b in deleteBlocks:
            sideObject.blocks.remove(sideObject.blocks.find(b))

        # Fill in gaps with new blocks
        for xIdx in range(x):
            for yIdx in range(y):
                found = False
                for b in sideObject.blocks:
                    if b.x == xIdx and b.y == yIdx:
                        found = True
                if not found:
                    item = sideObject.blocks.add()
                    item.name = str(xIdx) + "_" + str(yIdx)
                    item.x = xIdx
                    item.y = yIdx

        # print(sideObject.side.upper() + " NEW: " + str(len(sideObject.blocks)))
    

    def recreateSquares(context, block, squaresPerAxis):
        """Iterates through squares of a mountpoint side's blocks and adds their entries if necessary"""

        scene = context.scene

        # Iterate through existing squares and mark the ones out of scope for deletion
        deleteSquares = set()

        for s in block.squares:
            found = False
            for xIdx in range(squaresPerAxis):
                for yIdx in range(squaresPerAxis):
                    if s.x == xIdx and s.y == yIdx:
                        found = True
            if not found:
                deleteSquares.add(s.name)

        # Delete the squares that are out of scope
        for s in deleteSquares:
            block.squares.remove(block.squares.find(s))

        # Fill in gaps with new squares
        for xIdx in range(squaresPerAxis):
            for yIdx in range(squaresPerAxis):
                found = False
                for s in block.squares:
                    if s.x == xIdx and s.y == yIdx:
                        found = True
                if not found:
                    item = block.squares.add()
                    item.name = str(xIdx) + "_" + str(yIdx)
                    item.x = xIdx
                    item.y = yIdx
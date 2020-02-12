import bpy

from bpy.types import Operator

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

        scene = context.scene

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

        # Check if entries for squares exist. If not, add them.
        for mp in scene.seut.mountpoints:
            for block in mp.blocks:
                SEUT_OT_Mountpoints.recreateSquares(context, block, 5)

        # Create collection

        # Create empty tree for sides and blocks

        # Add the planes to the empties

        # Start the loop to check for selection

        return {'FINISHED'}
    

    def cleanMountpointSetup(self, context):

        scene = context.scene

        # stop the loop

        # delete planes

        # delete empties

        # delete collection

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

        # Create matrix with bounding box dimensions that are passed to function
        matrix = [[False] * x for r in range(y)]

        # Register existing blocks and remove blocks that are out of bounds
        for b in sideObject.blocks:
            if b is not None:
                if b.x <= x - 1 and b.y <= y - 1:
                    matrix[b.x][b.y] = True
                else:
                    sideObject.blocks.remove(b)

        # Recreate missing blocks
        for row in range(y):
            for col in range(x):
                if matrix[row][col] == False:
                    matrix[row][col] = True
                    item = sideObject.blocks.add()
                    item.x = row
                    item.y = col
    
    def recreateSquares(context, block, squaresPerAxis):
        """Iterates through squares of a mountpoint side's blocks and adds their entries if necessary"""

        scene = context.scene

        # Create matrix with given dimensions
        matrix = [[False] * squaresPerAxis for r in range(squaresPerAxis)]

        # Register existing square entries and remove squares out of bounds
        for s in block.squares:
            if s is not None:
                if s.x <= x - 1 and s.y <= y - 1:
                    matrix[s.x][s.y] = True
                else:
                    block.squares.remove(s)

        # Recreate missing squares
        for row in range(squaresPerAxis):
            for col in range(squaresPerAxis):
                if matrix[row][col] == False:
                    matrix[row][col] = True
                    item = block.squares.add()
                    item.x = row
                    item.y = col
                    item.valid = False
import bpy

from math           import pi
from bpy.types      import Operator
from collections    import OrderedDict

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection, isCollectionExcluded
from .seut_utils                    import getParentCollection, linkSubpartScene, unlinkSubpartScene

mirroringPresets = OrderedDict([
    ('None', (0.0, 0.0, 0.0)),
    ('X', (180.0, 0.0, 0.0)),
    ('Y', (0.0, 0.0, 180.0)),
    ('Z', (0.0, 180.0, 0.0)),
    ('HalfX', (90.0, 0.0, 0.0)),
    ('HalfY', (0.0, 0.0, -90.0)),
    ('HalfZ', (0.0, -90.0, 0.0)),
    ('MinusHalfX', (-90.0, 0.0, 0.0)),
    ('MinusHalfY', (0.0, 0.0, 90.0)),
    ('MinusHalfZ', (0.0, 90.0, 0.0)),
    ('XHalfY', (180.0, 0.0, -90.0)),
    ('XHalfZ', (180.0, 90.0, 0.0)),
    ('YHalfX', (90.0, 0.0, 180.0)),
    ('YHalfZ', (0.0, -90.0, 180.0)),
    ('ZHalfX', (-90.0, 0.0, 180.0)),
    ('ZHalfY', (0.0, 180.0, -90.0)),
    ('UnsupportedXY1', (90.0, 0.0, 90.0)),
    ('UnsupportedXY2', (-90.0, 0.0, 90.0)),
    ('UnsupportedXY3', (90.0, 0.0, -90.0)),
    ('UnsupportedXY4', (-90.0, 0.0, -90.0)),
    ('UnsupportedXZ1', (90.0, 90.0, 0.0)),
    ('UnsupportedXZ2', (-90.0, 90.0, 0.0)),
    ('UnsupportedXZ3', (90.0, -90.0, 0.0)),
    ('UnsupportedXZ4', (-90.0, -90.0, 0.0)),
])

class SEUT_OT_Mirroring(Operator):
    """Handles setup of mirroring options"""
    bl_idname = "object.mirroring"
    bl_label = "Mirroring"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.mirroringToggle == 'on':
            SEUT_OT_Mirroring.mirroringSetup(self, context)

        elif scene.seut.mirroringToggle == 'off':
            SEUT_OT_Mirroring.cleanMirroringSetup(self, context)

        return {'FINISHED'}
    

    def mirroringSetup(self, context):
        """Sets up mirroring utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)
        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children

        if collections['seut'] is None:
            print("SEUT Warning: Collection 'SEUT " + scene.name + "' not found. Action not possible. (002)")
            scene.seut.mirroringToggle = 'off'
            return

        isExcluded = isCollectionExcluded(collections['seut'].name, allCurrentViewLayerCollections)
        if isExcluded or isExcluded is None:
            print("SEUT Warning: Collection 'SEUT " + scene.name + "' excluded from view layer. Action not possible. (019)")
            scene.seut.mirroringToggle = 'off'
            return

        result = errorCollection(self, context, collections['main'], True)
        if not result == 'CONTINUE':
            scene.seut.mirroringToggle = 'off'
            return
            
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Create collection if it doesn't exist already
        if not 'Mirroring' + tag in bpy.data.collections:
            collection = bpy.data.collections.new('Mirroring' + tag)
            collections['seut'].children.link(collection)
        else:
            collection = bpy.data.collections['Mirroring' + tag]
            try:
                collections['seut'].children.link(collection)
            except:
                pass
        
        # Compile rotation / position / size information
        emptyXRotRaw = mirroringPresets[scene.seut.mirroring_X]
        emptyYRotRaw = mirroringPresets[scene.seut.mirroring_Y]
        emptyZRotRaw = mirroringPresets[scene.seut.mirroring_Z]
        emptyXRotation = ((pi * emptyXRotRaw[0] / 180), (pi * emptyXRotRaw[1] / 180), (pi * emptyXRotRaw[2] / 180))
        emptyYRotation = ((pi * emptyYRotRaw[0] / 180), (pi * emptyYRotRaw[1] / 180), (pi * emptyYRotRaw[2] / 180))
        emptyZRotation = ((pi * emptyZRotRaw[0] / 180), (pi * emptyZRotRaw[1] / 180), (pi * emptyZRotRaw[2] / 180))

        factor = 1
        if scene.seut.gridScale == 'large': factor = 2.5
        if scene.seut.gridScale == 'small': factor = 0.5

        size = 1
        if scene.seut.bBox_X > size: size = scene.seut.bBox_X
        if scene.seut.bBox_Y > size: size = scene.seut.bBox_Y
        if scene.seut.bBox_Z > size: size = scene.seut.bBox_Z
        emptySize = size * factor

        offset = size * factor * factor

        # Create empties (using property rotation info) with certain distance from bounding box
        bpy.ops.object.add(type='EMPTY', location=(offset, 0.0, 0.0), rotation=emptyXRotation)
        emptyX = bpy.context.view_layer.objects.active
        emptyX.name = 'Mirroring X'
        emptyX.empty_display_type = 'ARROWS'
        emptyX.empty_display_size = emptySize

        bpy.ops.object.add(type='EMPTY', location=(0.0, offset, 0.0), rotation=emptyYRotation)
        emptyY = bpy.context.view_layer.objects.active
        emptyY.name = 'Mirroring Y'
        emptyY.empty_display_type = 'ARROWS'
        emptyY.empty_display_size = emptySize

        bpy.ops.object.add(type='EMPTY', location=(0.0, 0.0, offset), rotation=emptyZRotation)
        emptyZ = bpy.context.view_layer.objects.active
        emptyZ.name = 'Mirroring Z'
        emptyZ.empty_display_type = 'ARROWS'
        emptyZ.empty_display_size = emptySize

        parentCollection = getParentCollection(context, emptyX)
        if parentCollection != collection:
            collection.objects.link(emptyX)
            collection.objects.link(emptyY)
            collection.objects.link(emptyZ)

            if parentCollection is None:
                scene.collection.objects.unlink(emptyX)
                scene.collection.objects.unlink(emptyY)
                scene.collection.objects.unlink(emptyZ)
            else:
                parentCollection.objects.unlink(emptyX)
                parentCollection.objects.unlink(emptyY)
                parentCollection.objects.unlink(emptyZ)

        # Instance main collection or mirroringScene main collection under empties
        sourceScene = scene
        if scene.seut.mirroringScene is not None:
            sourceScene = scene
        
        emptyX.seut.linkedScene = sourceScene
        linkSubpartScene(self, scene, emptyX, collection)
        emptyY.seut.linkedScene = sourceScene
        linkSubpartScene(self, scene, emptyY, collection)
        emptyZ.seut.linkedScene = sourceScene
        linkSubpartScene(self, scene, emptyZ, collection)

        return {'FINISHED'}
    

    def cleanMirroringSetup(self, context):
        """Cleans up mirroring utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Save empty rotation values to properties, delete children instances, remove empty
        for empty in scene.objects:
            if empty is not None and empty.type == 'EMPTY' and (empty.name == 'Mirroring X' or empty.name == 'Mirroring Y' or empty.name == 'Mirroring Z'):
                SEUT_OT_Mirroring.saveRotationToProps(self, context, empty)
                if len(empty.children) > 0:
                    unlinkSubpartScene(empty)
                empty.select_set(state=False, view_layer=context.window.view_layer)
                bpy.data.objects.remove(empty)

        # Delete collection
        if 'Mirroring' + tag in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections['Mirroring' + tag])

        return {'FINISHED'}
    

    def saveRotationToProps(self, context, empty):
        """Saves the current rotation values of an empty to the scene properties"""

        scene = context.scene
        rotation = bpy.data.objects[empty.name].rotation_euler
        rotConverted = (round(rotation[0] * 180 / pi), round(rotation[1] * 180 / pi), round(rotation[2] * 180 / pi))

        found = False
        for key, value in mirroringPresets.items():
            if value == rotConverted:
                found = True
                if empty.name.find("Mirroring X") != -1:
                    scene.seut.mirroring_X = key
                elif empty.name.find("Mirroring Y") != -1:
                    scene.seut.mirroring_Y = key
                elif empty.name.find("Mirroring Z") != -1:
                    scene.seut.mirroring_Z = key
                print("SEUT Info: Empty '" + empty.name + "' rotation " + str(rotConverted) + " registered as: " + str(key))
        
        if not found:
            print("SEUT Error: Empty '" + empty.name + "' has incorrect rotation value: " + str(rotConverted) + " (023)")

        return


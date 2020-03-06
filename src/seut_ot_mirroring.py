import bpy

from math           import pi
from bpy.types      import Operator
from collections    import OrderedDict

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection, isCollectionExcluded, showError
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
    bl_idname = "scene.mirroring"
    bl_label = "Mirroring"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.mirroringToggle == 'off':
            result = SEUT_OT_Mirroring.cleanMirroringSetup(self, context)

        # There may be trouble with multiple modes being active at the same time so I'm going to disable the other ones for all scenes, as well as this one for all scenes but the active one
        elif scene.seut.mirroringToggle == 'on':
            for scn in bpy.data.scenes:
                context.window.scene = scn
                if scn.seut.mountpointToggle == 'on' or scn.seut.renderToggle == 'on':
                    scn.seut.mountpointToggle = 'off'
                    scn.seut.renderToggle = 'off'
                if scn != scene:
                    scn.seut.mirroringToggle = 'off'

            context.window.scene = scene
            result = SEUT_OT_Mirroring.mirroringSetup(self, context)

        return result
    

    def mirroringSetup(self, context):
        """Sets up mirroring utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children

        currentArea = context.area.type
        context.area.type = 'VIEW_3D'
        if bpy.context.object is not None and bpy.context.object.mode is not 'OBJECT':
            currentMode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        if collections['seut'] is None:
            showError(context, "Report: Error", "SEUT Error: Collection 'SEUT " + scene.name + "' not found. Action not possible. (002)")
            scene.seut.mirroringToggle = 'off'
            return

        isExcluded = isCollectionExcluded(collections['seut'].name, allCurrentViewLayerCollections)
        if isExcluded or isExcluded is None:
            showError(context, "Report: Error", "SEUT Error: Collection 'SEUT " + scene.name + "' excluded from view layer. Action not possible. (019)")
            scene.seut.mirroringToggle = 'off'
            return

        result = errorCollection(self, scene, collections['main'], True)
        if not result == {'CONTINUE'}:
            scene.seut.mirroringToggle = 'off'
            return

        presetMat = None
        matXfound = False
        matYfound = False
        matZfound = False
        for mat in bpy.data.materials:
            if mat.name == 'SMAT_Mirror_X':
                matX = mat
                matXfound = True
            elif mat.name == 'SMAT_Mirror_Y':
                matY = mat
                matYfound = True
            elif mat.name == 'SMAT_Mirror_Z':
                matZ = mat
                matZfound = True
        
        if not matXfound or not matYfound or not matZfound:
            showError(context, "Report: Error", "SEUT Error: Cannot find mirror axis materials. Re-link 'MatLib_Presets.blend'! (026)")
            scene.seut.mirroringToggle = 'off'
            return {'CANCELLED'}
            
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

        offset = (size * 2 + size / 2) * factor

        ninetyDeg = pi * 90 / 180

        # Create empties (using property rotation info) with certain distance from bounding box
        bpy.ops.object.add(type='EMPTY', location=(offset, 0.0, 0.0), rotation=emptyXRotation)
        emptyX = bpy.context.view_layer.objects.active
        emptyX.name = 'Mirroring X'
        emptyX.empty_display_type = 'ARROWS'
        emptyX.empty_display_size = emptySize
        bpy.ops.mesh.primitive_plane_add(size=emptySize * 2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(offset / 2, 0.0, 0.0), rotation=(0.0, ninetyDeg, 0.0))
        planeX = bpy.context.view_layer.objects.active
        planeX.name = 'X Axis Mirror Plane'
        planeX.active_material = matX

        bpy.ops.object.add(type='EMPTY', location=(0.0, offset, 0.0), rotation=emptyYRotation)
        emptyY = bpy.context.view_layer.objects.active
        emptyY.name = 'Mirroring Y'
        emptyY.empty_display_type = 'ARROWS'
        emptyY.empty_display_size = emptySize
        bpy.ops.mesh.primitive_plane_add(size=emptySize * 2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, offset / 2, 0.0), rotation=(ninetyDeg, 0.0, 0.0))
        planeY = bpy.context.view_layer.objects.active
        planeY.name = 'Y Axis Mirror Plane'
        planeY.active_material = matY

        bpy.ops.object.add(type='EMPTY', location=(0.0, 0.0, offset), rotation=emptyZRotation)
        emptyZ = bpy.context.view_layer.objects.active
        emptyZ.name = 'Mirroring Z'
        emptyZ.empty_display_type = 'ARROWS'
        emptyZ.empty_display_size = emptySize
        bpy.ops.mesh.primitive_plane_add(size=emptySize * 2, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, offset / 2), rotation=(0.0, 0.0, ninetyDeg))
        planeZ = bpy.context.view_layer.objects.active
        planeZ.name = 'Z Axis Mirror Plane'
        planeZ.active_material = matZ

        parentCollection = getParentCollection(context, emptyX)
        if parentCollection != collection:
            collection.objects.link(emptyX)
            collection.objects.link(emptyY)
            collection.objects.link(emptyZ)
            collection.objects.link(planeX)
            collection.objects.link(planeY)
            collection.objects.link(planeZ)

            if parentCollection is None:
                scene.collection.objects.unlink(emptyX)
                scene.collection.objects.unlink(emptyY)
                scene.collection.objects.unlink(emptyZ)
                scene.collection.objects.unlink(planeX)
                scene.collection.objects.unlink(planeY)
                scene.collection.objects.unlink(planeZ)
            else:
                parentCollection.objects.unlink(emptyX)
                parentCollection.objects.unlink(emptyY)
                parentCollection.objects.unlink(emptyZ)
                parentCollection.objects.unlink(planeX)
                parentCollection.objects.unlink(planeY)
                parentCollection.objects.unlink(planeZ)

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
            
        # Reset interaction mode
        try:
            if bpy.context.object is not None and currentMode is not None:
                bpy.ops.object.mode_set(mode=currentMode)
        except:
            pass

        context.area.type = currentArea

        return {'FINISHED'}
    

    def cleanMirroringSetup(self, context):
        """Cleans up mirroring utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        # If mode is not object mode, export fails horribly.
        currentArea = context.area.type
        context.area.type = 'VIEW_3D'
        if bpy.context.object is not None and bpy.context.object.mode is not 'OBJECT':
            currentMode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Save empty rotation values to properties, delete children instances, remove empty
        for obj in scene.objects:
            if obj is not None and obj.type == 'EMPTY' and (obj.name == 'Mirroring X' or obj.name == 'Mirroring Y' or obj.name == 'Mirroring Z'):
                SEUT_OT_Mirroring.saveRotationToProps(self, context, obj)
                if len(obj.children) > 0:
                    unlinkSubpartScene(obj)
                obj.select_set(state=False, view_layer=context.window.view_layer)
                bpy.data.objects.remove(obj)
            elif obj.name == 'X Axis Mirror Plane' or obj.name == 'X Axis Mirror Plane' or obj.name == 'X Axis Mirror Plane':
                obj.select_set(state=False, view_layer=context.window.view_layer)
                bpy.data.objects.remove(obj)
    
        # Delete collection
        if 'Mirroring' + tag in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections['Mirroring' + tag])
            
        # Reset interaction mode
        try:
            if bpy.context.object is not None and currentMode is not None:
                bpy.ops.object.mode_set(mode=currentMode)
        except:
            pass

        context.area.type = currentArea

        return {'FINISHED'}
    

    def saveRotationToProps(self, context, empty):
        """Saves the current rotation values of an empty to the scene properties"""

        scene = context.scene
        rotation = bpy.data.objects[empty.name].rotation_euler
        rotX = round(rotation[0] * 180 / pi)
        rotY = round(rotation[1] * 180 / pi)
        rotZ = round(rotation[2] * 180 / pi)

        if rotX == -180:
            rotX = 180
        elif rotX == 270:
            rotX = -90
        elif rotX == -270:
            rotX = 90
        elif rotX == -0:
            rotX = 0

        if rotY == -180:
            rotY = 180
        elif rotY == 270:
            rotY = -90
        elif rotY == -270:
            rotY = 90
        elif rotY == -0:
            rotY = 0

        if rotZ == -180:
            rotZ = 180
        elif rotZ == 270:
            rotZ = -90
        elif rotZ == -270:
            rotZ = 90
        elif rotZ == -0:
            rotZ = 0

        rotConverted = (rotX, rotY, rotZ)

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
            showError(context, "Report: Error", "SEUT Error: Empty '" + empty.name + "' has incorrect rotation value: " + str(rotConverted) + " (023)")

        return


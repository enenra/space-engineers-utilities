import bpy

from math           import pi
from bpy.types      import Operator

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection, isCollectionExcluded, showError
from .seut_utils                    import getParentCollection, toRadians

class SEUT_OT_IconRender(Operator):
    """Handles functionality regarding icon rendering"""
    bl_idname = "scene.icon_render"
    bl_label = "Icon Render"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.renderToggle == 'off':
            result = SEUT_OT_IconRender.cleanRenderSetup(self, context)

        # There may be trouble with multiple modes being active at the same time so I'm going to disable the other ones for all scenes, as well as this one for all scenes but the active one
        elif scene.seut.renderToggle == 'on':
            for scn in bpy.data.scenes:
                context.window.scene = scn
                if scn.seut.mirroringToggle == 'on' or scn.seut.mountpointToggle == 'on':
                    scn.seut.mirroringToggle = 'off'
                    scn.seut.mountpointToggle = 'off'
                if scn != scene:
                    scn.seut.renderToggle = 'off'

            context.window.scene = scene
            result = SEUT_OT_IconRender.renderSetup(self, context)

        return result
    

    def renderSetup(self, context):
        """Sets up render utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children

        try:
            currentArea = context.area.type
            context.area.type = 'VIEW_3D'
        except AttributeError:
            context.area.type = 'VIEW_3D'
            currentArea = context.area.type

        if context.object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
            context.object.select_set(False)
            context.view_layer.objects.active = None

        if collections['seut'] is None:
            showError(context, "Report: Error", "SEUT Error: Collection 'SEUT (" + scene.name + ")' not found. Action not possible. (002)")
            scene.seut.renderToggle = 'off'
            return {'CANCELLED'}

        isExcluded = isCollectionExcluded(collections['seut'].name, allCurrentViewLayerCollections)
        if isExcluded or isExcluded is None:
            showError(context, "Report: Error", "SEUT Error: Collection 'SEUT " + scene.name + "' excluded from view layer. Action not possible. (019)")
            scene.seut.renderToggle = 'off'
            return {'CANCELLED'}
            
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Create collection if it doesn't exist already
        if not 'Render' + tag in bpy.data.collections:
            collection = bpy.data.collections.new('Render' + tag)
            collections['seut'].children.link(collection)
        else:
            collection = bpy.data.collections['Render' + tag]
            try:
                collections['seut'].children.link(collection)
            except:
                pass


        # Spawn holder empty
        bpy.ops.object.add(type='EMPTY', location=scene.seut.renderEmptyLocation, rotation=scene.seut.renderEmptyRotation)
        empty = bpy.context.view_layer.objects.active
        empty.scale.x = scene.seut.renderDistance
        empty.scale.y = scene.seut.renderDistance
        empty.scale.z = scene.seut.renderDistance
        empty.name = 'Icon Render'
        empty.empty_display_type = 'SPHERE'
        
        # Spawn camera
        bpy.ops.object.camera_add(location=(0.0, -15, 0.0), rotation=(toRadians(90), 0.0, 0.0))
        camera = bpy.context.view_layer.objects.active
        camera.parent = empty
        scene.camera = camera
        camera.name = 'ICON'
        camera.data.name = 'ICON'
        camera.data.lens = scene.seut.renderZoom

        # Spawn lights
        bpy.ops.object.light_add(type='POINT', location=(-12.5, -12.5, 5.0), rotation=(0.0, 0.0, 0.0))
        keyLight = bpy.context.view_layer.objects.active
        keyLight.parent = empty
        keyLight.name = 'Key Light'
        keyLight.data.energy = 7500.0 * scene.seut.renderDistance
        
        bpy.ops.object.light_add(type='POINT', location=(10.0, -10.0, -2.5), rotation=(0.0, 0.0, 0.0))
        fillLight = bpy.context.view_layer.objects.active
        fillLight.parent = empty
        fillLight.name = 'Fill Light'
        fillLight.data.energy = 5000.0 * scene.seut.renderDistance
        
        bpy.ops.object.light_add(type='SPOT', location=(0.0, 15.0, 0.0), rotation=(toRadians(-90), 0.0, 0.0))
        rimLight = bpy.context.view_layer.objects.active
        rimLight.parent = empty
        rimLight.name = 'Rim Light'
        rimLight.data.energy = 10000.0 * scene.seut.renderDistance
        
        parentCollection = getParentCollection(context, empty)
        if parentCollection != collection:
            collection.objects.link(empty)
            collection.objects.link(camera)
            collection.objects.link(keyLight)
            collection.objects.link(fillLight)
            collection.objects.link(rimLight)

            if parentCollection is None:
                scene.collection.objects.unlink(empty)
                scene.collection.objects.unlink(camera)
                scene.collection.objects.unlink(keyLight)
                scene.collection.objects.unlink(fillLight)
                scene.collection.objects.unlink(rimLight)
            else:
                parentCollection.objects.unlink(empty)
                parentCollection.objects.unlink(camera)
                parentCollection.objects.unlink(keyLight)
                parentCollection.objects.unlink(fillLight)
                parentCollection.objects.unlink(rimLight)

        # Spawn compositor node tree
        scene.use_nodes = True

        tree = scene.node_tree

        tree.nodes.clear()

        node_renderLayers = tree.nodes.new(type='CompositorNodeRLayers')
        node_colorCorrection = tree.nodes.new(type='CompositorNodeColorCorrection')
        node_RGB = tree.nodes.new(type='CompositorNodeRGB')
        node_mixRGB = tree.nodes.new(type='CompositorNodeMixRGB')
        node_outputFile = tree.nodes.new(type='CompositorNodeOutputFile')
        node_viewer = tree.nodes.new(type='CompositorNodeViewer')

        tree.links.new(node_renderLayers.outputs[0], node_colorCorrection.inputs[0])
        tree.links.new(node_colorCorrection.outputs[0], node_mixRGB.inputs[1])
        tree.links.new(node_RGB.outputs[0], node_mixRGB.inputs[2])
        tree.links.new(node_mixRGB.outputs[0], node_outputFile.inputs[0])
        tree.links.new(node_mixRGB.outputs[0], node_viewer.inputs[0])

        node_colorCorrection.midtones_gain = 2.0
        node_colorCorrection.shadows_gain = 2.5

        node_RGB.outputs[0].default_value = (0.23074, 0.401978, 0.514918, 1)  # 84AABE
        
        node_mixRGB.blend_type = 'COLOR'

        # Force update render resolution
        scene.seut.renderResolution = scene.seut.renderResolution
        scene.render.engine = 'BLENDER_EEVEE'
        scene.render.film_transparent = True

        context.active_object.select_set(state=False, view_layer=context.window.view_layer)

        context.area.type = currentArea
        
        return {'FINISHED'}


    def cleanRenderSetup(self, context):
        """Clean up render utilities"""

        scene = context.scene

        # If mode is not object mode, export fails horribly.
        try:
            currentArea = context.area.type
            context.area.type = 'VIEW_3D'
        except AttributeError:
            context.area.type = 'VIEW_3D'
            currentArea = context.area.type
            
        if context.object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
            context.object.select_set(False)
            context.view_layer.objects.active = None

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Delete objects
        for obj in scene.objects:
            if obj is not None and obj.type == 'EMPTY':
                if obj.name == 'Icon Render':
                    for child in obj.children:
                        if child.data is not None:
                            if child.type == 'CAMERA':
                                bpy.data.cameras.remove(child.data)
                            elif child.type == 'LIGHT':
                                bpy.data.lights.remove(child.data)

                    obj.select_set(state=False, view_layer=context.window.view_layer)
                    bpy.data.objects.remove(obj)
    
        # Delete collection
        if 'Render' + tag in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections['Render' + tag])

        # Delete Node Tree
        try:
            scene.node_tree.nodes.clear()
        except AttributeError:
            pass

        context.area.type = currentArea


        return {'FINISHED'}
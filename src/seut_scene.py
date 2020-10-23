import bpy
import os

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty,
                        CollectionProperty
                        )

from .seut_mirroring                import clean_mirroring, setup_mirroring
from .seut_mountpoints              import clean_mountpoints, setup_mountpoints
from .seut_icon_render              import clean_icon_render, setup_icon_render
from .seut_collections              import get_collections, rename_collections, names
from .seut_errors                   import seut_report, check_export
from .seut_utils                    import link_subpart_scene, unlink_subpart_scene, to_radians, get_parent_collection, toggle_scene_modes


def update_GridScale(self, context):
    
    scene = context.scene

    # Grid scale is SE block size divided by 2 because else the lines don't line up with the block edges.
    if scene.seut.gridScale == 'small':
        scale = 0.25
    else:
        scale = 1.25

    # It needs to be set for all viewports in all workspaces.
    for area in context.screen.areas:
        if not area.type == 'VIEW_3D':
            continue

        else:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.grid_scale = scale
                    break

    bpy.ops.object.bbox('INVOKE_DEFAULT')


def update_MirroringToggle(self, context):
    scene = context.scene
    toggle_mode(self, context, 'MIRRORING')


def update_mirroringScene(self, context):
    scene = context.scene
    target_scene = scene.seut.mirroringScene

    if target_scene is None:
        for scn in bpy.data.scenes:
            if scn.seut.mirroringScene == scene:
                scn.seut.mirroringScene = None

    elif target_scene is not None and target_scene.seut.mirroringScene is None or target_scene.seut.mirroringScene is not scene:
        self.mirroringScene.seut.mirroringScene = scene

    toggle_mode(self, context, 'MIRRORING')


def update_MountpointToggle(self, context):  
    scene = context.scene
    toggle_mode(self, context, 'MOUNTPOINT')


def update_RenderToggle(self, context):
    scene = context.scene
    toggle_mode(self, context, 'ICON_RENDER')


def toggle_mode(self, context, mode: str):
    """Toggles the passed mode on and all other modes off, in all scenes."""

    scene = context.scene

    if mode == 'MIRRORING':
        if self.mirroringToggle == 'off':
            clean_mirroring(self, context)

        elif self.mirroringToggle == 'on':
            clean_mirroring(self, context)
            toggle_scene_modes(context, 'on', 'off', 'off')
            setup_mirroring(self, context)

    elif mode == 'MOUNTPOINT':
        if self.mountpointToggle == 'off':
            clean_mountpoints(self, context)

        elif self.mountpointToggle == 'on':
            clean_mountpoints(self, context)
            toggle_scene_modes(context, 'off', 'on', 'off')
            setup_mountpoints(self, context)

    elif mode == 'ICON_RENDER':
        if self.renderToggle == 'off':
            clean_icon_render(self, context)

        elif self.renderToggle == 'on':
            clean_icon_render(self, context)
            toggle_scene_modes(context, 'off', 'off', 'on')
            setup_icon_render(self, context)


def update_RenderResolution(self, context):
    scene = context.scene

    scene.render.resolution_x = scene.seut.renderResolution
    scene.render.resolution_y = scene.seut.renderResolution


def update_renderEmptyRotation(self, context):
    scene = context.scene

    empty = bpy.data.objects['Icon Render']
    if empty is not None:
        empty.rotation_euler = scene.seut.renderEmptyRotation


def update_renderEmptyLocation(self, context):
    scene = context.scene

    empty = bpy.data.objects['Icon Render']
    if empty is not None:
        empty.location = scene.seut.renderEmptyLocation


def update_renderColorOverlay(self, context):
    scene = context.scene

    if scene.node_tree.nodes['RGB'] is not None:
        scene.node_tree.nodes['RGB'].mute = scene.seut.renderColorOverlay


def update_renderZoom(self, context):
    scene = context.scene

    camera = bpy.data.objects['ICON']
    if camera is not None:
        camera.data.lens = scene.seut.renderZoom


def update_renderDistance(self, context):
    scene = context.scene

    empty = bpy.data.objects['Icon Render']
    if empty is not None:
        empty.scale.x = self.renderDistance
        empty.scale.y = self.renderDistance
        empty.scale.z = self.renderDistance

    key_light = bpy.data.objects['Key Light']
    if key_light is not None:
        key_light.data.energy = 7500.0 * scene.seut.renderDistance
        
    fill_light = bpy.data.objects['Fill Light']
    if fill_light is not None:
        fill_light.data.energy = 5000.0 * scene.seut.renderDistance
        
    rim_light = bpy.data.objects['Rim Light']
    if rim_light is not None:
        rim_light.data.energy = 10000.0 * scene.seut.renderDistance


def update_subtypeId(self, context):
    scene = context.scene

    if scene.seut.subtypeId == "":
        scene.seut.subtypeId = scene.name
        scene.seut.subtypeBefore = scene.name

    # If the subtypeId already exists for a scene in the file, prevent it from being set
    for scn in bpy.data.scenes:
        if scn is not scene and scn.seut.subtypeId == scene.seut.subtypeId:
            scene.seut.subtypeId = scene.seut.subtypeBefore
            seut_report(self, context, 'ERROR', False, 'E018')
            return

    if scene.seut.subtypeId != scene.seut.subtypeBefore and scene.seut.subtypeBefore is not "":
        rename_collections(scene)
        scene.seut.subtypeBefore = scene.seut.subtypeId
        
    scene.name = scene.seut.subtypeId


def update_linkSubpartInstances(self, context):
    scene = context.scene
    collections = get_collections(scene)

    for col in collections.values():
        if col is not None:
            for empty in col.objects:
                if empty is not None and empty.type == 'EMPTY' and empty.name.find('(L)') == -1 and empty.seut.linkedScene is not None and empty.seut.linkedScene.name in bpy.data.scenes:

                    collection_type = 'main'
                    for key in names.keys():
                        if col == collections[key]:
                            collection_type = key
                            break

                    if scene.seut.linkSubpartInstances:
                        link_subpart_scene(self, scene, empty, col, collection_type)
                    else:
                        unlink_subpart_scene(empty)


def update_export_largeGrid(self, context):
    scene = context.scene

    if not self.export_smallGrid and not self.export_largeGrid:
        self.export_smallGrid = True


def update_export_smallGrid(self, context):
    scene = context.scene

    if not self.export_largeGrid and not self.export_smallGrid:
        self.export_largeGrid = True


def update_export_exportPath(self, context):
    scene = context.scene

    if self.export_exportPath == "":
        return

    if os.path.isdir(bpy.path.abspath(self.export_exportPath)):
        if check_export(self, context, False) == {'CANCELLED'}:
            self.export_exportPath = ""


def poll_linkedScene(self, object):
    return object != bpy.context.scene and object.seut.sceneType == 'mainScene'


class SEUT_MountpointAreas(PropertyGroup):
    
    side: EnumProperty(
    name='Side',
    items=(
        ('front', 'Front', ''),
        ('back', 'Back', ''),
        ('left', 'Left', ''),
        ('right', 'Right', ''),
        ('top', 'Top', ''),
        ('bottom', 'Bottom', '')
        ),
    default='front'        
    )
    x: FloatProperty(
        name="Location X",
        default=0
    )
    y: FloatProperty(
        name="Location Y",
        default=0
    )
    xDim: FloatProperty(
        name="Dimension X",
        default=0
    )
    yDim: FloatProperty(
        name="Dimension Y",
        default=0
    )
    default: BoolProperty(
        name="Default",
        default=False
    )
    pressurized: BoolProperty(
        name="Pressurized",
        default=False
    )


class SEUT_Scene(PropertyGroup):
    """Holder for the various scene properties"""

    sceneType: EnumProperty(
        name='Type',
        items=(
            ('mainScene', 'Main', 'This scene is a main scene'),
            ('subpart', 'Subpart', 'This scene is a subpart of a main scene'),
            ('character', 'Character ', 'This scene contains a character model'),
            ('character_animation', 'Character Animation', 'This scene contains a character animation or pose'),
            ),
        default='mainScene'
    )
    linkSubpartInstances: BoolProperty(
        name="Link Subpart Instances",
        description="Whether to link instances of subparts to their empties",
        default=True,
        update=update_linkSubpartInstances
    )
    subtypeId: StringProperty(
        name="SubtypeId",
        description="The SubtypeId for this model",
        update=update_subtypeId
    )
    subtypeBefore: StringProperty(
        name="Previous SubtypeId"
    )

    # Grid Scale
    gridScale: EnumProperty(
        name='Scale',
        items=(
            ('large', 'Large', 'Large grid blocks (2.5m)', 'MESH_CUBE', 1),
            ('small', 'Small', 'Small grid blocks (0.5m)', 'META_CUBE', 2)
            ),
        default='large',
        update=update_GridScale
    )

    # Bounding Box
    bBox_X: IntProperty(
        name="X:",
        description="",
        default=1,
        min=1
    )
    bBox_Y: IntProperty(
        name="Y:",
        description="",
        default=1,
        min=1
    )
    bBox_Z: IntProperty(
        name="Z:",
        description="",
        default=1,
        min=1
    )

    # Mirroing
    mirroringToggle: EnumProperty(
        name='Mirroring',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_MirroringToggle
    )
    mirroring_X: EnumProperty(
        name='Mirroring X',
        items=(
            ('None', 'None', ''),
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('HalfX', 'HalfX', ''),
            ('HalfY', 'HalfY', ''),
            ('HalfZ', 'HalfZ', ''),
            ('MinusHalfX', 'MinusHalfX', ''),
            ('MinusHalfY', 'MinusHalfY', ''),
            ('MinusHalfZ', 'MinusHalfZ', ''),
            ('XHalfY', 'XHalfY', ''),
            ('XHalfZ', 'XHalfZ', ''),
            ('YHalfX', 'YHalfX', ''),
            ('YHalfZ', 'YHalfZ', ''),
            ('ZHalfX', 'ZHalfX', ''),
            ('ZHalfY', 'ZHalfY', ''),
            ('UnsupportedXY1', 'UnsupportedXY1', ''),
            ('UnsupportedXY2', 'UnsupportedXY2', ''),
            ('UnsupportedXY3', 'UnsupportedXY3', ''),
            ('UnsupportedXY4', 'UnsupportedXY4', ''),
            ('UnsupportedXZ1', 'UnsupportedXZ1', ''),
            ('UnsupportedXZ2', 'UnsupportedXZ2', ''),
            ('UnsupportedXZ3', 'UnsupportedXZ3', ''),
            ('UnsupportedXZ4', 'UnsupportedXZ4', '')
            ),
        default='None'
    )
    mirroring_Y: EnumProperty(
        name='Mirroring Y',
        items=(
            ('None', 'None', ''),
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('HalfX', 'HalfX', ''),
            ('HalfY', 'HalfY', ''),
            ('HalfZ', 'HalfZ', ''),
            ('MinusHalfX', 'MinusHalfX', ''),
            ('MinusHalfY', 'MinusHalfY', ''),
            ('MinusHalfZ', 'MinusHalfZ', ''),
            ('XHalfY', 'XHalfY', ''),
            ('XHalfZ', 'XHalfZ', ''),
            ('YHalfX', 'YHalfX', ''),
            ('YHalfZ', 'YHalfZ', ''),
            ('ZHalfX', 'ZHalfX', ''),
            ('ZHalfY', 'ZHalfY', ''),
            ('UnsupportedXY1', 'UnsupportedXY1', ''),
            ('UnsupportedXY2', 'UnsupportedXY2', ''),
            ('UnsupportedXY3', 'UnsupportedXY3', ''),
            ('UnsupportedXY4', 'UnsupportedXY4', ''),
            ('UnsupportedXZ1', 'UnsupportedXZ1', ''),
            ('UnsupportedXZ2', 'UnsupportedXZ2', ''),
            ('UnsupportedXZ3', 'UnsupportedXZ3', ''),
            ('UnsupportedXZ4', 'UnsupportedXZ4', '')
            ),
        default='None'
    )
    mirroring_Z: EnumProperty(
        name='Mirroring Z',
        items=(
            ('None', 'None', ''),
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('HalfX', 'HalfX', ''),
            ('HalfY', 'HalfY', ''),
            ('HalfZ', 'HalfZ', ''),
            ('MinusHalfX', 'MinusHalfX', ''),
            ('MinusHalfY', 'MinusHalfY', ''),
            ('MinusHalfZ', 'MinusHalfZ', ''),
            ('XHalfY', 'XHalfY', ''),
            ('XHalfZ', 'XHalfZ', ''),
            ('YHalfX', 'YHalfX', ''),
            ('YHalfZ', 'YHalfZ', ''),
            ('ZHalfX', 'ZHalfX', ''),
            ('ZHalfY', 'ZHalfY', ''),
            ('UnsupportedXY1', 'UnsupportedXY1', ''),
            ('UnsupportedXY2', 'UnsupportedXY2', ''),
            ('UnsupportedXY3', 'UnsupportedXY3', ''),
            ('UnsupportedXY4', 'UnsupportedXY4', ''),
            ('UnsupportedXZ1', 'UnsupportedXZ1', ''),
            ('UnsupportedXZ2', 'UnsupportedXZ2', ''),
            ('UnsupportedXZ3', 'UnsupportedXZ3', ''),
            ('UnsupportedXZ4', 'UnsupportedXZ4', '')
            ),
        default='None'
    )
    mirroringScene: PointerProperty(
        name='Mirror Model',
        description="The scene which contains the (optional) mirror model. Must be set to type: 'Mirroring'",
        type=bpy.types.Scene,
        poll=poll_linkedScene,
        update=update_mirroringScene
    )

    # Mountpoints
    mountpointToggle: EnumProperty(
        name='Mountpoints',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_MountpointToggle
    )
    mountpointAreas: CollectionProperty(
        type=SEUT_MountpointAreas
    )
    

    # Export
    export_deleteLooseFiles: BoolProperty(
        name="Delete Temp Files",
        description="Whether the temporary files should be deleted after the MWM has been created",
        default=True
    )
    export_largeGrid: BoolProperty(
        name="Large",
        description="Whether to export to large grid",
        default=True,
        update=update_export_largeGrid
    )
    export_smallGrid: BoolProperty(
        name="Small",
        description="Whether to export to small grid",
        default=False,
        update=update_export_smallGrid
    )
    export_sbc: BoolProperty(
        name="SBC",
        description="Whether to export to SBC (CubeBlocks definition)",
        default=True
    )
    export_rescaleFactor: FloatProperty(
        name="Rescale Factor:",
        description="What to set the Rescale Factor to",
        default=1,
        min=0
    )
    export_exportPath: StringProperty(
        name="Export Folder",
        description="What folder to export to",
        subtype="DIR_PATH",
        update=update_export_exportPath
    )
    export_lod1Distance: IntProperty(
        name="LOD1:",
        description="From what distance this LOD should display",
        default=25,
        min=0
    )
    export_lod2Distance: IntProperty(
        name="LOD2:",
        description="From what distance this Build Stage LOD should display",
        default=50,
        min=0
    )
    export_lod3Distance: IntProperty(
        name="LOD3:",
        description="From what distance this LOD should display",
        default=150,
        min=0
    )
    export_bs_lodDistance: IntProperty(
        name="BS_LOD:",
        description="From what distance this LOD should display",
        default=50,
        min=0
    )

    # Axis Conversion
    axis_up: EnumProperty(
        name='Up',
        description='Axis Up',
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')
            ),
        default='Y'
    )
    axis_forward: EnumProperty(
        name='Forward',
        description='Axis Forward',
        items=(
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', ''),
            ('-X', '-X', ''),
            ('-Y', '-Y', ''),
            ('-Z', '-Z', '')
            ),
        default='Z'
    )

    # Icon Render
    renderToggle: EnumProperty(
        name='Render',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_RenderToggle
    )
    renderOutputFormat: EnumProperty(
        name='Format',
        items=(
            ('png', 'PNG', 'Render output will be in PNG format'),
            ('tif', 'TIF', 'Render output will be in TIF format'),
            ('dds', 'DDS', 'Render output will be in DDS format')
            ),
        default='png'
    )
    renderColorOverlay: BoolProperty(
        name="Color Overlay",
        description="Whether to overlay the blue color",
        default=False,
        update=update_renderColorOverlay
    )
    renderResolution: IntProperty(
        name="Resolution",
        description="The resolution Blender should render at",
        default=128,
        min=0,
        update=update_RenderResolution
    )
    renderEmptyRotation: FloatVectorProperty(
        name="Rotation",
        description="The rotation of the empty holding the render setup",
        subtype='EULER',
        default=(to_radians(-20), 0.0, to_radians(45)),
        update=update_renderEmptyRotation
    )
    renderEmptyLocation: FloatVectorProperty(
        name="Location",
        description="The location of the empty holding the render setup",
        subtype='XYZ',
        default=(0.0, 0.0, 0.0),
        update=update_renderEmptyLocation
    )
    renderZoom: IntProperty(
        name="Zoom",
        description="The zoom of the camera",
        default=70,
        min=0,
        update=update_renderZoom
    )
    renderDistance: FloatProperty(
        name="Distance",
        description="The distance of the camera and lights from origin",
        default=1,
        min=1,
        max=10,
        update=update_renderDistance
    )
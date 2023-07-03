import collections
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

from .planets.seut_planets          import SEUT_PlanetPropertiesEnvironmentItems, SEUT_PlanetPropertiesMaterialGroups, SEUT_PlanetPropertiesOreMappings, poll_voxelmaterials
from .seut_mirroring                import clean_mirroring, setup_mirroring
from .seut_mountpoints              import clean_mountpoints, setup_mountpoints
from .seut_icon_render              import clean_icon_render, setup_icon_render
from .seut_collections              import get_collections, rename_collections, seut_collections
from .seut_errors                   import get_abs_path, seut_report, check_export
from .seut_utils                    import link_subpart_scene, unlink_subpart_scene, to_radians, get_parent_collection, toggle_scene_modes


def update_sceneType(self, context):
    scene = context.scene
    collections = get_collections(scene, True)

    # There can be only one Planet Editor per BLEND file
    if self.sceneType == 'planet_editor':
        for scn in bpy.data.scenes:
            if scn.seut.sceneType == 'planet_editor' and scn is not scene:
                if self.previous_scene_type == "":
                    self.sceneType = 'mainScene'
                else:
                    self.sceneType = self.previous_scene_type
                seut_report(self, context, 'ERROR', False, 'E048')

    elif self.sceneType == 'character':
        scene.tool_settings.use_auto_normalize = True

    for key, cols in collections.items():
        if cols is None:
            continue
        
        if not key in seut_collections[scene.seut.sceneType] and key != 'seut':
            for col in cols:
                if len(col.objects) <= 0:
                    bpy.data.collections.remove(col)
                else:
                    col.color_tag = 'COLOR_07'
        else:
            for col in cols:
                if col.seut.ref_col is not None and not col.seut.ref_col.seut.col_type in seut_collections[scene.seut.sceneType]:
                    if len(col.objects) <= 0:
                        bpy.data.collections.remove(col)
                    else:
                        col.color_tag = 'COLOR_07'
    
    self.previous_scene_type = self.sceneType


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
    toggle_mode(self, context, 'MOUNTPOINT')


def update_RenderToggle(self, context):
    toggle_mode(self, context, 'ICON_RENDER')


def toggle_mode(self, context, mode: str):
    """Toggles the passed mode on and all other modes off, in all scenes."""

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
    if scene.node_tree.nodes['RGB to BW'] is not None:
        scene.node_tree.nodes['RGB to BW'].mute = scene.seut.renderColorOverlay
    if bpy.app.version < (3, 4, 0):
        if scene.node_tree.nodes['Combine RGBA'] is not None:
            scene.node_tree.nodes['Combine RGBA'].mute = scene.seut.renderColorOverlay
    else:
        if scene.node_tree.nodes['Combine Color'] is not None:
            scene.node_tree.nodes['Combine Color'].mute = scene.seut.renderColorOverlay


def update_renderZoom(self, context):
    scene = context.scene

    camera = bpy.data.objects['ICON']
    if camera is not None:
        camera.data.lens = scene.seut.renderZoom


def update_renderDistance(self, context):
    scene = context.scene

    if 'Icon Render' in bpy.data.objects:
        empty = bpy.data.objects['Icon Render']
        empty.scale.x = self.renderDistance
        empty.scale.y = self.renderDistance
        empty.scale.z = self.renderDistance

    if 'Key Light' in bpy.data.objects:
        key_light = bpy.data.objects['Key Light']
        key_light.data.energy = 7500.0 * scene.seut.renderDistance
    
    if 'Fill Light' in bpy.data.objects:
        fill_light = bpy.data.objects['Fill Light']
        fill_light.data.energy = 5000.0 * scene.seut.renderDistance
    
    if 'Rim Light' in bpy.data.objects:
        rim_light = bpy.data.objects['Rim Light']
        rim_light.data.energy = 10000.0 * scene.seut.renderDistance


def update_subtypeId(self, context):
    scene = context.scene

    if scene.seut.subtypeId == "":
        scene.seut.subtypeId = scene.name
        scene.seut.subtypeBefore = scene.name

    if "\\" in scene.seut.subtypeId or "/" in scene.seut.subtypeId:
        scene.seut.subtypeId = scene.seut.subtypeBefore
        return

    # If the subtypeId already exists for a scene in the file, prevent it from being set
    for scn in bpy.data.scenes:
        if scn is not scene and scn.seut.subtypeId == scene.seut.subtypeId:
            if scene.seut.subtypeBefore == scene.seut.subtypeId:
                scene.seut.subtypeId = f"{scene.seut.subtypeId} ({scene.name})"
            else:
                scene.seut.subtypeId = scene.seut.subtypeBefore
                seut_report(self, context, 'ERROR', False, 'E018')
            return

    if scene.seut.subtypeId != scene.seut.subtypeBefore and scene.seut.subtypeBefore != "":
        rename_collections(scene)
        scene.seut.subtypeBefore = scene.seut.subtypeId

    scene.name = scene.seut.subtypeId


def update_linkSubpartInstances(self, context):
    scene = context.scene
    collections = get_collections(scene)

    for col_type, col in collections.items():
        if col_type == 'main' and not col is None and not col[0] is None:
            for empty in col[0].objects:
                if empty is not None and empty.type == 'EMPTY' and not empty.seut.linked and empty.seut.linkedScene is not None and empty.seut.linkedScene.name in bpy.data.scenes:

                    if scene.seut.linkSubpartInstances:
                        link_subpart_scene(self, scene, empty, col[0])
                    else:
                        unlink_subpart_scene(empty)

        elif col_type in ['bs', 'lod'] and not col is None:
            for sub_col in col:
                for empty in sub_col.objects:
                    if empty is not None and empty.type == 'EMPTY' and not empty.seut.linked and empty.seut.linkedScene is not None and empty.seut.linkedScene.name in bpy.data.scenes:

                        if scene.seut.linkSubpartInstances:
                            link_subpart_scene(self, scene, empty, sub_col)
                        else:
                            unlink_subpart_scene(empty)


def update_export_largeGrid(self, context):

    if not self.export_smallGrid and not self.export_largeGrid:
        self.export_smallGrid = True


def update_export_smallGrid(self, context):

    if not self.export_largeGrid and not self.export_smallGrid:
        self.export_largeGrid = True
    
    if not self.export_smallGrid and self.export_medium_grid:
        self.export_medium_grid = False


def update_export_exportPath(self, context):
    scene = context.scene

    if self.export_exportPath == "":
        return

    path = get_abs_path(self.export_exportPath)

    if not path.startswith(get_abs_path(self.mod_path)):
        seut_report(self, context, 'ERROR', False, 'E045', get_abs_path(self.mod_path))
        self.export_exportPath = ""

    if path.find("Models\\") != -1 or (path + "\\").find("Models\\") != -1:
        pass
    else:
        seut_report(self, context, 'ERROR', False, 'E014', path, scene.name)
        self.export_exportPath = ""


def update_mod_path(self, context):
    scene = context.scene

    if self.mod_path == "":
        return

    if not os.path.isdir(get_abs_path(self.mod_path)):
        seut_report(self, context, 'ERROR', False, 'E003', "Mod", self.mod_path)
        self.mod_path = ""
    
    if self.export_exportPath == "":
        if scene.seut.sceneType in ['mainScene', 'subpart']:
            self.export_exportPath = os.path.join(self.mod_path, "Models", "Cubes", self.gridScale)
        elif scene.seut.sceneType == 'character':
            self.export_exportPath = os.path.join(self.mod_path, "Models", "Characters")
        elif scene.seut.sceneType == 'character_animation':
            self.export_exportPath = os.path.join(self.mod_path, "Models", "Characters", "Animations")
    else:
        self.export_exportPath = os.path.join(self.mod_path, self.export_exportPath[self.export_exportPath.rfind("Models"):])
    
    if scene.render.filepath in ["", "/tmp\\", "//"]:
        scene.render.filepath = os.path.join(get_abs_path(self.mod_path), "Textures", "GUI", "Icons", "Cubes")
    else:
        scene.render.filepath = os.path.join(get_abs_path(self.mod_path), scene.render.filepath[scene.render.filepath.find("Textures"):])


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
    enabled: BoolProperty(
        name="Enabled",
        default=True
    )
    exclusion_mask: IntProperty(
        name="Exclusion Mask",
        default=0,
        min=0,
        max=255
    )
    properties_mask: IntProperty(
        name="Properties Mask",
        default=0,
        min=0,
        max=255
    )


class SEUT_Scene(PropertyGroup):
    """Holder for the various scene properties"""

    version: IntProperty(
        name="SEUT Scene Version",
        description="Used as a reference to patch the SEUT scene propertiesto newer versions",
        default=0 # current: 4
    )

    sceneType: EnumProperty(
        name='Type',
        items=(
            ('mainScene', 'Main', 'This scene is a main scene'),
            ('subpart', 'Subpart', 'This scene is a subpart of a main scene'),
            ('character', 'Character', 'This scene contains a character model'),
            ('character_animation', 'Character Animation', 'This scene contains a character animation or pose'),
            ('planet_editor', 'Planet Editor (Alpha)', 'This scene can be used to create a Space Engineers planet with. Only one can exist per BLEND file'),
            ),
        default='mainScene',
        update=update_sceneType
    )
    previous_scene_type: StringProperty()
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
        description="The scene which contains the (optional) mirror model",
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
        name="Delete Temporary Files",
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
    export_medium_grid: BoolProperty(
        name="Medium",
        description="Use a 3:5 ratio instead of 1:5 when exporting to small grid.\nThis means a 1x1x1 large grid block will be exported to 3x3x3 small grid",
        default=False
    )
    export_sbc_type: EnumProperty(
        name='SBC',
        description="Whether and how to export data to SBC file(s)",
        items=(
            ('none', 'No SBC', 'Do not export data to SBC.'),
            ('update', 'Update', 'Update existing entries, create new ones if missing.'),
            ('new', 'New', 'Only create new files, do not update existing ones.')
            ),
        default='update'
    )
    export_rescaleFactor: FloatProperty(
        name="Rescale Factor:",
        description="What to set the Rescale Factor to",
        default=1,
        min=0
    )
    export_exportPath: StringProperty(
        name="Model Folder",
        description="What folder to export this scene to. Must be located within Mod-folder",
        subtype="DIR_PATH",
        update=update_export_exportPath
    )
    mod_path: StringProperty(
        name="Mod Folder",
        description="The root folder of the mod",
        subtype="DIR_PATH",
        update=update_mod_path
    )

    # These are pre 0.9.95 legacy, not directly used anymore --> moved to being saved onto collections
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
    export_sbc: BoolProperty(
        name="SBC",
        description="Whether to export to SBC (CubeBlocks definition)",
        default=True
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
    render_output_type: EnumProperty(
        name='Format',
        items=(
            ('png', 'PNG', 'Render output will be in PNG format'),
            ('dds', 'DDS', 'Render output will be in DDS format')
            ),
        default='dds'
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
        min=0,
        max=10,
        update=update_renderDistance
    )

    # Planet Editor
    sd_texture: StringProperty(
        name="Texture",
        description="This texture is used like a heightmap on defined slopes in the terrain to add additional detail",
        subtype="FILE_PATH"
    )
    sd_size: IntProperty(
        name="Size",
        description="Defines the size in which the Surface Detail texture is applied to the terrain. Larger values result in less detailed voxel geometry",
        min=0
    )
    sd_scale: IntProperty(
        name="Scale",
        description="Defines how much the generated voxel geometry is offset from the terrain through the Surface Detail texture",
        min=1,
        max=100
    )
    sd_slope_min: IntProperty(
        name="Slope Minimum",
        description="The minimum slope angle (in degrees) the Surface Detail texture should be applied to",
        min=0,
        max=90
    )
    sd_slope_max: IntProperty(
        name="Slope Maximum",
        min=0,
        description="The maximum slope angle (in degrees) the Surface Detail texture should be applied to",
        max=90
    )
    sd_transition: IntProperty(
        name="Transition",
        description="Defines the range of degrees over which the Surface Detail texture fades away",
        min=0
    )
    
    hill_params_min: FloatProperty(
        name="Hills Parameter Minimum",
        min=-1,
        description="The minimum offset by which the terrain is displaced according to the height map",
        max=-0.01
    )
    hill_params_max: FloatProperty(
        name="Hills Parameter Maximum",
        description="The maximum offset by which the terrain is displaced according to the height map",
        min=0.01,
        max=1
    )

    default_surface_temperature: EnumProperty(
        name="Default Surface Temperature",
        description="The default surface temperature of the planet, changing with height",
        items=(
            ('ExtremeFreeze', 'Extreme Freeze', ""),
            ('Freeze', 'Freeze', ""),
            ('Cozy', 'Cozy', ""),
            ('Hot', 'Hot', ""),
            ('ExtremeHot', 'Extreme Hot', "")
            ),
        default='Cozy'
    )
    default_surface_material: PointerProperty(
        name="Default Surface Material",
        description="The default surface voxel material that is placed in all places not covered by a Complex Material rule",
        type=bpy.types.Material,
        poll=poll_voxelmaterials
    )
    default_surface_material_max: IntProperty(
        name="Max Depth",
        description="The max depth to which this voxel material is placed",
        min=0,
        default=10
    )
    default_subsurface_material: PointerProperty(
        name="Default Subsurface Material",
        description="The default subsurface voxel material that is placed in all places not covered by a Complex Material rule",
        type=bpy.types.Material,
        poll=poll_voxelmaterials
    )
    min_surface_layer_depth: IntProperty(
        name="Minimum Surface Layer Depth",
        description="The minimum depth in meters of the surface layer",
        min=0,
        default=1
    )
    
    surface_gravity: FloatProperty(
        name="Surface Gravity",
        description="The gravity on height zero on the planet, falling off with distance",
        min=0,
        default=1.0
    )
    gravity_falloff_power: FloatProperty(
        name="Gravity Falloff Power",
        description="The power to which the gravity falls off after exiting the height defined by Hill Parameter Maximum. The smaller the value, the lower the falloff",
        default=7.0
    )
    has_atmosphere: BoolProperty(
        name="Has Atmosphere",
        description="Whether the planet has an atmosphere or not. False overrides the Oxygen Density property",
        default=True
    )
    atm_breathable: BoolProperty(
        name="Breathable",
        description="Whether the atmosphere is breathable or not. False overrides any Oxygen Density property and prevents oxygen from being gathered by vents",
        default=True
    )
    atm_oxygen_density: FloatProperty(
        name="Oxygen Density",
        description="The ratio of oxygen within air (air being defined as the Air Density property)",
        min=0,
        default=1.0
    )
    atm_density: FloatProperty(
        name="Air Density",
        description="The density of air at height zero, falling off with height. This value directly corresponds to thruster MinPlanetaryInfluence and MaxPlanetaryInfluence settings",
        min=0,
        default=1.0
    )
    atm_limit_altitude: FloatProperty(
        name="Limit Altitude",
        description="Defines how high the atmosphere reaches, relative to the Hill Parameter Maximum property",
        min=0,
        default=1.0
    )
    atm_max_wind_speed: FloatProperty(
        name="Maximum Wind Speed",
        description="The maximum wind speed on a planet. This value can be multiplied by weather effects",
        min=0,
        default=80.0
    )

    material_groups: CollectionProperty(
        type=SEUT_PlanetPropertiesMaterialGroups
    )
    material_groups_index: IntProperty(
        default=0
    )
    material_groups_palette: PointerProperty(
        type=bpy.types.Palette
    )
    environment_items: CollectionProperty(
        type=SEUT_PlanetPropertiesEnvironmentItems
    )
    environment_items_index: IntProperty(
        default=0
    )
    biomes_palette: PointerProperty(
        type=bpy.types.Palette
    )
    ore_mappings: CollectionProperty(
        type=SEUT_PlanetPropertiesOreMappings
    )
    ore_mappings_index: IntProperty(
        default=0
    )
    ore_mappings_palette: PointerProperty(
        type=bpy.types.Palette
    )

    planet: PointerProperty(
        type=bpy.types.Object
    )
    bake_type: EnumProperty(
        name='Bake Type',
        description="Which map type to bake from the current planet material",
        items=(
            ('height', 'Height Map', '', 'BOIDS', 0),
            ('biome', 'Biome Map', '', 'WORLD_DATA', 1),
            ('spots', 'Ore Spots', '', 'OUTLINER_OB_POINTCLOUD', 2)
            ),
        default='height'
    )
    bake_resolution: EnumProperty(
        name='Bake Resolution',
        description="What resolution to bake the selected map type to. Higher resolutions result in higher bake times.\nNote: 128x128 maps are only suitable to do quick tests with",
        items=(
            ('128', '128x128', 'For testing purposes only'),
            ('2048', '2048x2048', 'This is the only viable resolution for normal-sized planets'),
            ('8192', '8192x8192', 'Viable only on oversized planets without additional performance issues')
            ),
        default='2048'
    )
    export_map_height: BoolProperty(
        name="Height Map",
        description="Whether to export the height map",
        default=True
    )
    export_map_biome: BoolProperty(
        name="Biome Map",
        description="Whether to export the biome map",
        default=True
    )
    export_map_spots: BoolProperty(
        name="Ore Spots Map",
        description="Whether to export the ore spots map",
        default=True
    )
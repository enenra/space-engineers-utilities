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

from .seut_ot_mirroring             import SEUT_OT_Mirroring
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import showError
from .seut_utils                    import linkSubpartScene, unlinkSubpartScene, toRadians


# These update_* functions need to be above the class... for some reason.
def update_GridScale(self, context):
    bpy.ops.object.gridscale()
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_MirroringToggle(self, context):
    bpy.ops.scene.mirroring()

def update_mirroringScene(self, context):
    bpy.ops.scene.mirroring()

def update_MountpointToggle(self, context):
    bpy.ops.scene.mountpoints()

def update_RenderToggle(self, context):
    bpy.ops.scene.icon_render()

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

    keyLight = bpy.data.objects['Key Light']
    if keyLight is not None:
        keyLight.data.energy = 7500.0 * scene.seut.renderDistance
        
    fillLight = bpy.data.objects['Fill Light']
    if fillLight is not None:
        fillLight.data.energy = 5000.0 * scene.seut.renderDistance
        
    rimLight = bpy.data.objects['Rim Light']
    if rimLight is not None:
        rimLight.data.energy = 10000.0 * scene.seut.renderDistance

def update_subtypeId(self, context):
    scene = context.scene

    if scene.seut.subtypeId == "":
        scene.seut.subtypeId = scene.name

    # If the subtypeId already exists for a scene in the file, prevent it from being set
    for scn in bpy.data.scenes:
        if scn is not scene and scn.seut.subtypeId == scene.seut.subtypeId:
            scene.seut.subtypeId = scene.seut.subtypeBefore
            showError(context, "Report: Error", "SEUT Error: Cannot set SubtypeId to a SubtypeId that already exists in the file for another scene. (018)")
            return

    if scene.seut.subtypeId != scene.seut.subtypeBefore:
        SEUT_OT_RecreateCollections.rename_Collections(scene)
        scene.seut.subtypeBefore = scene.seut.subtypeId
        
    scene.name = scene.seut.subtypeId

def update_linkSubpartInstances(self, context):
    scene = context.scene
    collections = SEUT_OT_RecreateCollections.getCollections(scene)

    if collections['main'] is None:
        return

    for empty in collections['main'].objects:
        if empty is not None:
            # The check for the empty name prevents this from being run on empties that are linked to this scene.
            if empty.type == 'EMPTY' and empty.name.find('(L)') == -1 and empty.seut.linkedScene is not None and empty.seut.linkedScene.name in bpy.data.scenes:
                if scene.seut.linkSubpartInstances:
                    linkSubpartScene(self, scene, empty, None)
                else:
                    unlinkSubpartScene(empty)


def update_export_exportPath(self, context):
    scene = context.scene

    if self.export_exportPath == "":
        return

    if os.path.isdir(self.export_exportPath):
        if self.export_exportPath.find('Models\\') == -1:
            showError(context, "Report: Error", "SEUT Error: Export path '" + self.export_exportPath + "' does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            self.export_exportPath = ""


def poll_linkedScene(self, object):
    return object != bpy.context.scene and object.seut.sceneType == 'mirror'

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

class SEUT_Scene(PropertyGroup):
    """Holder for the various scene properties"""

    sceneType: EnumProperty(
        name='Type',
        items=(
            ('mainScene', 'Main', 'This scene is a main scene'),
            ('subpart', 'Subpart', 'This scene is a subpart of a main scene'),
            ('mirror', 'Mirroring', 'This scene contains the mirror model of another scene'),
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
            ('large', 'Large', 'Large grid blocks (2.5m)'),
            ('small', 'Small', 'Small grid blocks (0.5m)')
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
        name="Delete Loose Files",
        description="Whether the intermediary files should be deleted after the MWM has been created",
        default=True
    )
    export_fbx: BoolProperty(
        name="FBX",
        description="Whether to export to FBX",
        default=True
    )
    export_xml: BoolProperty(
        name="XML",
        description="Whether to export to XML",
        default=True
    )
    export_hkt: BoolProperty(
        name="HKT",
        description="Whether to export to HKT (Collision model filetype)",
        default=True
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
        default=(toRadians(-20), 0.0, toRadians(45)),
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
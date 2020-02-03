import bpy

from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty
                        )

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_utils                    import linkSubpartScene, unlinkSubpartScene

# These update_* functions need to be above the class... for some reason.
def update_GridScale(self, context):
    bpy.ops.object.gridscale()
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_Mirroring(self, context):
    scene = context.scene

def update_subtypeId(self, context):
    scene = context.scene

    # If the subtypeId already exists for a scene in the file, prevent it from being set
    for scn in bpy.data.scenes:
        if scn is not scene and scn.seut.subtypeId == scene.seut.subtypeId:
            scene.seut.subtypeId = scene.seut.subtypeBefore
            print("SEUT Error: Cannot set SubtypeId to a SubtypeId that already exists in the file for another scene. (018)")
            return

    if scene.seut.subtypeId != scene.seut.subtypeBefore:
        SEUT_OT_RecreateCollections.rename_Collections(scene)
        scene.name = scene.seut.subtypeId
        scene.seut.subtypeBefore = scene.seut.subtypeId

def update_linkSubpartInstances(self, context):
    scene = context.scene

    for empty in scene.objects:
        if empty is not None:
            # The check for the empty name prevents this from being run on empties that are linked to this scene.
            if empty.type == 'EMPTY' and empty.name.find('(L)') == -1 and empty.seut.linkedScene is not None and empty.seut.linkedScene.name in bpy.data.scenes:
                if scene.seut.linkSubpartInstances:
                    linkSubpartScene(self, scene, empty)
                else:
                    unlinkSubpartScene(empty)


class SEUT_Scene(PropertyGroup):
    """Holder for the various scene properties"""

    sceneType: EnumProperty(
        name='Type',
        items=(
            ('mainScene', 'Main', 'This scene is a main scene'),
            ('subpart', 'Subpart', 'This scene is a subpart of a main scene')
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
        update=update_Mirroring
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
        subtype="DIR_PATH"
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
    
    # Materials
    matPreset: EnumProperty(
        name='SEUT Material Preset',
        description="Select a nodetree preset for your material",
        items=(
            ('SMAT_Preset_Full', 'Full', '[X] Alpha\n[X] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_Full_NoEmissive', 'No Emissive', '[X] Alpha\n[_] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_Full_NoADD', 'Full, No ADD', '[X] Alpha\n[_] Emissive\n[_] ADD\n[X] NG'),
            ('SMAT_Preset_NoAlpha', 'No Alpha', '[_] Alpha\n[X] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_NoAlpha_NoEmissive', 'No Alpha, No Emissive', '[_] Alpha\n[_] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_NoADD', 'No ADD', '[_] Alpha\n[_] Emissive\n[_] ADD\n[X] NG')
            ),
        default='SMAT_Preset_Full'
    )
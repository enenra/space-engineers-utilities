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

# These update_* functions need to be above the class... for some reason.
def update_GridScale(self, context):
    bpy.ops.object.gridscale()
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_BBox(self, context):
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_SceneName(self, context):
    scene = context.scene
    if scene.seut.index == -1:
        if len(bpy.data.scenes) > 1:
            scene.seut.index = len(bpy.data.scenes) - 1
        elif len(bpy.data.scenes) == 1:
            scene.seut.index = 0
    sceneIndex = ' (' + str(scene.seut.index) + ')'
    scene.name = scene.seut.subtypeId + sceneIndex

def update_parent(self, context):
    print("parent updated")

class SEUT_Scene(PropertyGroup):
    """Holder for the various scene properties"""

    index: IntProperty(
        name='Index',
        default=-1,
        min=0
    )
    sceneType: EnumProperty(
        name='Type',
        items=(
            ('mainScene', 'Main', 'This scene is a main scene'),
            ('subpart', 'Subpart', 'This scene is a subpart of a main scene')
            ),
        default='subpart'
    )
    parent: PointerProperty(
        name='Parent',
        description="Which parent scene this subpart scene is linked to",
        type=bpy.types.Scene,
        update=update_parent
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
    bBoxToggle: EnumProperty(
        name='Bounding Box',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_BBox
    )
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

    # Export
    subtypeId: StringProperty(
        name="SubtypeId",
        description="The SubtypeId for this model",
        default="Scene",
        update=update_SceneName
    )
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
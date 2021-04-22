import bpy
import os

from bpy.types      import UIList
from bpy.types      import Panel
from bpy.types      import PropertyGroup
from bpy.props      import (EnumProperty,
                            FloatProperty,
                            FloatVectorProperty,
                            IntProperty,
                            StringProperty,
                            BoolProperty)


dlc_materials = [
    "Cooker",
    "Console",
    "Dirt",
    "SmallTiresMotion",
    "Grating",
    "GratingMetallic",
    "FoodDispenser",
    "PlasticWhite",
    "LabEquipmentScreen_01",
    "Astronaut_Damaged",
    "ArmsDamaged",
    "RightArmDamaged"
]


class SEUT_Materials(PropertyGroup):
    """Holder for the varios material properties"""
    
    overrideMatLib: BoolProperty(
        name="Override MatLib",
        description="Whether the material should replace its MatLib counterpart during export of this file (non-destructively)",
        default=False
    )
    technique: EnumProperty(
        name='Technique',
        description="The technique with which the material is rendered ingame",
        items=(
            ('MESH', 'MESH', 'The standard technique'),
            ('DECAL', 'DECAL', "Makes the material look like it's part of the model behind it"),
            ('DECAL_NOPREMULT', 'DECAL_NOPREMULT', "Higher accuracy of transparency than 'DECAL', but same visual style"),
            ('DECAL_CUTOUT', 'DECAL_CUTOUT', "Makes the material look like it cuts into the model behind it"),
            ('GLASS', 'GLASS', 'Transparent material - requires additional values to be set in TransparentMaterials.sbc'),
            ('ALPHA_MASKED', 'ALPHA_MASKED', 'Has an alphamask texture'),
            ('SHIELD', 'SHIELD', 'Animated material used on SafeZone shield - currently limited to default one.\nWarning: Causes Space Engineers to crash with some block types'),
            ('HOLO', 'HOLO', 'Transparent LCD screen texture'),
            ('FOLIAGE', 'FOLIAGE', 'Used for half-transparent textures like leaves - shadows observe transparency in texture')
            ),
        default='MESH'
    )
    facing: EnumProperty(
        name='Facing',
        description="The facing mode of the material",
        items=(
            ('None', 'None', 'No facing mode (standard)'),
            ('Vertical', 'Vertical', 'Vertical facing mode'),
            ('Full', 'Full', 'Full facing mode'),
            ('Impostor', 'Imposter', 'Imposter facing mode')
            ),
        default='None'
    )
    windScale: FloatProperty(
        name="Wind Scale:",
        description="Only relevant for trees and bushes",
        default=0,
        min=0,
        max=1
    )
    windFrequency: FloatProperty(
        name="Wind Frequency:",
        description="Only relevant for trees and bushes",
        default=0,
        min=0,
        max=100
    )

    nodeLinkedToOutputName: StringProperty(
        name="Node Linked to Output",
        default=""
    )

    # TransparentMaterial properties

    alpha_misting_enable: BoolProperty(
        name="Enable Alpha Misting",
        description="Start and end values determine the distance in meters at which a material's transparency is rendered",
        default=False
    )
    alpha_misting_start: BoolProperty(
        name="Alpha Misting Start",
        description="The distance at which the material starts to fade in",
        unit='LENGTH',
        default=0.0
    )
    alpha_misting_end: BoolProperty(
        name="Alpha Misting End",
        description="The distance at which the material finishes fading in",
        unit='LENGTH',
        default=0.0
    )
    alpha_saturation: FloatProperty(
        name="Alpha Saturation",
        description="UNKNOWN",
        default=1.0,
        min=0.0,
        max=1.0
    )
    affected_by_other_lights: BoolProperty(
        name="Affected by Other Lights",
        description="Whether or not other lights will cast light onto this texture",
        default=False
    )
    soft_particle_distance_scale: FloatProperty(
        name="Soft Particle Distance Scale",
        description="Changes the way normals are applied to a transparent surface, making it appear to have smoother transitions between hard surfaces",
        default=1.0,
        min=0.0
    )
    # Texture from CM
    # GlossTexture from NG
    color: FloatVectorProperty(
        name="Color",
        description="Overrides the color of the CM texture",
        subtype='COLOR_GAMMA',
        size=4,
        default=(0.0, 0.0, 0.0, 1.0)
    )
    color_add: FloatVectorProperty(
        name="Color Add",
        description="This color is added on top of the color of the CM texture",
        subtype='COLOR_GAMMA',
        size=4,
        default=(0.0, 0.0, 0.0, 0.1)
    )
    color_emission_multiplier: FloatProperty(
        name="Emission Multiplier",
        description="Makes the material more emissive in the Color / Color Add defined",
        default=0.0,
        min=0.0,
        max=50.0
    )
    shadow_multiplier: FloatVectorProperty(
        name="Shadow Multiplier",
        description="Controls the contribution of the color in shadowed areas",
        subtype='COLOR_GAMMA',
        size=4,
        default=(0.0, 0.0, 0.0, 0.0)
    )
    light_multiplier: FloatVectorProperty(
        name="Light Multiplier",
        description="Controls the contribution of the sun to the lighting",
        subtype='COLOR_GAMMA',
        size=4,
        default=(0.0, 0.0, 0.0, 0.0)
    )
    reflectivity: FloatProperty(
        name="Reflectivity",
        description="If Fresnel and Reflectivity are greater than 0, there can be a reflection. Increase Reflectivity if you want reflections at all angles.",
        default=0.6,
        min=0.0,
        max=1.0
    )
    fresnel: FloatProperty(
        name="Fresnel",
        description="If Fresnel and Reflectivity are greater than 0, there can be a reflection. Increase Fresnel if you want reflections at glancing angles.",
        default=1.0
    )
    reflection_shadow: FloatProperty(
        name="Reflection Shadow",
        description="Controls how intense the reflection is in the shadowed part of the block. Intensity is always 1 in the unshadowed part",
        default=0.1,
        min=0.0,
        max=1.0
    )
    gloss_texture_add: FloatProperty(
        name="Gloss Texture Add",
        description="Increases the gloss defined by the NG texture of the material. If both are zero, the reflection devolves into ambient color",
        default=0.55,
        min=0.0,
        max=1.0
    )
    gloss: FloatProperty(
        name="Gloss",
        description="How clear the reflected sun can be seen on the material",
        default=0.4,
        min=0.0,
        max=1.0
    )
    specular_color_factor: FloatProperty(
        name="Specular Color Factor",
        description="Increases the specularity of the color (the size of the sun glare)",
        default=0.0
    )
    is_flare_occluder: BoolProperty(
        name="Is Flare Occluder",
        description="Hides sprite flares of the sun, lights, thrusters, etc",
        default=False
    )


class SEUT_UL_MatLib(UIList):
    """Creates the MatLib UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.9)
        if item.enabled:
            split.label(text=item.name[:-6], icon='LINKED')
        else:
            split.label(text=item.name[:-6], icon='UNLINKED')
        split.prop(item, "enabled", text="", index=index)

        self.use_filter_sort_alpha = True

    def invoke(self, context, event):
        pass 


class SEUT_PT_Panel_Materials(Panel):
    """Creates the materials panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Materials"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene

        if bpy.context.active_object is not None and context.active_object.active_material is not None:

            material = context.active_object.active_material

            box = layout.box()
            split = box.split(factor=0.85)
            split.label(text=material.name, icon_value=layout.icon(material))
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'reference/'
            link.page = 'shader-editor-panel'

            box.prop(material.seut, 'overrideMatLib')
            box.prop(material.seut, 'technique', icon='IMGDISPLAY')
            box.prop(material.seut, 'facing')
            
            box.prop(material.seut, 'windScale', icon='SORTSIZE')
            box.prop(material.seut, 'windFrequency', icon='GROUP')

        box = layout.box()

        split = box.split(factor=0.85)
        split.label(text="Create SEUT Material", icon='MATERIAL')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials/'
        link.page = 'create-material'

        box.operator('object.create_material', icon='ADD')
        box.operator('wm.import_materials', icon='IMPORT')


class SEUT_PT_Panel_MatLib(Panel):
    """Creates the MatLib linking panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_MatLib"
    bl_label = "Material Libraries"
    bl_category = "SEUT"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        rows = 2
        row = layout.row()
        row.template_list('SEUT_UL_MatLib', "", wm.seut , 'matlibs', wm.seut , 'matlib_index', rows=rows)
        layout.operator('wm.refresh_matlibs', icon='FILE_REFRESH')
        
        layout.separator()
        split = layout.split(factor=0.85)
        split.operator('scene.export_materials', icon='EXPORT')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials/'
        link.page = 'create-matlib'


def create_internal_material(context, mat_type: str):
    """Creates a preset internal SEUT material"""

    material = bpy.data.materials.new(name="SEUT_TEMP")
    material.use_nodes = True
    material.blend_method = 'BLEND'
    nodes = material.node_tree.nodes
    
    node_bsdf = None
    node_output = None

    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node_bsdf = node
        elif node.type == 'OUTPUT_MATERIAL':
            node_output = node

    if node_bsdf is None:
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    if node_output is None:
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        material.node_tree.links.new(node_bsdf.outputs[0], node_output.inputs[0])

    if mat_type == 'MOUNTPOINT':
        node_bsdf.inputs[0].default_value = (0.03899, 1.0, 0.348069, 1)
        node_bsdf.inputs[18].default_value = 0.75
        material.name = "SMAT_Mountpoint"

    elif mat_type == 'MIRROR_X':
        node_bsdf.inputs[0].default_value = (0.715694, 0.0368895, 0.0802198, 1)
        node_bsdf.inputs[18].default_value = 0.75
        material.name = "SMAT_Mirror_X"
        
    elif mat_type == 'MIRROR_Y':
        node_bsdf.inputs[0].default_value = (0.23074, 0.533276, 0.00477695, 1)
        node_bsdf.inputs[18].default_value = 0.75
        material.name = "SMAT_Mirror_Y"
        
    elif mat_type == 'MIRROR_Z':
        node_bsdf.inputs[0].default_value = (0.0395462, 0.300544, 0.64448, 1)
        node_bsdf.inputs[18].default_value = 0.75     
        material.name = "SMAT_Mirror_Z"

    return material
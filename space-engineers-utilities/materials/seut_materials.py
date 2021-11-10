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


def update_color(self, context):
    nodes = context.active_object.active_material.node_tree.nodes

    ng = None
    for node in nodes:
        if node.name == 'SEUT_NODE_GROUP':
            ng = node
    if ng is None:
        return
    
    override = None
    alpha = None
    for i in ng.inputs:
        if i.name == 'Color Override':
            override = i
        elif i.name == 'Color Override Alpha':
            alpha = i
    if override is None or alpha is None:
        return

    override.default_value = self.color
    alpha.default_value = self.color[3]


def update_color_add(self, context):
    nodes = context.active_object.active_material.node_tree.nodes

    ng = None
    for node in nodes:
        if node.name == 'SEUT_NODE_GROUP':
            ng = node
    if ng is None:
        return
    
    overlay = None
    alpha = None
    for i in ng.inputs:
        if i.name == 'Color Overlay':
            overlay = i
        elif i.name == 'Color Overlay Alpha':
            alpha = i
    if overlay is None or alpha is None:
        return

    overlay.default_value = self.color_add
    alpha.default_value = self.color_add[3]


def update_emission_mult(self, context):
    nodes = context.active_object.active_material.node_tree.nodes

    ng = None
    for node in nodes:
        if node.name == 'SEUT_NODE_GROUP':
            ng = node
    if ng is None:
        return
    
    mult = None
    for i in ng.inputs:
        if i.name == 'Emission Strength':
            mult = i
    if mult is None:
        return

    mult.default_value = self.color_emission_multiplier


class SEUT_Materials(PropertyGroup):
    """Holder for the varios material properties"""

    version: IntProperty(
        name="SEUT Material Version",
        description="Used as a reference to patch the SEUT material properties to newer versions",
        default=1
    )
    
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
            ('DECAL', 'DECAL', "Makes the material look like it's part of the model behind it. Does not support transparency"),
            ('DECAL_NOPREMULT', 'DECAL_NOPREMULT', "Higher accuracy of transparency than 'DECAL', but same visual style"),
            ('DECAL_CUTOUT', 'DECAL_CUTOUT', "Makes the material look like it cuts into the model behind it"),
            ('GLASS', 'GLASS', 'Transparent material - requires additional values to be set in TransparentMaterials.sbc'),
            ('ALPHA_MASKED', 'ALPHA_MASKED', 'Has an alphamask texture'),
            ('ALPHA_MASKED_SINGLE_SIDED', 'ALPHA_MASKED_SINGLE_SIDED', 'Alpha mask texture, but only for a single side. Used in LOD materials'),
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
        name="Alpha Misting",
        description="Start and end values determine the distance in meters at which a material's transparency is rendered.\nNote: Only works on billboards spawned by code, not on models",
        default=False
    )
    alpha_misting_start: FloatProperty(
        name="Alpha Misting Start",
        description="The distance at which the material starts to fade in",
        unit='LENGTH',
        default=0.0
    )
    alpha_misting_end: FloatProperty(
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
        description="Whether or not other lights will cast light onto this texture.\nNote: Only works on billboards spawned by code, not on models",
        default=False
    )
    soft_particle_distance_scale: FloatProperty(
        name="Soft Particle Distance Scale",
        description="Changes the way normals are applied to a transparent surface, making it appear to have smoother transitions between hard surfaces.\nNote: Only works on billboards spawned by code, not on models",
        default=1.0,
        min=0.0
    )
    # Texture from CM
    # GlossTexture from NG
    color: FloatVectorProperty(
        name="Color Override",
        description="Overrides the color of the CM texture",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 0.0),
        update=update_color
    )
    color_add: FloatVectorProperty(
        name="Color Overlay",
        description="This color is added on top of the color of the CM texture",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 0.0),
        update=update_color_add
    )
    color_emission_multiplier: FloatProperty(
        name="Emission Multiplier",
        description="Makes the material more emissive in the Color Override / Color Overlay defined",
        default=0.0,
        min=0.0,
        max=50.0,
        update=update_emission_mult
    )
    shadow_multiplier_x: FloatProperty(
        name="Shadow Multiplier X",
        description="",
        default=0.0,
        min=0.0
    )
    shadow_multiplier_y: FloatProperty(
        name="Shadow Multiplier Y",
        description="",
        default=0.0,
        min=0.0
    )
    shadow_multiplier_z: FloatProperty(
        name="Shadow Multiplier Z",
        description="",
        default=0.0,
        min=0.0
    )
    shadow_multiplier_w: FloatProperty(
        name="Shadow Multiplier W",
        description="",
        default=0.0,
        min=0.0
    )
    #shadow_multiplier: FloatVectorProperty(
    #    name="Shadow Multiplier",
    #    description="Controls the contribution of the color in shadowed areas",
    #    subtype='COLOR_GAMMA',
    #    size=4,
    #    min=0.0,
    #    max=1.0,
    #    default=(0.0, 0.0, 0.0, 0.0)
    #)
    light_multiplier_x: FloatProperty(
        name="Light Multiplier X",
        description="",
        default=0.0,
        min=0.0
    )
    light_multiplier_y: FloatProperty(
        name="Light Multiplier Y",
        description="",
        default=0.0,
        min=0.0
    )
    light_multiplier_z: FloatProperty(
        name="Light Multiplier Z",
        description="",
        default=0.0,
        min=0.0
    )
    light_multiplier_w: FloatProperty(
        name="Light Multiplier W",
        description="",
        default=0.0,
        min=0.0
    )
    #light_multiplier: FloatVectorProperty(
    #    name="Light Multiplier",
    #    description="Controls the contribution of the sun to the lighting",
    #    subtype='COLOR_GAMMA',
    #    size=4,
    #    min=0.0,
    #    max=1.0,
    #    default=(0.0, 0.0, 0.0, 0.0)
    #)
    reflectivity: FloatProperty(
        name="Reflectivity",
        description="If Fresnel and Reflectivity are greater than 0, there can be a reflection. Increase Reflectivity if you want reflections at all angles",
        default=0.6,
        min=0.0,
        max=1.0
    )
    fresnel: FloatProperty(
        name="Fresnel",
        description="If Fresnel and Reflectivity are greater than 0, there can be a reflection. Increase Fresnel if you want reflections at glancing angles",
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
        name="Flare Occluder",
        description="Whether sprite flares of the sun, lights, thrusters, etc. can be seen through the Transparent Material",
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
            link.section = 'reference'
            link.page = '6095000/SEUT+Shader+Editor'

            box.prop(material.seut, 'overrideMatLib')
            box.prop(material.seut, 'technique', icon='IMGDISPLAY')
            box.prop(material.seut, 'facing')
            
            box.prop(material.seut, 'windScale', icon='SORTSIZE')
            box.prop(material.seut, 'windFrequency', icon='GROUP')

            if material.seut.technique == 'GLASS' or material.seut.technique == 'HOLO' or material.seut.technique == 'SHIELD':
                box = layout.box()
                box.label(text="Transparent Material Options", icon='SETTINGS')
                
                box.prop(material.seut, 'alpha_saturation', slider=True)

                box2 = box.box()
                box2.label(text="Color Adjustments", icon='COLOR')
                col = box2.column(align=True)
                col.prop(material.seut, 'color', text="")
                col.prop(material.seut, 'color_add', text="")
                col.prop(material.seut, 'color_emission_multiplier', slider=True)
                col = box2.column(align=True)
                col.prop(material.seut, 'shadow_multiplier_x', text="")
                col.prop(material.seut, 'shadow_multiplier_y', text="")
                col.prop(material.seut, 'shadow_multiplier_z', text="")
                col.prop(material.seut, 'shadow_multiplier_w', text="")
                col.prop(material.seut, 'light_multiplier_x', text="")
                col.prop(material.seut, 'light_multiplier_y', text="")
                col.prop(material.seut, 'light_multiplier_z', text="")
                col.prop(material.seut, 'light_multiplier_w', text="")
                
                box2 = box.box()
                box2.label(text="Reflection Adjustments", icon='MOD_MIRROR')
                
                col = box2.column(align=True)
                col.prop(material.seut, 'reflectivity')
                col.prop(material.seut, 'fresnel')
                col.prop(material.seut, 'reflection_shadow')

                box2.prop(material.seut, 'gloss_texture_add', slider=True)

                col = box2.column(align=True)
                col.prop(material.seut, 'gloss')
                col.prop(material.seut, 'specular_color_factor')
                col.prop(material.seut, 'is_flare_occluder', icon='LIGHT_SUN')

                box2 = box.box()
                box2.label(text="Billboards", icon='IMAGE_PLANE')
                col = box2.column(align=True)
                col.prop(material.seut, 'alpha_misting_enable', icon='ZOOM_ALL')
                if material.seut.alpha_misting_enable:
                    row = col.row(align=True)
                    row.prop(material.seut, 'alpha_misting_start', text="Start")
                    row.prop(material.seut, 'alpha_misting_end', text="End")
                box2.prop(material.seut, 'soft_particle_distance_scale')
                box2.prop(material.seut, 'affected_by_other_lights', icon='LIGHT')


        box = layout.box()

        split = box.split(factor=0.85)
        split.label(text="Create SEUT Material", icon='MATERIAL')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials'
        link.page = '6095265/Create+Material+Tutorial'

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
        link.section = 'tutorials'
        link.page = '6128098/Create+MatLib+Tutorial'


class SEUT_PT_Panel_TextureConversion(Panel):
    """Creates the Texture Conversion panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_TextureConversion"
    bl_label = "Texture Conversion"
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

        layout.prop(wm.seut, 'texconv_preset')

        box = layout.box()
        box.label(text="Input", icon='IMPORT')

        row = box.row()
        if wm.seut.texconv_input_type == 'file':
            row.prop(wm.seut, 'texconv_input_type', expand=True)
            box.prop(wm.seut, 'texconv_input_file', text="File", icon='FILE_IMAGE')
        else:
            row.prop(wm.seut, 'texconv_input_type', expand=True)
            box.prop(wm.seut, 'texconv_input_dir', text="Directory", icon='FILE_FOLDER')
        if wm.seut.texconv_preset == 'custom':
            box.prop(wm.seut, 'texconv_input_filetype', text="Type")

        box = layout.box()
        box.label(text="Output", icon='EXPORT')
        box.prop(wm.seut, 'texconv_output_dir', text="Directory", icon='FILE_FOLDER')
        if wm.seut.texconv_preset == 'custom':
            box.prop(wm.seut, 'texconv_output_filetype', text="Type")

            box = layout.box()
            box.label(text="Options", icon='SETTINGS')
            box.prop(wm.seut, 'texconv_format')
            row = box.row()
            row.prop(wm.seut, 'texconv_pmalpha')
            row.prop(wm.seut, 'texconv_sepalpha')
            box.prop(wm.seut, 'texconv_pdd')
        
        layout.operator('wm.convert_textures', icon='EXPORT')


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
        node_bsdf.inputs['Alpha'].default_value = 0.75
        material.name = "SMAT_Mountpoint"

    elif mat_type == 'MIRROR_X':
        node_bsdf.inputs[0].default_value = (0.715694, 0.0368895, 0.0802198, 1)
        node_bsdf.inputs['Alpha'].default_value = 0.75
        material.name = "SMAT_Mirror_X"
        
    elif mat_type == 'MIRROR_Y':
        node_bsdf.inputs[0].default_value = (0.23074, 0.533276, 0.00477695, 1)
        node_bsdf.inputs['Alpha'].default_value = 0.75
        material.name = "SMAT_Mirror_Y"
        
    elif mat_type == 'MIRROR_Z':
        node_bsdf.inputs[0].default_value = (0.0395462, 0.300544, 0.64448, 1)
        node_bsdf.inputs['Alpha'].default_value = 0.75     
        material.name = "SMAT_Mirror_Z"

    return material


def get_seut_texture_path(texture_type: str, material) -> str:
    """Returns the path to a material's texture of a specified type. Valid is CM, NG, ADD, AM."""

    path = None
    for node in material.node_tree.nodes:
        if node.type == 'IMAGE' and node.label == texture_type and node.name == texture_type:
            image = node.image
            path = bpy.data.images[image].filepath

    return path
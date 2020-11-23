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
            ('HOLO', 'HOLO', 'Transparent LCD screen texture')
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
        layout.operator('scene.refresh_matlibs', icon='FILE_REFRESH')
        
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
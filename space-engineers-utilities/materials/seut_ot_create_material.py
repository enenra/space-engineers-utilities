import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_errors  import seut_report


class SEUT_OT_MatCreate(Operator):
    """Create a SEUT material for the selected mesh"""
    bl_idname = "object.create_material"
    bl_label = "Create Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'


    def execute(self, context):
        
        wm = context.window_manager
        scene = context.scene
            
        new_material = create_material()
        new_material.name = "SEUT Material"

        context.active_object.active_material = new_material

        return {'FINISHED'}
    

def create_material(material=None):
    """Creates a SEUT Material"""

    if material is None:
        material = bpy.data.materials.new(name="SEUT_TEMP")
        
    material.use_nodes = True
    material.use_backface_culling = True
    material.blend_method = 'CLIP'

    nodes = material.node_tree.nodes

    node_output = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            node_output = node
        elif node.type == 'BSDF_PRINCIPLED':
            nodes.remove(node)
    if node_output == None:
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
    
    node_output.location = (250.0000, 173.1309)

    node_group_node = nodes.new(type='ShaderNodeGroup')
    node_group_node.name = 'SEUT_NODE_GROUP'
    node_group_node.location = (-25.0000, 173.1309)

    if not 'SEUT Node Group' in bpy.data.node_groups or bpy.data.node_groups['SEUT Node Group'].library != None:
        node_group = create_seut_nodegroup(node_group_node)
    else:
        node_group = bpy.data.node_groups['SEUT Node Group']

    node_group_node.node_tree = node_group
    node_group_node.inputs[6].default_value = (1.0, 1.0, 1.0, 1.0)
    material.node_tree.links.new(node_group_node.outputs[0], node_output.inputs[0])

    add_seut_image_input(material, 'CM')
    add_seut_image_input(material, 'ADD')
    add_seut_image_input(material, 'NG')
    add_seut_image_input(material, 'ALPHAMASK')

    node_paint = material.node_tree.nodes.new(type='ShaderNodeRGB')
    node_paint.label = 'Paint Color'
    node_paint.name = 'Paint Color'
    node_paint.location = (-320.0000, -660.0000)
    material.node_tree.links.new(node_paint.outputs[0], node_group_node.inputs[7])

    return material


def create_seut_nodegroup(node):
    """Creates the SEUT node group."""
    
    node_group = bpy.data.node_groups.new("SEUT Node Group", 'ShaderNodeTree')
    
    node.node_tree = node_group
    
    nodes = node_group.nodes
    links = node.node_tree.links

    node_output = nodes.new(type='NodeGroupOutput')
    node_output.label = 'Output'
    node_output.location = (0.0000, 0.0000)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.label = 'Principled BSDF'
    node_bsdf.location = (-400.0000, 0.0000)
    
    node_add_ao = nodes.new(type='ShaderNodeMixRGB')
    node_add_ao.label = 'Add AO'
    node_add_ao.location = (-687.5000, 0.0000)
    node_add_ao.blend_type = 'MULTIPLY'
    node_add_ao.use_clamp = True
    node_add_ao.inputs[0].default_value = 1.0
    links.new(node_add_ao.outputs[0], node_bsdf.inputs[0])
    
    node_gloss_rough = nodes.new(type='ShaderNodeInvert')
    node_gloss_rough.label = 'Gloss to Roughness'
    node_gloss_rough.location = (-687.5000, -231.0000)
    links.new(node_gloss_rough.outputs[0], node_bsdf.inputs[7])
    
    node_emission_color = nodes.new(type='ShaderNodeMixRGB')
    node_emission_color.label = 'Emission Color'
    node_emission_color.location = (-687.5000, -370.2500)
    links.new(node_emission_color.outputs[0], node_bsdf.inputs[17])
    
    node_normal_map = nodes.new(type='ShaderNodeNormalMap')
    node_normal_map.label = 'Normal Map'
    node_normal_map.location = (-687.5000, -600.4375)
    
    node_add_switch = nodes.new(type='ShaderNodeMath')
    node_add_switch.label = 'ADD Switch'
    node_add_switch.location = (-962.5000, 0.0000)
    node_add_switch.operation = 'CEIL'
    node_add_switch.use_clamp = True
    node_add_switch.inputs[1].default_value = 1.0
    links.new(node_add_switch.outputs[0], node_add_ao.inputs[0])
    
    node_add_paint = nodes.new(type='ShaderNodeMixRGB')
    node_add_paint.label = 'Add Paint'
    node_add_paint.location = (-962.5000, -210.7531)
    node_add_paint.blend_type = 'COLOR'
    links.new(node_add_paint.outputs[0], node_add_ao.inputs[1])
    links.new(node_add_paint.outputs[0], node_emission_color.inputs[2])
    
    node_emission_switch = nodes.new(type='ShaderNodeMath')
    node_emission_switch.label = 'Emission Switch'
    node_emission_switch.location = (-962.5000, -441.7531)
    node_emission_switch.operation = 'GREATER_THAN'
    node_emission_switch.use_clamp = True
    node_emission_switch.inputs[1].default_value = 0.1
    links.new(node_emission_switch.outputs[0], node_emission_color.inputs[0])
    
    node_separate_rgb = nodes.new(type='ShaderNodeSeparateRGB')
    node_separate_rgb.label = 'Separate RGB'
    node_separate_rgb.location = (-1237.5000, 0.0000)
    links.new(node_separate_rgb.outputs[0], node_add_ao.inputs[2])
    links.new(node_separate_rgb.outputs[1], node_emission_switch.inputs[0])
    links.new(node_separate_rgb.outputs[1], node_emission_color.inputs[1])
    
    node_input = nodes.new(type='NodeGroupInput')
    node_input.label = 'Input'
    node_input.location = (-1512.5000, 0.0000)
    node_group.inputs.new('NodeSocketColor', "CM Color")
    links.new(node_input.outputs[0], node_add_paint.inputs[1])
    node_group.inputs.new('NodeSocketColor', "CM Alpha")
    links.new(node_input.outputs[1], node_bsdf.inputs[4])
    node_group.inputs.new('NodeSocketColor', "ADD Color")
    links.new(node_input.outputs[2], node_separate_rgb.inputs[0])
    links.new(node_input.outputs[2], node_add_switch.inputs[0])
    node_group.inputs.new('NodeSocketColor', "ADD Alpha")
    links.new(node_input.outputs[3], node_add_paint.inputs[0])
    node_group.inputs.new('NodeSocketColor', "NG Color")
    links.new(node_input.outputs[4], node_normal_map.inputs[1])
    node_group.inputs.new('NodeSocketColor', "NG Alpha")
    links.new(node_input.outputs[5], node_gloss_rough.inputs[1])
    node_group.inputs.new('NodeSocketColor', "AM Color")
    links.new(node_input.outputs[6], node_bsdf.inputs[18])
    node_group.inputs.new('NodeSocketColor', "Paint Color")
    links.new(node_input.outputs[7], node_add_paint.inputs[2])

    # Backwards compatability
    
    if bpy.app.version >= (2, 90, 0):
        node_group.inputs[0].hide_value = True
        node_group.inputs[1].hide_value = True
        node_group.inputs[2].hide_value = True
        node_group.inputs[3].hide_value = True
        node_group.inputs[4].hide_value = True
        node_group.inputs[5].hide_value = True
        node_group.inputs[6].hide_value = True
        node_group.inputs[7].hide_value = True

    if bpy.app.version >= (2, 91, 0):
        node_group.inputs.new('NodeSocketFloat', "Emission Strength")
        links.new(node_input.outputs[8], node_bsdf.inputs[18])
        links.new(node_input.outputs[6], node_bsdf.inputs[19])
        links.new(node_normal_map.outputs[0], node_bsdf.inputs[20])
    else:
        links.new(node_input.outputs[6], node_bsdf.inputs[18])
        links.new(node_normal_map.outputs[0], node_bsdf.inputs[19])
        
    # Moving this down here fixed a crash on scene initialization.
    links.new(node_bsdf.outputs[0], node_output.inputs[0])

    return node_group


def add_seut_image_input(material, input_type):
    """Adds an specified image input to the given material's SEUT noe group."""
    
    node_image = material.node_tree.nodes.new(type='ShaderNodeTexImage')
    node_image.label = input_type
    node_image.name = input_type

    node_group_node = None
    for node in material.node_tree.nodes:
        if node.name == 'SEUT_NODE_GROUP':
            node_group_node = node
            break
    if node_group_node == None:
        return

    links = material.node_tree.links

    if input_type == 'CM':
        location = (-420.0000, 380.0000)
        links.new(node_image.outputs[0], node_group_node.inputs[0])
        links.new(node_image.outputs[1], node_group_node.inputs[1])
    elif input_type == 'ADD':
        location = (-420.0000, 120.0000)
        links.new(node_image.outputs[0], node_group_node.inputs[2])
        links.new(node_image.outputs[1], node_group_node.inputs[3])
    elif input_type == 'NG':
        location = (-420.0000, -140.0000)
        links.new(node_image.outputs[0], node_group_node.inputs[4])
        links.new(node_image.outputs[1], node_group_node.inputs[5])
    elif input_type == 'ALPHAMASK':
        location = (-420.0000, -400.0000)
        links.new(node_image.outputs[0], node_group_node.inputs[6])
        
    node_image.location = location

    return node_image
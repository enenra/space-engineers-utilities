import bpy
import json

ignored_attributes = [
    "__doc__",
    "__module__",
    "__slots__",
    "bl_rna",
    "rna_type",
    "copy",
    "evaluated_get",
    "get_output_node",
    "draw",
    "draw_color",
    "rna_type",
    "make_local",
    "draw_buttons",
    "draw_buttons_ext",
    "input_template",
    "interface",
    "internal_links",
    "is_registered_node_type",
    "output_template",
    "poll",
    "poll_instance",
    "socket_value_update",
    "update",
    "node",
    "original",
    "override_create",
    "update_tag",
    "user_clear",
    "user_of_id",
    "animation_data_clear",
    "animation_data_create",
    "interface_update",
    "identifier",
    "bl_icon",
    "user_remap",
    ]


def node_to_dict(node):
    dictionary = {}
    
    for attrib in dir(node):

        attrib_str = str(attrib)
        
        if attrib_str == 'inputs':
            dictionary[attrib_str] = []
            for i in node.inputs:
                dictionary[attrib_str].append(node_to_dict(i))
        
        elif attrib_str == 'links':
            dictionary[attrib_str] = []
            for l in node.links:
                dictionary[attrib_str].append(node_to_dict(l))
        
        elif attrib_str == 'outputs':
            dictionary[attrib_str] = []
            for o in node.outputs:
                dictionary[attrib_str].append(node_to_dict(o))
        
        elif attrib_str == 'nodes':
            dictionary[attrib_str] = []
            for n in node.nodes:
                dictionary[attrib_str].append(node_to_dict(n))
                
        else:
            if attrib_str not in ignored_attributes:
                value_str = str(getattr(node, attrib))
                if value_str.find("<") == -1 and value_str != "None" and value_str != "True" and value_str != "False":
                    dictionary[attrib_str] = getattr(node, attrib)
                else:
                    dictionary[attrib_str] = value_str.replace('"', "'")
            
    return dictionary
    

def print_json(dictionary):

    replace = [
        [", '", ', "'],
        ["': ", '": '],
        ["{'", '{"'],
        ["['", '["'],
        ["', ", '", '],
        [": '", ': "'],
        ["'}", '"}'],
        ["']", '"]']
        ]

    text = str(dictionary).replace(", '", ', "').replace("': ", '": ').replace("{'", '{"').replace("['", '["')
    text = text.replace("', ", '", ').replace(": '", ': "').replace("'}", '"}').replace("']", '"]')
    bpy.data.texts['output'].write(text)


node_group = bpy.data.node_groups['SEUT Node Group']

print_json(node_to_dict(node_group))
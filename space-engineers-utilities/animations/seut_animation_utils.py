import bpy
import json

from ..seut_utils       import get_seut_blend_data


def collection_property_cleanup(coll_prop):

    cleanup = [coll.name for coll in coll_prop]

    for a in bpy.data.actions:
        for f in a.fcurves:
            for k in f.keyframe_points:
                if str(k) in cleanup:
                    cleanup.remove(str(k))

    for c in cleanup:
        coll_prop.remove(next(i for i, it in enumerate(coll_prop) if it == coll_prop[c]))


def get_or_create_prop(coll_prop, act_prop):

    prop = next(
        (p for p in coll_prop if p.name == str(act_prop)), None
    )
    if prop is None:
        prop = coll_prop.add()
        prop.name = str(act_prop)
    
    return prop

def update_vars(item, holder, animation_engine):
    
    data = get_seut_blend_data()

    vars_list = json.loads(item.vars)
    if len(vars_list) > 0:
        for var in vars_list:
            del data[var]
    item.vars = "[]"

    if holder == 'triggers':
        prop = item.trigger_type
    elif holder == 'functions':
        prop = item.function_type

    if 'vars' in animation_engine[holder][prop]:
        vars = animation_engine[holder][prop]['vars']
        vars_list = []

        for k, v in vars.items():
            id = f".seut_{str(hash(item))}_{str(k)}"
            if v['type'] == "string":
                data[id] = ""
            elif v['type'] == "bool":
                data[id] = False
            elif v['type'] == "float":
                data[id] = 0.0
            elif v['type'] == "color":
                data[id] = (1.0, 1.0, 1.0)

            id_prop = data.id_properties_ui(id)
            id_prop.update(description = v['description'])

            if 'min' in v:
                id_prop.update(min = v['min'])
            if 'max' in v:
                id_prop.update(max = v['max'])
            if 'default' in v:
                id_prop.update(default = v['default'])
            if 'subtype' in v:
                id_prop.update(subtype = v['subtype'])

            vars_list.append(id)

        item.vars = json.dumps(vars_list)
import bpy


def collection_property_cleanup(coll_prop, ext_prop):

    cleanup = [coll.name for coll in coll_prop]

    for ext in ext_prop:
        if str(ext) in cleanup:
            cleanup.remove(str(ext))

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
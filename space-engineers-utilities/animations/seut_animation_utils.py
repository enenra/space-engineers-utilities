import bpy


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
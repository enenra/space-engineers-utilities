
import bpy
import threading

from collections            import OrderedDict

# STOLLIE: This clones the specification from Blenders source code for its FBX Exporter so we can add some custom properties.
def _clone_fbx_module():
    import sys
    from importlib.util import find_spec

    SPECIFICATION = 'io_scene_fbx.export_fbx_bin'
    saved_module = sys.modules.pop(SPECIFICATION, None)
    try:
        spec = find_spec(SPECIFICATION)
        return spec.loader.load_module()
    finally:
        if saved_module:
            sys.modules[SPECIFICATION] = saved_module
        else:
            if sys.modules.get(SPECIFICATION, None):
                del sys.modules[SPECIFICATION]

# STOLLIE: Assign the clone of the loaded specification to global variable.
_fbx = _clone_fbx_module() 

# STOLLIE: Assign a copy of the function from the loaded specification to a global variable.
_original_fbx_template_def_model = _fbx.fbx_template_def_model 

# HARAG: Extend the "fbx_template_def_model" function with further SE properties by using the overrides.
# Reference material: https://github.com/rjstone/SEMT/issues/1
# Reference material: https://forums.keenswh.com/threads/space-engineers-mod-toolkit-for-blender.7090652/
def fbx_template_def_model(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        # HARAG: Name, Value, Type, Animatable
        # HARAG: SE properties
        (b"file", ("", "p_string", False)),
        (b"highlight", ("", "p_string", False)),

        # HARAG: Havok properties last to avoid including unrelated properties in the conversion to .hkt
        (b"hkTypeRigidBody", ("", "p_string", False)),
        (b"mass", (-1.0, "p_double", False)),
        (b"friction", (-1.0, "p_double", False)),
        (b"restitution", (-1.0, "p_double", False)),
        (b"hkTypeShape", ("", "p_string", False)),
        (b"shapeType", ("", "p_string", False)),
    ))

    if override_defaults is not None:
        props.update(override_defaults)

    return _original_fbx_template_def_model(scene, settings, props, nbr_users)

# STOLLIE: Assign extended properties to the copied function from the loaded specification by calling the function above.
_fbx.fbx_template_def_model = fbx_template_def_model

HAVOK_SHAPE_NAMES = {
    'CONVEX_HULL': 'Hull',
    'BOX': 'Box',
    'SPHERE': 'Sphere',
    'CYLINDER': 'Cylinder',
    'CAPSULE': 'Capsule',
    'MESH': 'Mesh',
    'CONE': 'Hull', # not supported by Havok
}

# HARAG: No easy way to extend, so copied from export_fbx_bin.py and modified.
def fbx_data_object_elements(root, ob_obj, scene_data):
    
    # Write the Object (Model) data blocks.
    # Note this "Model" can also be bone or dupli!
    
    obj_type = b"Null"  # default, sort of empty...
    if ob_obj.is_bone:
        obj_type = b"LimbNode"
    elif (ob_obj.type == 'ARMATURE'):
        obj_type = b"Root"
    elif (ob_obj.type in _fbx.BLENDER_OBJECT_TYPES_MESHLIKE):
        obj_type = b"Mesh"
    elif (ob_obj.type == 'LAMP'):
        obj_type = b"Light"
    elif (ob_obj.type == 'CAMERA'):
        obj_type = b"Camera"
    elif (ob_obj.type == 'EMPTY'):
        obj_type = b"Empty"

    model = _fbx.elem_data_single_int64(root, b"Model", ob_obj.fbx_uuid)
    model.add_string(_fbx.fbx_name_class(ob_obj.name.encode(), b"Model"))
    model.add_string(obj_type)

    # STOLLIE: The modifications in this method are assigned to our cloned function instead of Blenders orginial.
    # https://developer.blender.org/diffusion/BA/browse/master/io_scene_fbx/export_fbx_bin.py$1664 
    _fbx.elem_data_single_int32(model, b"Version", _fbx.FBX_MODELS_VERSION) 

    # BLENDER: Object transform info.
    loc, rot, scale, matrix, matrix_rot = ob_obj.fbx_object_tx(scene_data)
    rot = tuple(_fbx.convert_rad_to_deg_iter(rot))

    tmpl = _fbx.elem_props_template_init(scene_data.templates, b"Model")

    # BLENDER: For now add only loc/rot/scale...
    # STOLLIE: These have more info in both 2.79b and 2.81 source, not sure if extra bits needed?
    # https://developer.blender.org/diffusion/BA/browse/master/io_scene_fbx/export_fbx_bin.py$1673
    props = _fbx.elem_properties(model)
    _fbx.elem_props_template_set(tmpl, props, "p_lcl_translation", b"Lcl Translation", loc)
    _fbx.elem_props_template_set(tmpl, props, "p_lcl_rotation", b"Lcl Rotation", rot)
    _fbx.elem_props_template_set(tmpl, props, "p_lcl_scaling", b"Lcl Scaling", scale)
    _fbx.elem_props_template_set(tmpl, props, "p_visibility", b"Visibility", float(not ob_obj.hide))

    # BLENDER: Absolutely no idea what this is, but seems mandatory for validity of the file, and defaults to
    # BLENDER: invalid -1 value...
    _fbx.elem_props_template_set(tmpl, props, "p_integer", b"DefaultAttributeIndex", 0)

    _fbx.elem_props_template_set(tmpl, props, "p_enum", b"InheritType", 1)  # BLENDER: RSrs

    # BLENDER: Custom properties.
    if scene_data.settings.use_custom_props:
        # BLENDER: Here we want customprops from the 'pose' bone, not the 'edit' bone...
        # _fbx.bdata = ob_obj.bdata_pose_bone if ob_obj.is_bone else ob_obj.bdata #STOLLIE: 2.8 addition.
        _fbx.fbx_data_element_custom_properties(props, ob_obj.bdata)

    # BLENDER: Those settings would obviously need to be edited in a complete version of the exporter, may depends on
    # BLENDER: object type, etc.
    _fbx.elem_data_single_int32(model, b"MultiLayer", 0)
    _fbx.elem_data_single_int32(model, b"MultiTake", 0)
    _fbx.elem_data_single_bool(model, b"Shading", True)
    _fbx.elem_data_single_string(model, b"Culling", b"CullingOff")

    if obj_type == b"Camera":
        # BLENDER: Why, oh why are FBX cameras such a mess???
        # BLENDER: And WHY add camera data HERE??? Not even sure this is needed...
        render = scene_data.scene.render
        width = render.resolution_x * 1.0
        height = render.resolution_y * 1.0
        _fbx.elem_props_template_set(tmpl, props, "p_enum", b"ResolutionMode", 0)  # BLENDER: Don't know what it means
        _fbx.elem_props_template_set(tmpl, props, "p_double", b"AspectW", width)
        _fbx.elem_props_template_set(tmpl, props, "p_double", b"AspectH", height)
        _fbx.elem_props_template_set(tmpl, props, "p_bool", b"ViewFrustum", True)
        _fbx.elem_props_template_set(tmpl, props, "p_enum", b"BackgroundMode", 0)  # BLENDER: Don't know what it means
        _fbx.elem_props_template_set(tmpl, props, "p_bool", b"ForegroundTransparent", True)
        
    # ----------------------- CUSTOM PART BEGINS HERE ----------------------- #

    # This is the link from empties to files and/or highlights to meshes.
    
    """
    if obj_type == b"Empty" and bpy.data.objects[ob_obj.name]['file'] is not None:
        customProp = bpy.data.objects[ob_obj.name]['file']

        if customProp is not None:
            _fbx.elem_props_template_set(tmpl, props, "p_string", b"file", customProp)
    
    """
    if obj_type == b"Empty":
        se_custom_property_file = ob_obj.bdata.get('file', None)
        se_custom_property_highlight = ob_obj.bdata.get('highlight', None)

        if se_custom_property_file is not None:
            _fbx.elem_props_template_set(tmpl, props, "p_string", b"file", se_custom_property_file)
        
        if se_custom_property_highlight is not None:
            # HARAG: TODO SE supports mutliple highlight shapes via <objectSPECIFICATION1>;<objectSPECIFICATION2>;...
            _fbx.elem_props_template_set(tmpl, props, "p_string", b"highlight", se_custom_property_highlight)

    if obj_type == b"Mesh" and ob_obj.bdata.rigid_body:
        rbo = ob_obj.bdata.rigid_body
        shapeType = HAVOK_SHAPE_NAMES[rbo.collision_shape] or rbo.collision_shape
        _fbx.elem_props_template_set(tmpl, props, "p_string", b"hkTypeRigidBody", "hkRigidBody")
        _fbx.elem_props_template_set(tmpl, props, "p_double", b"mass", rbo.mass)
        _fbx.elem_props_template_set(tmpl, props, "p_double", b"friction", rbo.friction)
        _fbx.elem_props_template_set(tmpl, props, "p_double", b"restitution", rbo.restitution)
        _fbx.elem_props_template_set(tmpl, props, "p_string", b"hkTypeShape", "hkShape")
        _fbx.elem_props_template_set(tmpl, props, "p_string", b"shapeType", shapeType)

    # ------------------------ CUSTOM PART ENDS HERE ------------------------ #

    _fbx.elem_props_template_finalize(tmpl, props)

# STOLLIE: Assign the blender defined and custom properties above to the copied function from the loaded specification by calling the above function.
_fbx.fbx_data_object_elements = fbx_data_object_elements

# HARAG: Export these two functions as our own so that clients of this module don't have to depend on 
# HARAG: the cloned fbx_experimental.export_fbx_bin module
save_single = _fbx.save_single
save = _fbx.save
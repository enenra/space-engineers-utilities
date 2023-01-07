import bpy
import os

from ..utils.seut_xml_utils import *
from ..seut_errors          import seut_report
from ..seut_utils           import get_abs_path, get_enum_items


def export_animation_xml(self, context: bpy.types.Context):
    """Exports all animation sets to xml"""
    wm = context.window_manager
    scene = context.scene
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data", "Animations")

    # Check for animations to override by file name

    # Error if two animation sets are named the same

    # Error if bezier is used

    if len(wm.seut.animations) == 0:
        return {'CANCELLED'}

    animations = ET.Element('Animations')
    for animation_set in wm.seut.animations:
        animation = add_subelement(animations, 'Animation')
        add_attrib(animation, 'id', animation_set.name)

        # Triggers
        triggers = add_subelement(animation, 'Triggers')
        for tg in animation_set.triggers:

            trigger_enum = tg.bl_rna.properties['trigger_type']
            id = next(
                (
                    p.identifier
                    for p in trigger_enum.enum_items
                    if p.name == tg.trigger_type
                ),
                None,
            )
            if id in ['Working', 'Producing']:
                trigger = add_subelement(triggers, 'State')
            else:
                trigger = add_subelement(triggers, 'Event')

            add_attrib(trigger, 'type', id)

            if id in ['PressedOn', 'PressedOff', 'Pressed']:
                add_attrib(trigger, 'empty', tg.Pressed_empty)

            elif id in ['Arrive', 'Leave']:
                add_attrib(trigger, 'distance', tg.distance)

            elif id == 'Working':
                add_attrib(trigger, 'bool', tg.Working_bool.lower())
                add_attrib(trigger, 'loop', tg.Working_loop)

            elif id == 'Producing':
                add_attrib(trigger, 'bool', tg.Producing_bool.lower())
                add_attrib(trigger, 'loop', tg.Producing_loop)

        # Subparts
        subparts = add_subelement(animation, 'Subparts')
        for sp in animation_set.subparts:
            subpart = add_subelement(subparts, 'Subpart')
            add_attrib(subpart, 'empty', sp.obj.name)

            # Keyframes
            keyframes = add_subelement(subparts, 'Keyframes')

            if sp.action is None:
                continue

            # Create dict that lists all keyframes on the same time marker
            k_dict = {}
            for f in sp.action.fcurves:
                for k in f.keyframe_points:
                    if k.co_ui[0] not in k_dict:
                        k_dict[k.co_ui[0]] = {}
                    k_dict[k.co_ui[0]][k] = f

            for time, k_f_dict in k_dict.items():
                keyframe = add_subelement(keyframes, 'Keyframe')
                add_attrib(keyframe, 'time', time)

                for kf, f in k_f_dict.items():

                    # Write Animated Properties
                    anim = add_subelement(keyframe, 'Anim')

                    coords = [0.0, 0.0, 0.0]
                    coords[f.array_index] = kf.co_ui[1]
                    add_attrib(anim, f.data_path, f"[{coords[0]},{coords[1]},{coords[2]}]")

                    add_attrib(anim, 'lerp', kf.interpolation)

                    if kf.easing == 'AUTO' and kf.interpolation in ['SINE', 'QUAD', 'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC']:
                        add_attrib(anim, 'easing', 'IN')
                    if kf.easing == 'AUTO' and kf.interpolation in ['BACK', 'BOUNCE', 'ELASTIC']:
                        add_attrib(anim, 'easing', 'OUT')
                    elif kf.easing != 'AUTO':
                        add_attrib(anim, 'easing', kf.easing)

                    # Write Functions
                    seut_kf = next(
                        (k for k in sp.action.seut.keyframes if k.name == str(kf)), None
                    )
                    if seut_kf is not None:
                        for func in seut_kf.functions:

                            # Get enum with IDs of function types
                            func_enum = func.bl_rna.properties['function_type']
                            id = next(
                                (
                                    p.identifier
                                    for p in func_enum.enum_items
                                    if p.name == func.function_type
                                ),
                                None,
                            )
                            function = add_subelement(keyframe, 'Function')
                            add_attrib(function, 'type', id)

                            if id == 'setVisible':
                                add_attrib(function, 'bool', func.setVisible_bool.lower())
                                add_attrib(function, 'empty', func.setVisible_empty)

                            elif id == 'setEmissiveColor':
                                add_attrib(function, 'material', func.setEmissiveColor_material)
                                add_attrib(function, 'rgb', f"[{func.setEmissiveColor_rgb[0]},{func.setEmissiveColor_rgb[1]},{func.setEmissiveColor_rgb[2]}]")
                                add_attrib(function, 'brightness', func.setEmissiveColor_brightness)

                            elif id == 'playParticle':
                                add_attrib(function, 'empty', func.playParticle_empty)
                                add_attrib(function, 'subtypeid', func.playParticle_subtypeid)

                            elif id == 'stopParticle':
                                add_attrib(function, 'empty', func.stopParticle_empty)
                                add_attrib(function, 'subtypeid', func.stopParticle_subtypeid)

                            elif id == 'playSound':
                                add_attrib(function, 'subtypeid', func.playSound_subtypeid)

                            elif id == 'stopSound':
                                add_attrib(function, 'subtypeid', func.stopSound_subtypeid)

                            elif id == 'setLightColor':
                                add_attrib(function, 'empty', func.setLightColor_empty)
                                add_attrib(function, 'rgb', f"[{func.setLightColor_rgb[0]},{func.setLightColor_rgb[1]},{func.setLightColor_rgb[2]}]")

                            elif id in ['lightOn', 'lightOff', 'toggleLight']:
                                add_attrib(function, 'subtypeid', func.light_empty)


    temp_string = ET.tostring(animations, 'utf-8')
    xml_string = xml.dom.minidom.parseString(temp_string)
    xml_formatted = xml_string.toprettyxml()

    print(xml_formatted)
    return {'FINISHED'}
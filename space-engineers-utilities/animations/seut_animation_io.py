import bpy
import os
import math

from math import pi

from .seut_animations       import items_trigger_types, items_function_types

from ..utils.seut_xml_utils import *
from ..seut_errors          import seut_report
from ..seut_utils           import get_abs_path, get_enum_items, get_seut_blend_data


def export_animation_xml(self, context: bpy.types.Context):
    """Exports all animation sets to xml"""

    data = get_seut_blend_data()
    scene = context.scene
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data", "Animation")

    # Warning if bezier is used (unsupported)
    bezier = False
    for anim in data.seut.animations:
        for sp in anim.subparts:
            if sp.action is not None:
                for f in sp.action.fcurves:
                    for kf in f.keyframe_points:
                        if kf.interpolation == 'BEZIER':
                            bezier = True
                            break
    if bezier:
        seut_report(self, context, 'WARNING', True, 'W015')

    animations = ET.Element('Animations')
    add_attrib(animations, 'ver', 1)
    for animation_set in data.seut.animations:

        # Don't export animation sets where no subpart has an action
        if all(sp.action is None for sp in animation_set.subparts):
            continue

        animation = ET.SubElement(animations, 'Animation')
        add_attrib(animation, 'id', animation_set.name)
        add_attrib(animation, 'subtypeId', scene.seut.subtypeId)

        # Triggers
        triggers = add_subelement(animation, 'Triggers')
        for tg in animation_set.triggers:

            if tg.trigger_type in ['Working', 'Producing']:
                trigger = ET.SubElement(triggers, 'State')
            else:
                trigger = ET.SubElement(triggers, 'Event')

            add_attrib(trigger, 'type', tg.trigger_type)

            if tg.trigger_type in ['PressedOn', 'PressedOff', 'Pressed']:
                add_attrib(trigger, 'empty', tg.Pressed_empty.name)

            elif tg.trigger_type in ['Arrive', 'Leave']:
                add_attrib(trigger, 'distance', round(tg.distance,2))

            elif tg.trigger_type == 'Working':
                add_attrib(trigger, 'bool', str(tg.Working_bool).lower())
                add_attrib(trigger, 'loop', str(tg.Working_loop).lower())

            elif tg.trigger_type == 'Producing':
                add_attrib(trigger, 'bool', str(tg.Producing_bool).lower())
                add_attrib(trigger, 'loop', str(tg.Producing_loop).lower())

        # Subparts
        subparts = add_subelement(animation, 'Subparts')
        for sp in animation_set.subparts:
            subpart = ET.SubElement(subparts, 'Subpart')
            add_attrib(subpart, 'empty', sp.obj.name)

            # Keyframes
            keyframes = add_subelement(subpart, 'Keyframes')

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
                keyframe = ET.SubElement(keyframes, 'Keyframe')
                add_attrib(keyframe, 'frame', int(round(time,0)))

                anim_dict = {}
                for kf, f in k_f_dict.items():

                    if f.data_path not in anim_dict and f.data_path != 'scale':
                        anim_dict[f.data_path] = [0.0, 0.0, 0.0]
                    elif f.data_path not in anim_dict:
                        anim_dict[f.data_path] = [1.0, 1.0, 1.0]

                    if (f.data_path == 'scale' and kf.co_ui[1] != 1.0) or (f.data_path != 'scale' and kf.co_ui[1] not in [0.0, -0.0]):

                        # This triggers in case the rotation is in quaternions and transforms it to euler, then overwrites x, y and z
                        if f.data_path == 'rotation_quaternion' and f.array_index not in anim_dict[f.data_path]:
                            euler_rot = quaternion_to_euler(anim_dict[f.data_path][0], anim_dict[f.data_path][1], anim_dict[f.data_path][2], kf.co_ui[1])
                            anim_dict[f.data_path][0] = euler_rot[0]
                            anim_dict[f.data_path][1] = euler_rot[1]
                            anim_dict[f.data_path][2] = euler_rot[2]

                        else:
                            anim_dict[f.data_path][f.array_index] = kf.co_ui[1]

                for key, coords in anim_dict.items():
                    # Write Animated Properties
                    anim = ET.SubElement(keyframe, 'Anim')

                    motion_type = key

                    if motion_type in ['rotation_euler','rotation_quaternion']:
                        motion_type = 'rotation'
                        if coords[0] != 0: coords[0] = coords[0] * 180 / pi
                        if coords[1] != 0: coords[1] = coords[1] * 180 / pi
                        if coords[2] != 0: coords[2] = coords[2] * 180 / pi
                    
                    precision = 2
                    x = round(coords[0], precision)
                    y = round(coords[1], precision)
                    z = round(coords[2], precision)
                    
                    if x == -0.0:
                        x = abs(x)
                    if y == -0.0:
                        y = abs(y)
                    if z == -0.0:
                        z = abs(z)

                    add_attrib(anim, motion_type, f"[{x},{y},{z}]")

                    if kf.interpolation == 'BEZIER':
                        kf.interpolation = 'LINEAR'

                    add_attrib(anim, 'lerp', kf.interpolation)

                    if kf.easing == 'AUTO' and kf.interpolation in ['SINE', 'QUAD', 'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC']:
                        add_attrib(anim, 'easing', 'EASE_IN')
                    if kf.easing == 'AUTO' and kf.interpolation in ['BACK', 'BOUNCE', 'ELASTIC']:
                        add_attrib(anim, 'easing', 'EASE_OUT')
                    elif kf.easing != 'AUTO':
                        add_attrib(anim, 'easing', kf.easing)

                # Write Functions
                for kf in k_f_dict.keys():
                    seut_kf = next(
                        (k for k in sp.action.seut.keyframes if k.name == str(kf)), None
                    )
                    if seut_kf is not None:
                        for func in seut_kf.functions:

                            function = ET.SubElement(keyframe, 'Function')
                            add_attrib(function, 'type', func.function_type)

                            if func.function_type == 'setVisible':
                                add_attrib(function, 'bool', str(func.setVisible_bool).lower())
                                add_attrib(function, 'empty', func.setVisible_empty.name)

                            elif func.function_type == 'setEmissiveColor':
                                add_attrib(function, 'material', func.setEmissiveColor_material.name)
                                add_attrib(function, 'rgb', f"[{round(func.setEmissiveColor_rgb[0],1)},{round(func.setEmissiveColor_rgb[1],1)},{round(func.setEmissiveColor_rgb[2],1)}]")
                                add_attrib(function, 'brightness', round(func.setEmissiveColor_brightness,2))

                            elif func.function_type == 'playParticle':
                                add_attrib(function, 'empty', func.playParticle_empty.name)
                                add_attrib(function, 'subtypeid', func.playParticle_subtypeid)

                            elif func.function_type == 'stopParticle':
                                add_attrib(function, 'empty', func.stopParticle_empty.name)
                                add_attrib(function, 'subtypeid', func.stopParticle_subtypeid)

                            elif func.function_type == 'playSound':
                                add_attrib(function, 'subtypeid', func.playSound_subtypeid)

                            elif func.function_type == 'stopSound':
                                add_attrib(function, 'subtypeid', func.stopSound_subtypeid)

                            elif func.function_type == 'setLightColor':
                                add_attrib(function, 'empty', func.setLightColor_empty.name)
                                add_attrib(function, 'rgb', f"[{round(func.setLightColor_rgb[0],1)},{round(func.setLightColor_rgb[1],1)},{round(func.setLightColor_rgb[2],1)}]")

                            elif func.function_type in ['lightOn', 'lightOff', 'toggleLight']:
                                add_attrib(function, 'subtypeid', func.light_empty.name)


    temp_string = ET.tostring(animations, 'utf-8')
    xml_string = xml.dom.minidom.parseString(temp_string)
    xml_formatted = xml_string.toprettyxml()

    filename = scene.seut.subtypeId
    target_file = os.path.join(path_data, f"{filename}.xml")
    if not os.path.exists(os.path.join(path_data)):
        os.makedirs(os.path.join(path_data))

    exported_xml = open(target_file, "w")
    exported_xml.write(xml_formatted)

    update_main_info(filename, path_data)

    seut_report(self, context, 'INFO', False, 'I004', target_file)

    return {'FINISHED'}


def quaternion_to_euler(x, y, z, w):

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z


def update_main_info(filename, path):

    info_path = os.path.join(path, "main.info")

    if not os.path.exists(info_path):
        main_file = open(info_path, 'w')
        lines = []
    else:
        with open(info_path, 'r') as main_file:
            lines = main_file.readlines()
            main_file.close()

    for l in lines:
        if l is None or l == '':
            continue

        split = l.split(" ")
        if split[0] == 'XMLAnimation' and split[1] == filename:
            return

    if len(lines) > 0:
        lines[len(lines)-1] += '\n'
    lines.append(f"XMLAnimation {filename}")

    with open(info_path, 'w') as main_file:
        main_file.write("".join(lines))
import bpy
import os
import time

from bpy.types  import Operator

from ..utils.seut_tool_utils        import *
from ..seut_errors                  import seut_report, get_abs_path
from ..seut_utils                   import create_relative_path, get_preferences


presets = {
    "icon": [None, None, '-ft', 'DDS', '-f', 'BC7_UNORM_SRGB', '-pmalpha', '-sRGB', '-y', '-o', None],
    "cm": [None, None, '-ft', 'DDS', '-f', 'BC7_UNORM_SRGB', '-sepalpha', '-sRGB', '-y', '-o', None],
    "add": [None, None, '-ft', 'DDS', '-f', 'BC7_UNORM_SRGB', '-if', 'POINT_DITHER_DIFFUSION', '-sepalpha', '-sRGB', '-y', '-o', None],
    "ng": [None, None, '-ft', 'DDS', '-f', 'BC7_UNORM', '-sepalpha', '-y', '-o', None],
    "alphamask": [None, None, '-ft', 'DDS', '-f', 'BC7_UNORM', '-if', 'POINT_DITHER_DIFFUSION', '-y', '-o', None],
    "tif": [None, None, '-ft', 'TIF', '-y', '-o', None],
    "custom": [None, None, '-y', '-o', None]
}


class SEUT_OT_ConvertTextures(Operator):
    """Converts textures to a different format"""
    bl_idname = "wm.convert_textures"
    bl_label = "Convert Textures"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        if wm.seut.texconv_input_type == 'file':
            return wm.seut.texconv_input_file != ""
        else:
            return wm.seut.texconv_input_dir != ""


    def execute(self, context):
        
        wm = context.window_manager

        if wm.seut.texconv_output_dir == "":
            if wm.seut.texconv_input_type == 'file':
                wm.seut.texconv_output_dir = os.path.dirname(wm.seut.texconv_input_file)
            else:
                wm.seut.texconv_output_dir = wm.seut.texconv_input_dir
        
        settings = []

        if wm.seut.texconv_preset == 'custom':
            settings.append('-ft')
            settings.append(wm.seut.texconv_output_filetype.lower())

            if wm.seut.texconv_format != 'NONE':
                settings.append('-f')
                settings.append(wm.seut.texconv_format)
                if wm.seut.texconv_format == 'BC7_UNORM_SRGB':
                    settings.append('-sRGB')

            if wm.seut.texconv_pmalpha:
                settings.append('-pmalpha')

            if wm.seut.texconv_sepalpha:
                settings.append('-sepalpha')

            if wm.seut.texconv_pdd:
                settings.append('-if')
                settings.append('POINT_DITHER_DIFFUSION')
        
        output_path = get_abs_path(wm.seut.texconv_output_dir)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if wm.seut.texconv_input_type == 'file':
            result = convert_texture(get_abs_path(wm.seut.texconv_input_file), output_path, wm.seut.texconv_preset, settings)
            if result[0] == 0:
                seut_report(self, context, 'INFO', True, 'I009', f"1/1", "")
            else:
                seut_report(self, context, 'ERROR', True, 'E046', "texture conversion", result[1])
                return {'CANCELLED'}
        else:
            results = mass_convert_textures(self, context, [get_abs_path(wm.seut.texconv_input_dir)], output_path, wm.seut.texconv_preset, settings)
            converted = 0
            for r in results:
                if r[0] == 0:
                    converted += 1

            if converted == 0:
                return {'CANCELLED'}
            else:
                seut_report(self, context, 'INFO', True, 'I009', converted, "")
        
        return {'FINISHED'}
        

class SEUT_OT_MassConvertTextures(Operator):
    """Mass converts DDS textures to TIF.\nWARNING: This can lock up Blender for up to 30min for a full conversion"""
    bl_idname = "wm.mass_convert_textures"
    bl_label = "Update Textures from Game Files"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        preferences = get_preferences()
        return os.path.exists(preferences.game_path) and os.path.exists(preferences.asset_path)


    def execute(self, context):

        wm = context.window_manager
        preferences = get_preferences()
        target_dir = preferences.asset_path

        dirs_to_convert = [
            "Models\\Cubes",
            "Models\\Cubes\\armor",
            "Models\\Cubes\\lods",
            "Models\\Physical_item",
            "Models\\Debris",
            "Models\\Characters\\Astronaut",
            "Models\\Environment\\Bushes",
            "Models\\Environment\\Grass",
            "Models\\Environment\\Trees",
            "Models\\Environment\\Props",
            "Models\\Environment\\SafeZone",
            "Models\\Weapons",
            "Models\\Debug",
            "Particles"
        ]

        skip_list = ['_de.', '_ns.']

        for d in range(0, len(dirs_to_convert)):
            dirs_to_convert[d] = os.path.join(preferences.game_path, 'Content', 'Textures', dirs_to_convert[d])

        result = mass_convert_textures(self, context, dirs_to_convert, target_dir, 'tif', skip_list=skip_list, log_to_file=True, can_report=True)

        return result


def mass_convert_textures(self, context, dirs: list, target_dir: str, preset: str, settings: list = [], skip_list: list = [], log_to_file=False, can_report=False):

    wm = context.window_manager

    idx_ft = presets[preset].index('-ft')
    output_type = presets[preset][idx_ft + 1]

    files_to_convert = []

    for tex_dir in dirs:

        for file in os.listdir(tex_dir):
            if os.path.isfile(os.path.join(tex_dir, file)):
                source = os.path.join(tex_dir, file)

                if not os.path.splitext(source)[1].upper()[1:] in ['DDS', 'TIF', 'PNG']:
                    continue
                
                if skip_list != []:
                    skip = False
                    for i in skip_list:
                        if i in os.path.basename(source):
                            skip = True
                            break
                    if skip:
                        continue
                
                if target_dir.find('Textures') != -1:
                    target = os.path.join(target_dir, os.path.splitext(file)[0] + '.' + output_type)
                else:
                    target = os.path.join(target_dir, create_relative_path(tex_dir, 'Textures'), os.path.splitext(file)[0] + '.' + output_type)

                if not os.path.exists(target) or os.path.getmtime(source) > os.path.getmtime(target):
                    files_to_convert.append(os.path.join(tex_dir, file))

    commands = []
    for tex in files_to_convert:
        if target_dir.find('Textures') != -1:
            path_out = target_dir
        else:
            path_out =  create_relative_path(os.path.dirname(tex), 'Textures')
            path_out = os.path.join(target_dir, path_out)

        os.makedirs(path_out, exist_ok=True)
        target_file = os.path.join(path_out, os.path.splitext(os.path.basename(tex))[0])
    
        commands.append(get_conversion_args(preset, tex, path_out, settings))
        
    total = len(files_to_convert)
    if total > 0:
        if log_to_file:
            logfile = os.path.join(target_dir, 'conversion.log')
        else:
            logfile = None

        timer = time.time()
        results = []
        results = call_tool_threaded(commands, 10, logfile)
        duration = time.time() - timer

        converted = 0
        for r in results:
            idx_o = presets[preset].index('-o')
            target_file = os.path.join(r[2][idx_o + 1], os.path.splitext(os.path.basename(r[2][1]))[0] + '.' + output_type)
            if r[0] == 0:
                converted += 1
                print(f"OK    - {target_file}")
            else:
                print(f"ERROR - {target_file}")
                print(r[1])

        if converted == 0:
            return {'CANCELLED'}

        elif duration > 60:
            m, s = divmod(duration, 60)
            seut_report(self, context, 'INFO', can_report, 'I009', f"{converted}/{total}", f" in {m}m {s}s")
        else:
            seut_report(self, context, 'INFO', can_report, 'I009', f"{converted}/{total}", f" in {round(duration, 1)}s")

    else:
        seut_report(self, context, 'INFO', can_report, 'I003')

    return {'FINISHED'}


def convert_texture(path_in: str, path_out: str, preset: str, settings=[]):

    path_in = get_abs_path(path_in)
    path_out = get_abs_path(path_out)

    if preset in presets:
        args = get_conversion_args(preset, path_in, path_out, settings)
        
        result = call_tool(args)
        if result[1] is not None:
            result[1] = result[1].decode("utf-8", "ignore")
        else:
            result[1] = "None"
        return result


def get_conversion_args(preset: str, path_in: str, path_out: str, settings=[]) -> list:

    args = presets[preset]
    args[0] = os.path.join(get_tool_dir(), 'texconv.exe')
    args[1] = path_in
    args[len(args) - 1] = path_out

    if preset == 'custom' and settings != []:
        pos = 2
        for i in settings:
            args.insert(pos, i)
            pos += 1

    return list(args)
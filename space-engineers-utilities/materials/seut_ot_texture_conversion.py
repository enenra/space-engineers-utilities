import bpy
import os

from bpy.types  import Operator

from ..utils.seut_tool_utils    import *
from ..seut_errors              import seut_report, get_abs_path


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

        if wm.seut.texconv_input_type == 'file':
            path_in = wm.seut.texconv_input_file
        else:
            path_in = wm.seut.texconv_input_dir + '*.' + wm.seut.texconv_input_filetype.lower()

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

            if wm.seut.texconv_pmalpha:
                settings.append('-pmalpha')

            if wm.seut.texconv_sepalpha:
                settings.append('-sepalpha')

            if wm.seut.texconv_pdd:
                settings.append('-if')
                settings.append('POINT_DITHER_DIFFUSION')
                
        convert_texture(path_in, wm.seut.texconv_output_dir, wm.seut.texconv_preset, settings)

        for path, subdirs, files in os.walk(wm.seut.texconv_output_dir):
            for f in files:
                if f.endswith(wm.seut.texconv_output_filetype.upper()):
                    filepath = os.path.join(path, f)
                    os.rename(filepath, os.path.splitext(filepath)[0] + '.' + wm.seut.texconv_output_filetype.lower())

        return {'FINISHED'}


def convert_texture(path_in: str, path_out: str, preset: str, settings: list):

    texconv = os.path.join(get_tool_dir(), 'texconv.exe')

    path_in = get_abs_path(path_in)
    path_out = get_abs_path(path_out)

    presets = {
        "icon": [texconv, 'texconv', '-ft', 'DDS', '-f', 'BC7_UNORM_SRGB', '-pmalpha', '-sRGB', '-y', '-o', path_out, path_in],
        "cm": [texconv, 'texconv', '-ft', 'DDS', '-f', 'BC7_UNORM_SRGB', '-sepalpha', '-sRGB', '-y', '-o', path_out, path_in],
        "add": [texconv, 'texconv', '-ft', 'DDS', '-f', 'BC7_UNORM_SRGB', '-if', 'POINT_DITHER_DIFFUSION', '-sepalpha', '-sRGB', '-y', '-o', path_out, path_in],
        "ng": [texconv, 'texconv', '-ft', 'DDS', '-f', 'BC7_UNORM', '-sepalpha', '-y', '-o', path_out, path_in],
        "alphamask": [texconv, 'texconv', '-f', 'BC7_UNORM', '-if', 'POINT_DITHER_DIFFUSION', '-y', '-o', path_out, path_in],
        "tif": [texconv, 'texconv', '-ft', 'TIF', '-o', path_out, path_in],
        "custom": [texconv, 'texconv', '-o', path_out, path_in]
    }

    if preset in presets:
        args = presets[preset]

        if preset == "custom":
            args.append(settings)
        
        result = call_tool(args, path_out + 'conversion.log')
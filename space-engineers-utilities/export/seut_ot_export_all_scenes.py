import bpy
import os

from bpy.types  import Operator

from ..utils.seut_tool_utils    import get_tool_dir
from ..seut_errors              import *
from ..seut_utils               import prep_context, get_preferences
from .seut_ot_export            import export


class SEUT_OT_ExportAllScenes(Operator):
    """Exports all collections in all scenes and compresses them to MWM.\nScene needs to be in Object mode for export to be available"""
    bl_idname = "scene.export_all_scenes"
    bl_label = "Export All Scenes"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'


    def execute(self, context):
        """Exports all collections in all scenes and compresses them to MWM."""

        preferences = get_preferences()

        # Check for availability of FBX Importer
        result = check_toolpath(self, context, os.path.join(get_tool_dir(), 'FBXImporter.exe'), "Custom FBX Importer", "FBXImporter.exe")
        if result != {'CONTINUE'}:
            return result

        # Check for availability of MWM Builder
        result = check_toolpath(self, context, preferences.mwmb_path, "MWM Builder", "MwmBuilder.exe")
        if result != {'CONTINUE'}:
            return result

        # Check materials path
        materials_path = os.path.join(get_abs_path(preferences.asset_path), 'Materials')
        if preferences.asset_path == "":
            seut_report(self, context, 'ERROR', True, 'E012', "Asset Directory", get_abs_path(preferences.asset_path))
            return {'CANCELLED'}
        elif not os.path.isdir(materials_path):
            os.makedirs(materials_path, exist_ok=True)

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if result != {'CONTINUE'}:
            return result

        current_area = prep_context(context)
        original_scene = context.window.scene

        scene_counter = 0
        failed_counter = 0

        for idx, scn in enumerate(bpy.data.scenes):

            if 'SEUT' not in scn.view_layers:
                continue

            if scn.seut.sceneType in ['mainScene', 'subpart', 'character', 'character_animation', 'item']:

                scene_counter += 1
                context.window.scene = scn

                try:
                    result = export(self, context, idx != 0)

                    if result != {'FINISHED'}:
                        failed_counter += 1
                        seut_report(self, context, 'ERROR', True, 'E016', scn.name)

                except RuntimeError:
                    failed_counter += 1
                    seut_report(self, context, 'ERROR', True, 'E016', scn.name)

        context.window.scene = original_scene
        context.area.type = current_area

        seut_report(self, context, 'INFO', True, 'I008', scene_counter - failed_counter, scene_counter)

        return {'FINISHED'}
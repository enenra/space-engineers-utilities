import bpy

from bpy.types  import Operator

from .seut_ot_export    import export
from ..seut_errors      import check_export, seut_report
from ..seut_utils       import prep_context


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

        current_area = prep_context(context)
        original_scene = context.window.scene

        scene_counter = 0
        failed_counter = 0

        for scn in bpy.data.scenes:
            
            if not 'SEUT' in scn.view_layers:
                continue

            if scn.seut.sceneType == 'mainScene' or scn.seut.sceneType == 'subpart' or scn.seut.sceneType == 'character' or scn.seut.sceneType == 'character_animation':
                
                scene_counter += 1
                context.window.scene = scn

                try:
                    result = export(self, context)

                    if not result == {'FINISHED'}:
                        failed_counter += 1
                        seut_report(self, context, 'ERROR', True, 'E016', scn.name)

                except RuntimeError:
                    failed_counter += 1
                    seut_report(self, context, 'ERROR', True, 'E016', scn.name)
        
        context.window.scene = original_scene
        context.area.type = current_area
        
        seut_report(self, context, 'INFO', True, 'I008', scene_counter - failed_counter, scene_counter)

        return {'FINISHED'}
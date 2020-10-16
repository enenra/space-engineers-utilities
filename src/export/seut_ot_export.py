import bpy
import os
import glob
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator

from .seut_ot_export_main           import export_main
from .seut_ot_export_bs             import export_bs
from .seut_ot_export_hkt            import export_hkt
from .seut_ot_export_lod            import export_lod
from .seut_ot_export_mwm            import export_mwm
from .seut_ot_export_sbc            import export_sbc
from .seut_export_utils             import correct_for_export_type
from ..seut_preferences             import get_addon_version
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export


class SEUT_OT_Export(Operator):
    """Exports all collections in the current scene and compiles them to MWM"""
    bl_idname = "scene.export"
    bl_label = "Export Current Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        scene = context.scene
        collections = get_collections(scene)

        print("\n============================================================ Exporting Scene '" + scene.name + "' with SEUT " + str(get_addon_version()) + ".")

        # If mode is not object mode, export fails horribly.
        try:
            current_area = context.area.type
            context.area.type = 'VIEW_3D'
        except AttributeError:
            context.area.type = 'VIEW_3D'
            current_area = context.area.type
            
        if context.object is not None:
            context.object.select_set(False)
            context.view_layer.objects.active = None

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        # Character animations need at least one keyframe
        if scene.seut.sceneType == 'character_animation' and len(scene.timeline_markers) <= 0:
            scene.timeline_markers.new('F_00', frame=0)
            
        grid_scale = str(scene.seut.gridScale)
        subtype_id = str(scene.seut.subtypeId)
        rescale_factor = int(scene.seut.export_rescaleFactor)
        path = str(scene.seut.export_exportPath)
        
        # Exports large grid and character-type scenes
        if scene.seut.export_largeGrid or scene.seut.sceneType == 'character_animation' or scene.seut.sceneType == 'character':
            scene.seut.gridScale = 'large'
            scene.seut.subtypeId = correct_for_export_type(scene, scene.seut.subtypeId)

            if grid_scale == 'small':
                scene.seut.export_rescaleFactor = 5.0
            else:
                scene.seut.export_rescaleFactor = 1.0

            if scene.seut.export_exportPath.find("/small/") != -1:
                scene.seut.export_exportPath = scene.seut.export_exportPath.replace("/small/", "/large/")
            
            export_all(self, context)
        
        # Exports small grid scenes
        if scene.seut.export_smallGrid:
            scene.seut.gridScale = 'small'
            scene.seut.subtypeId = correct_for_export_type(scene, scene.seut.subtypeId)

            if grid_scale == 'large':
                scene.seut.export_rescaleFactor = 0.2
            else:
                scene.seut.export_rescaleFactor = 1.0

            if scene.seut.export_exportPath.find("/large/") != -1:
                scene.seut.export_exportPath = scene.seut.export_exportPath.replace("/large/", "/small/")
            
            export_all(self, context)

        # Resetting the variables
        if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
            scene.seut.subtypeId = subtype_id
            scene.seut.gridScale = grid_scale
            scene.seut.export_rescaleFactor = rescale_factor
            scene.seut.export_exportPath = path
            
        context.area.type = current_area

        return {'FINISHED'}

def export_all(self, context):
    """Exports all collections"""

    scene = context.scene

    export_bs(self, context)
    export_lod(self, context)
    result_main = export_main(self, context)
    export_hkt(self, context)

    if scene.seut.export_sbc and scene.seut.sceneType == 'mainScene':
        export_sbc(self, context)
    
    if result_main == {'FINISHED'}:
        export_mwm(self, context)
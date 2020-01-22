import os	
import re	
import bpy	
import shutil	
import tempfile	

from collections            import OrderedDict	
from os.path                import basename, join	
from string                 import Template	
from xml.etree              import ElementTree	
from mathutils              import Matrix	
from bpy_extras.io_utils    import axis_conversion, ExportHelper	

from .seut_havok_fbx       import save_single
from .seut_havok_options   import HAVOK_OPTION_FILE_CONTENT
from ..seut_export_utils   import ExportSettings, StdoutOperator, MissbehavingToolError, tool_path, write_to_log

# HARAG: FWD = 'Z'
# HARAG: UP = 'Y'
# HARAG: MATRIX_NORMAL = axis_conversion(to_forward=FWD, to_up=UP).to_4x4()
# HARAG: MATRIX_SCALE_DOWN = Matrix.Scale(0.2, 4) * MATRIX_NORMAL
def export_hktfbx_for_fbximporter(settings: ExportSettings, filepath, objects, kwargs = None):	
    kwargs = {	
        # HARAG: FBX operator defaults	
        # HARAG: Some internals of the fbx exporter depend on them and will step out of line if they are not present	
        'version': 'BIN7400', # This was removed in 2.8	
        'use_mesh_edges': False,	
        'use_custom_props': False, # HARAG: SE / Havok properties are hacked directly into the modified fbx importer in fbx.py	
        # HARAG:  anim, BIN7400	
        'bake_anim': False, # HARAG: no animation export to SE by default	
        'bake_anim_use_all_bones': True,	
        'bake_anim_use_nla_strips': True,	
        'bake_anim_use_all_actions': True,	
        'bake_anim_force_startend_keying': True,	
        'bake_anim_step': 1.0,	
        'bake_anim_simplify_factor': 1.0,	
        # HARAG:  anim, ASCII6100	
        'use_anim' : False, # HARAG: No animation export to SE by default	
        'use_anim_action_all' : True, # Not a Blender property.	
        'use_default_take' : True, # Not a Blender property.	
        'use_anim_optimize' : True, # Not a Blender property.	
        'anim_optimize_precision' : 6.0, # Not a Blender property.	
        # HARAG: Referenced files stay on automatic, MwmBuilder only cares about what's written to its .xml file	
        'path_mode': 'AUTO',	
        'embed_textures': False,	
        # HARAG: Batching isn't used because the export is driven by the node tree	
        'batch_mode': 'OFF',	
        'use_batch_own_dir': True,	
        'use_metadata': True,	
        # HARAG: Important settings for SE	
        'object_types': {'MESH', 'EMPTY'},	
        'axis_forward': 'Z', # STOLLIE: Normally a -Z in Blender source.	
        'axis_up': 'Y',	
        'bake_space_transform': True, # HARAG: The export to Havok needs this, it's off for the MwmFileNode	
        'use_mesh_modifiers': True,	
        'mesh_smooth_type': 'OFF', # STOLLIE: Normally 'FACE' in Blender source.	
        'use_tspace': False, # BLENDER: Why? Unity is expected to support tspace import...	
        # HARAG: For characters	
        'global_scale': 0.1, # Resizes Havok collision mesh in .hkt (fixed for Blender 2.79) Default=1.0 for 2.78c	
        'use_armature_deform_only': False,	
        'add_leaf_bones': False,	
        'armature_nodetype': 'NULL',	
        'primary_bone_axis': 'X', # STOLLIE: Swapped for SE, Y in Blender source.	
        'secondary_bone_axis': 'Y', # STOLLIE: Swapped for SE, X in Blender source. """	
    }	

    if kwargs:	
        if isinstance(kwargs, bpy.types.PropertyGroup):	
            kwargs = {prop : getattr(kwargs, prop) for prop in kwargs.rna_type.properties.keys()}	
        kwargs.update(**kwargs)	

    # these cannot be overriden and are always set here	
    kwargs['use_selection'] = False # because of context_objects	
    kwargs['context_objects'] = objects	

    global_matrix = axis_conversion(to_forward=kwargs['axis_forward'], to_up=kwargs['axis_up']).to_4x4()	
    scale = kwargs['global_scale']	

    if abs(1.0-scale) >= 0.000001:	
        global_matrix = Matrix.Scale(scale, 4) @ global_matrix	

    kwargs['global_matrix'] = global_matrix	

    return save_single(	
        settings.operator,	
        settings.scene,	
        settings.depsgraph,	
        filepath=filepath,	
        **kwargs # Stores any number of Keyword Arguments into a dictionary called 'fbxSettings'.	
    )	

def process_hktfbx_to_fbximporterhkt(settings: ExportSettings, srcfile, dstfile):	
    settings.callTool(	
        [settings.fbximporter, srcfile, dstfile],	
        logfile=dstfile+'.convert.log'	
    )	

def process_fbximporterhkt_to_final_hkt_for_mwm(self, scene, path, settings: ExportSettings, srcfile, dstfile, havokoptions=HAVOK_OPTION_FILE_CONTENT):	
    hko = tempfile.NamedTemporaryFile(mode='wt', prefix='space_engineers_', suffix=".hko", delete=False) # wt mode is write plus text mode.	
    try:	
        with hko.file as tempfile_to_process:	
            tempfile_to_process.write(havokoptions)	

        settings.callTool(	
            # -t is for standard ouput, -s designates a filter set (hko created above), -p designates path.	
            # Above referenced from running "hctStandAloneFilterManager.exe -h"	
            [settings.havokfilter, '-t', '-s', hko.name, '-p', dstfile, srcfile], 	
            logfile=dstfile+'.filter.log',	
            successfulExitCodes=[0,1])	
    finally:	
        os.remove(hko.name)	
        self.report({'INFO'}, "SEUT: Collision files have been created.") 
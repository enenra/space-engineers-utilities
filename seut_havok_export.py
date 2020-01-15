import os
import re
import bpy
import shutil
import subprocess
import tempfile

from collections            import OrderedDict
from os.path                import basename, join
from string                 import Template
from xml.etree              import ElementTree
from mathutils              import Matrix
from bpy_extras.io_utils    import axis_conversion, ExportHelper

from .seut_havok_fbx        import save_single
from .seut_havok_options    import HAVOK_OPTION_FILE_CONTENT

# STOLLIE: Standard output error operator class for catching error return codes.
class StdoutOperator():
    def report(self, type, message):
        print(message)

# STOLLIE: Assigning of above class to a global constant.
STDOUT_OPERATOR = StdoutOperator()

# STOLLIE: Processes subprocesss tool error messages, e.g. FBXImporter/HavokTool/MWMBuilder.
class MissbehavingToolError(subprocess.SubprocessError):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message

# STOLLIE: Returns a tools path from the user preferences config, e.g. FBXImporter/HavokTool/MWMBuilder.
def tool_path(propertyName, displayName, toolPath=None):
    """Gets path to tool from user preferences.

    Returns:
    toolPath
    """
    if toolPath is None:
        # STOLLIE: This is referencing the folder name the addon is stored in.
        toolPath = getattr(bpy.context.preferences.addons.get(__package__).preferences, propertyName)

    if toolPath is None:
        raise FileNotFoundError("%s is not configured", (displayName))

    toolPath = os.path.normpath(bpy.path.abspath(toolPath))
    if os.path.isfile(toolPath) is None:
        raise FileNotFoundError("%s: no such file %s" % (displayName, toolPath))

    return toolPath

# STOLLIE: Called by other methods to write to a log file when an errors occur.
def write_to_log(logfile, content, cmdline=None, cwd=None, loglines=[]):
    with open(logfile, 'wb') as log: # wb params here represent writing/create file and binary mode.
        if cwd:
            str = "Running from: %s \n" % (cwd)
            log.write(str.encode('utf-8'))

        if cmdline:
            str = "Command: %s \n" % (" ".join(cmdline))
            log.write(str.encode('utf-8'))

        for line in loglines:
            log.write(line.encode('utf-8'))
            log.write(b"\n")

        log.write(content)

class ExportSettings:
    def __init__(self, scene, depsgraph, mwmDir=None):
        self.scene = scene # ObjectSource.getObjects() uses .utils.scene() instead
        self.depsgraph = depsgraph
        self.operator = STDOUT_OPERATOR
        self.isLogToolOutput = True
        
        # set on first access, see properties below
        self._fbximporter = None
        self._havokfilter = None

    @property
    def fbximporter(self):
        if self._fbximporter == None:
            self._fbximporter = tool_path('pref_fbxImporterPath', 'Custom FBX Importer')
        return self._fbximporter

    @property
    def havokfilter(self):
        if self._havokfilter == None:
            self._havokfilter = tool_path('pref_havokPath', 'Havok Standalone Filter Tool')
        return self._havokfilter

    def callTool(self, cmdline, logfile=None, cwd=None, successfulExitCodes=[0], loglines=[], logtextInspector=None):
        try:
            out = subprocess.check_output(cmdline, cwd=cwd, stderr=subprocess.STDOUT)
            if self.isLogToolOutput and logfile:
                write_to_log(logfile, out, cmdline=cmdline, cwd=cwd, loglines=loglines)
            if logtextInspector is not None:
                logtextInspector(out)

        except subprocess.CalledProcessError as e:
            if self.isLogToolOutput and logfile:
                write_to_log(logfile, e.output, cmdline=cmdline, cwd=cwd, loglines=loglines)
            if e.returncode not in successfulExitCodes:
                raise
    
    def __getitem__(self, key): # makes all attributes available for parameter substitution
        if not type(key) is str or key.startswith('_'):
            raise KeyError(key)
        try:
            value = getattr(self, key)
            if value is None or type(value) is _FUNCTION_TYPE:
                raise KeyError(key)
            return value
        except AttributeError:
            raise KeyError(key)

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

    
    print("DEBUG:" + filepath)
    
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

def process_fbximporterhkt_to_final_hkt_for_mwm(settings: ExportSettings, srcfile, dstfile, havokoptions=HAVOK_OPTION_FILE_CONTENT):
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
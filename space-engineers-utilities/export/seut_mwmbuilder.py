import os
import glob

from .seut_export_utils         import ExportSettings
from ..utils.called_tool_type   import ToolType
from ..seut_errors              import seut_report


def mwmbuilder(self, context, path, mwm_path, settings: ExportSettings, mwmfile: str, materials_path: str):
    """Calls MWMB to compile files into MWM"""

    scene = context.scene
    result = False

    try:
        cmdline = [settings.mwmbuilder, '/f', '/s:' + path + '', '/m:' + scene.seut.subtypeId + '*.fbx', '/o:' + mwm_path + '', '/x:' + materials_path + '']
        
        result = settings.callTool(
            context,
            cmdline,
            ToolType(3),
            cwd=path,
            logfile=os.path.join(path, scene.seut.subtypeId + '.mwm.log')
        )

    finally:
        if scene.seut.export_deleteLooseFiles:
            file_list = [f for f in os.listdir(path) if (f"{scene.seut.subtypeId}_BS" in f or f"{scene.seut.subtypeId}_LOD" in f or f"{scene.seut.subtypeId}." in f) and (".fbx" in f or ".xml" in f or ".hkt" in f or ".log" in f)]

            try:
                for f in file_list:
                    os.remove(os.path.join(path, f))
            
                if result:
                    seut_report(self, context, 'INFO', True, 'I007', scene.name)

            except EnvironmentError:
                seut_report(self, context, 'ERROR', False, 'E020')
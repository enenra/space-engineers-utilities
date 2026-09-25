import os
import glob

from .seut_export_utils         import ExportSettings
from ..utils.called_tool_type   import ToolType
from ..utils.seut_paths         import to_tool_path
from ..seut_errors              import seut_report


def mwmbuilder(self, context, path, mwm_path, settings: ExportSettings, mwmfile: str, materials_path: str):
    """Calls MWMB to compile files into MWM"""

    scene = context.scene
    result = False

    try:
        cmdline = [settings.mwmbuilder, '/f', '/s:' + to_tool_path(path), '/m:' + scene.seut.subtypeId + '*.fbx', '/o:' + to_tool_path(mwm_path), '/x:' + to_tool_path(materials_path)]

        # cwd = tool dir so wine finds its sibling DLLs (assimp32.dll, VRage.*)
        result = settings.callTool(
            context,
            cmdline,
            ToolType(3),
            cwd=os.path.dirname(settings.mwmbuilder),
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
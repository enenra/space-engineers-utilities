import os
import glob

from .seut_export_utils         import ExportSettings
from ..utils.called_tool_type   import ToolType
from ..seut_errors              import seut_report


def mwmbuilder(self, context, path, mwm_path, settings: ExportSettings, mwmfile: str, materials_path: str):
    """Calls MWMB to compile files into MWM"""

    result = False

    try:
        scene = context.scene

        cmdline = [settings.mwmbuilder, '/f', '/s:' + path + '', '/m:' + scene.seut.subtypeId + '*.fbx', '/o:' + mwm_path + '', '/x:' + materials_path + '']
        
        result = settings.callTool(
            context,
            cmdline,
            ToolType(3),
            cwd=path,
            logfile=os.path.join(path, scene.seut.subtypeId + '.mwm.log')
        )

    finally:
        file_removal_list = [filename for filename in glob.glob(mwm_path + "*.hkt.mwm")]

        try:
            for filename in file_removal_list:
                os.remove(filename)
            
            if result:
                seut_report(self, context, 'INFO', True, 'I007', scene.name)

        except EnvironmentError:
            seut_report(self, context, 'ERROR', True, 'E020')
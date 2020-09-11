import os
import glob

from .seut_export_utils         import ExportSettings
from ..utils.called_tool_type   import ToolType
from ..seut_errors              import report_error

def mwmbuilder(self, context, path, mwmpath, settings: ExportSettings, mwmfile: str, materialspath):
    try:
        scene = context.scene
        cmdline = [settings.mwmbuilder, '/f', '/s:'+path+'', '/m:'+scene.seut.subtypeId+'*.fbx', '/o:'+mwmpath+'', '/x:'+materialspath+'']
        settings.callTool(
            context,
            cmdline,
            ToolType(3),
            cwd=path,
            logfile=path + scene.seut.subtypeId + '.log'            
        )
    finally:
        fileRemovalList = [fileName for fileName in glob.glob(mwmpath + "*.hkt.mwm")]
        try:
            for fileName in fileRemovalList:
                os.remove(fileName)

        except EnvironmentError:
            report_error(self, context, True, 'E020')
        
        self.report({'INFO'}, "SEUT: FBX and XML files of Scene '%s' have been compiled to MWM." % (scene.name))

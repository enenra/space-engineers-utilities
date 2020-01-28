import os
import glob

from .seut_export_utils     import ExportSettings

def mwmbuilder(self, context, path, settings: ExportSettings, mwmfile: str, materialspath):
    try:
        scene = context.scene
        cmdline = [settings.mwmbuilder, '/f', '/s:'+path+'', '/m:'+scene.seut.subtypeId+'*.fbx', '/o:'+path+'', '/x:'+materialspath+'']
        settings.callTool(cmdline, cwd=path, logfile=mwmfile+'.log')
        # os.remove(path + scene.seut.subtypeId + ".hkt.mwm")
    finally:
        fileRemovalList = [fileName for fileName in glob.glob(path + "*.hkt.mwm")]
        try:
            for fileName in fileRemovalList:
                os.remove(fileName)

        except EnvironmentError:
            self.report({'ERROR'}, "SEUT: Loose files file deletion failed. (020)")
            print("SEUT Error: File Deletion failed. (020)")
        
        self.report({'INFO'}, "SEUT: MWM file(s) have been created.")        

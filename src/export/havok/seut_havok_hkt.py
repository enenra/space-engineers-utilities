import os	
import re	
import bpy	
import shutil	
import tempfile	

from collections            import OrderedDict	
from os.path                import basename, join	
from string                 import Template	
from xml.etree              import ElementTree	

from .seut_havok_options   import HAVOK_OPTION_FILE_CONTENT
from ..seut_export_utils   import ExportSettings, StdoutOperator, MissbehavingToolError, tool_path, write_to_log

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
        hktBSfile1 = join(path, scene.seut.subtypeId + "_BS1.hkt")
        hktBSfile2 = join(path, scene.seut.subtypeId + "_BS2.hkt")
        hktBSfile3 = join(path, scene.seut.subtypeId + "_BS3.hkt")

        def copy(srcfile: str, dstfile: str):
            if srcfile is not None and dstfile != srcfile:
                shutil.copy2(srcfile, dstfile)

        if os.path.exists(srcfile):
            copy(srcfile, hktBSfile1)
            copy(srcfile, hktBSfile2)
            copy(srcfile, hktBSfile3)
            print("No Havok")
        
        self.report({'INFO'}, "SEUT: Collision files have been created.") 
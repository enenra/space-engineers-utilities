import os	
import re	
import bpy	
import shutil	
import tempfile	

from collections            import OrderedDict	
from os.path                import basename, join	
from string                 import Template	
from xml.etree              import ElementTree	

from .seut_havok_options        import HAVOK_OPTION_FILE_CONTENT
from ..seut_export_utils        import ExportSettings, StdoutOperator, MissbehavingToolError, tool_path, write_to_log
from ...utils.called_tool_type  import ToolType
from ...seut_collections        import seut_collections
from ...seut_errors             import seut_report


def process_hktfbx_to_fbximporterhkt(context, settings: ExportSettings, srcfile, dstfile):	
    settings.callTool(	
        context,
        [settings.fbximporter, srcfile, dstfile],	
        ToolType(1),
        logfile=dstfile+'.convert.log'
    )	


def process_fbximporterhkt_to_final_hkt_for_mwm(self, context, settings: ExportSettings, srcfile, dstfile, havokoptions=HAVOK_OPTION_FILE_CONTENT):
    
    hko = tempfile.NamedTemporaryFile(mode='wt', prefix='space_engineers_', suffix=".hko", delete=False) # wt mode is write plus text mode.	
    try:
        with hko.file as tempfile_to_process:
            tempfile_to_process.write(havokoptions)

        # -t is for standard ouput, -s designates a filter set (hko created above), -p designates path.	
        # Above referenced from running "hctStandAloneFilterManager.exe -h"	
        result = settings.callTool(
            context,
            [settings.havokfilter, '-t', '-s', hko.name, '-p', dstfile, srcfile],
            ToolType(2),
            logfile=dstfile+'.filter.log',
            successfulExitCodes=[0,1]
        )

    except:
        result = False

    finally:
        if context.scene.seut.export_deleteLooseFiles:
            os.remove(hko.name)

        if result:
            seut_report(self, context, 'INFO', True, 'I009')
import bpy
import os

from bpy.types                      import Operator

from .seut_export_utils             import isCollectionExcluded, export_XML, export_FBX
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral, errorCollection

class SEUT_OT_ExportMain(Operator):
    """Exports the main model"""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.get_Collections()
        return collections['main'] is not None
        
    def execute(self, context):
        """Exports the 'Main' collection"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_main'")

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == 'CONTINUE':
            return {result}

        SEUT_OT_ExportMain.export_Main(self, context, False)

        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_main'")

        return {'FINISHED'}
    
    def export_Main(self, context, partial):
        """Exports the 'Main' collection"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()

        # Checks whether collection exists, is excluded or is empty
        result = errorCollection(self, context, collections['main'], partial)
        if not result == 'CONTINUE':
            return {result}

        # Export XML if boolean is set.
        if scene.seut.export_xml:
            self.report({'INFO'}, "SEUT: Exporting XML for 'Main'.")
            export_XML(self, context, collections['main'])
        else:
            print("SEUT Info: 'XML' export disabled.")

        # Export FBX if boolean is set.
        if scene.seut.export_fbx:
            self.report({'INFO'}, "SEUT: Exporting FBX for 'Main'.")

            export_FBX(self, context, collections['main'])
        else:
            print("SEUT Info: 'FBX' export disabled.")
        
        return
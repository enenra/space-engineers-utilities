import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_export                 import SEUT_OT_Export

class SEUT_OT_ExportSBC(bpy.types.Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export SBC"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports a CubeBlocks definition to SBC"""

        scene = context.scene

        collections = SEUT_OT_RecreateCollections.get_collections()

        # Create new


        # Update existing


        return {'FINISHED'}
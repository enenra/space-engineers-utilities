import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_export                 import SEUT_OT_Export

class SEUT_OT_ExportMain(bpy.types.Operator):
    """Exports the main model"""
    bl_idname = "object.export_main"
    bl_label = "Export Main"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'Main' collection"""

        scene = context.scene

        collections = SEUT_OT_RecreateCollections.get_collections()

        # If main collection isn't found, error out.
        if collections['main'] == None:
            print("SEUT Error 002: Collection 'Main' not found. Export not possible.")
            return {'CANCELLED'}

        # Export XML if boolean is set.
        if scene.prop_export_xml:
            SEUT_OT_Export.export_XML(context, collections['main'])
            print("SEUT Info: Exporting XML for 'Main'.")

        # Export FBX if boolean is set.
        if scene.prop_export_fbx:
            SEUT_OT_Export.export_FBX(context, collections['main'])
            print("SEUT Info: Exporting FBX for 'Main'.")


        return {'FINISHED'}
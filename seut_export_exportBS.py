import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_export                 import SEUT_OT_Export

class SEUT_OT_ExportBS(bpy.types.Operator):
    """Exports Build Stages"""
    bl_idname = "object.export_bs"
    bl_label = "Export Build Stages"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'Build Stages' collections"""

        scene = context.scene

        collections = SEUT_OT_RecreateCollections.get_collections()

        # If no collections are found, error out.
        if collections['bs1'] == None and collections['bs2'] == None and collections['bs3'] == None:
            print("SEUT Error 003: No 'BS'-type collections found. Export not possible.")
            return {'CANCELLED'}

        # Export BS1, if present.
        if collections['bs1'] == None:
            print("SEUT Error 002: Collection 'BS1' not found. Export not possible.")
        else:
            if scene.prop_export_xml:
                SEUT_OT_Export.export_XML(context, collections['bs1'])
                print("SEUT Info: Exporting XML for 'BS1'.")
            if scene.prop_export_fbx:
                SEUT_OT_Export.export_FBX(context, collections['bs1'])
                print("SEUT Info: Exporting FBX for 'BS1'.")
        
        # Export BS2, if present.
        if collections['bs2'] == None:
            print("SEUT Error 002: Collection 'BS2' not found. Export not possible.")
        else:
            if scene.prop_export_xml:
                SEUT_OT_Export.export_XML(context, collections['bs2'])
                print("SEUT Info: Exporting XML for 'BS2'.")
            if scene.prop_export_fbx:
                SEUT_OT_Export.export_FBX(context, collections['bs2'])
                print("SEUT Info: Exporting FBX for 'BS2'.")

        # Export BS3, if present.
        if collections['bs3'] == None:
            print("SEUT Error 002: Collection 'BS3' not found. Export not possible.")
        else:
            if scene.prop_export_xml:
                SEUT_OT_Export.export_XML(context, collections['bs3'])
                print("SEUT Info: Exporting XML for 'BS3'.")
            if scene.prop_export_fbx:
                SEUT_OT_Export.export_FBX(context, collections['bs3'])
                print("SEUT Info: Exporting FBX for 'BS3'.")


        return {'FINISHED'}
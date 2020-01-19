import bpy
import os

from os.path                        import join
from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_havok_options            import HAVOK_OPTION_FILE_CONTENT
from .seut_ot_export                import ExportSettings
from .seut_havok_export             import export_hktfbx_for_fbximporter, process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm


class SEUT_OT_ExportHKT(Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports collision to HKT"""

        scene = context.scene
        depsgraph = None
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        settings = ExportSettings(scene, depsgraph)

        self.report({'DEBUG'}, "SEUT: Running operator: 'object.export_hkt'")

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "" or os.path.exists(scene.prop_export_exportPath) == False:
            self.report({'ERROR'}, "SEUT: No export folder defined or export folder doesn't exist. (ExportHKT: 003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if preferences.pref_fbxImporterPath == "":
            self.report({'ERROR'}, "SEUT: No Custom FBX Importer linked. (012)")
            return {'CANCELLED'}

        if preferences.pref_havokPath == "":
            self.report({'ERROR'}, "SEUT: No path to Havok Standalone Filter Tool defined. (013)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        if collections['hkt'] == None:
            self.report({'ERROR'}, "SEUT: Collection 'Collision' not found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['hkt'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Collision' is empty. Export not possible. (005)")
            return {'CANCELLED'}

        for obj in collections['hkt'].objects:
            context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_add(type='ACTIVE')

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return {'CANCELLED'}
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)

        # FBX export via Custom FBX Importer
        fbxhktfile = join(path, scene.prop_subtypeId + ".hkt.fbx")
        hktfile = join(path, scene.prop_subtypeId + ".hkt")
        
        export_hktfbx_for_fbximporter(settings, fbxhktfile, collections['hkt'].objects)

        # Then create the HKT file.
        process_hktfbx_to_fbximporterhkt(settings, fbxhktfile, hktfile)
        process_fbximporterhkt_to_final_hkt_for_mwm(self, settings, hktfile, hktfile)

        return {'FINISHED'}

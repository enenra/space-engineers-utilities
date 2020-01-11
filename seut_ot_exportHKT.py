import bpy
import os
import subprocess
import tempfile

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_havok_options            import HAVOK_OPTION_FILE_CONTENT

class SEUT_OT_ExportHKT(bpy.types.Operator):
    """Exports the HKT"""
    bl_idname = "object.export_hkt"
    bl_label = "Export HKT"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports collision to HKT"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get("space-engineers-utilities").preferences

        # Debug
        self.report({'DEBUG'}, "SEUT: OT Export HKT executed.")

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            return {'CANCELLED'}

        if preferences.pref_fbxImporterPath == "":
            self.report({'ERROR'}, "SEUT: No Custom FBX Importer linked. (012)")
            return {'CANCELLED'}

        if preferences.pref_havokPath == "":
            self.report({'ERROR'}, "SEUT: No path to Havok Standalone File Manager defined. (013)")
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

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)
        
        # Exporting the collection.
        # I can only export the currently active collection, so I need to set the target collection to active (for which I have to link it for some reason),
        # then export, then unlink. User won't see it and it shouldn't make a difference.
        bpy.context.scene.collection.children.link(collection)
        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        
        # Change stuff in preparation for FBX export

        # FBX export via Custom FBX Importer
        # subprocess.call(scene.pref_fbxImporterPath)


        # Then create the HKO file.
        # hko = tempfile.NamedTemporaryFile(mode='wt', prefix='space_engineers_', suffix=".hko", delete=False)
        # hko.write(HAVOK_OPTION_FILE_CONTENT)


        # Finally, call the havok standalone file manager with the two files.
        

        return {'FINISHED'}
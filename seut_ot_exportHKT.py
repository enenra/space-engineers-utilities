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
        preferences = bpy.context.preferences.addons.get(__package__).preferences

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
        # The try / finally ensures that the file is only removed after the export has completed.
        """
        try:
            hko = tempfile.NamedTemporaryFile(mode='wt', prefix='space_engineers_', suffix=".hko", delete=False)
            hko.write(HAVOK_OPTION_FILE_CONTENT)


        # Finally, call the havok standalone file manager with the two files.
        finally:
            os.remove(hko.name)
        """

        return {'FINISHED'}
    

    # A lot of this is taken directly from Harag's code:
    # https://github.com/Hotohori/se-blender/blob/efc49bbc106a617e01b9f0f2835a63e94a299b93/src/python/space_engineers/export.py
    def export_HKT(filepath, objects):
        fbxSettings = {
            # FBX operator defaults
            # some internals of the fbx exporter depend on them and will step out of line if they are not present
            'version': 'BIN7400',
            'use_mesh_edges': False,
            'use_custom_props': False, # SE / Havok properties are hacked directly into the modified fbx importer
            # anim, BIN7400
            'bake_anim': False, # no animation export to SE by default
            'bake_anim_use_all_bones': True,
            'bake_anim_use_nla_strips': True,
            'bake_anim_use_all_actions': True,
            'bake_anim_force_startend_keying': True,
            'bake_anim_step': 1.0,
            'bake_anim_simplify_factor': 1.0,
            # anim, ASCII6100
            'use_anim' : False, # no animation export to SE by default
            'use_anim_action_all' : True,
            'use_default_take' : True,
            'use_anim_optimize': True,
            'anim_optimize_precision' : 6.0,
            # referenced files stay on automatic, MwmBuilder only cares about what's written to its .xml file
            'path_mode': 'AUTO',
            'embed_textures': False,
            # batching isn't used because the export is driven by the node tree
            'batch_mode': 'OFF',
            'use_batch_own_dir': True,
            'use_metadata': True,
            # important settings for SE
            'object_types': {'MESH', 'EMPTY'},
            'axis_forward': 'Z',
            'axis_up': 'Y',
            'bake_space_transform': True, # the export to Havok needs this, it's off for the MwmFileNode
            'use_mesh_modifiers': True,
            'mesh_smooth_type': 'OFF',
            'use_tspace': settings.isUseTangentSpace, # TODO deprecate settings.isUseTangentSpace
            # for characters
            'global_scale': 0.1, # Resizes Havok collision mesh in .hkt (fixed for Blender 2.79) Default=1.0 for 2.78c
            'use_armature_deform_only': False,
            'add_leaf_bones': False,
            'armature_nodetype': 'NULL',
            'primary_bone_axis': 'X',
            'secondary_bone_axis': 'Y',
            # This is added in directly for SEUT.
            'use_selection': False,
            'context_objects': False,
        }
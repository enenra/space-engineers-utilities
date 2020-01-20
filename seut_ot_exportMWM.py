import bpy
import os

from os.path                        import join
from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_ot_export                import ExportSettings
from .seut_MWM_export               import mwmbuilder

class SEUT_OT_ExportMWM(Operator):
    """Compiles the MWM from the previously exported loose files"""
    bl_idname = "object.export_mwm"
    bl_label = "Compile MWM"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Compiles all loose files into a MWM"""

        scene = context.scene
        depsgraph = None
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences
        settings = ExportSettings(scene, depsgraph)
        mwmbPath = os.path.normpath(bpy.path.abspath(preferences.pref_mwmbPath))
        materialsPath = os.path.normpath(bpy.path.abspath(preferences.pref_materialsPath))

        self.report({'INFO'}, "SEUT: Running operator: 'object.export_mwm' ---------------------------")

        if preferences.pref_mwmbPath == "" or os.path.exists(mwmbPath) == False:
            self.report({'ERROR'}, "SEUT: Path to MWM Builder '%s' not valid. (018)" % (mwmbPath))
            self.report({'INFO'}, "SEUT: Path to MWM Builder '%s' not valid. (018)" % (mwmbPath))
            return {'CANCELLED'}

        if preferences.pref_materialsPath == "" or os.path.exists(materialsPath) == False:
            self.report({'ERROR'}, "SEUT: Path to Materials Folder '%s' not valid. (017)" % (materialsPath))
            self.report({'INFO'}, "SEUT: Path to Materials Folder '%s' not valid. (017)" % (materialsPath))
            return {'CANCELLED'}

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            self.report({'INFO'}, "SEUT: BLEND file must be saved before HKT can be exported to its directory. (008)")
            return {'CANCELLED'}
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)
            
            mwmpath = bpy.path.abspath(scene.prop_export_exportPath)

        # call mwmb
        fbxfile = join(path, scene.prop_subtypeId + ".fbx")
        havokfile = join(path, scene.prop_subtypeId + ".hkt")
        paramsfile = join(path, scene.prop_subtypeId + ".xml")
        mwmfile = join(mwmpath, scene.prop_subtypeId + ".mwm")
        materialspath = bpy.path.abspath(preferences.pref_materialsPath)

        mwmbuilder(self, context, path, settings, fbxfile, havokfile, paramsfile, mwmfile, materialspath)
        
        return {'FINISHED'}
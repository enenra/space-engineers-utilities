# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Space Engineers Utilities",
    "description": "This addon offers various utilities to make creating assets for Space Engineers easier.",
    "author": "enenra, Stollie",
    "version": (0, 9, 95),
    "dev_version": 0,
    "dev_tag": "rc",
    "blender": (2, 92, 0),
    "location": "View3D > Tools",
    "warning": "",
    "wiki_url": "https://space-engineers-modding.github.io/modding-reference/tools/3d-modelling/seut.html",
    "tracker_url": "https://github.com/enenra/space-engineers-utilities/issues",
    "git_url": "https://github.com/enenra/space-engineers-utilities",
    "support": "COMMUNITY",
    "category": "Modding"
}

import bpy

from bpy.app.handlers import persistent
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

from .empties.seut_empties                      import SEUT_MT_ContextMenu
from .empties.seut_empties                      import SEUT_PT_EmptyLink
from .empties.seut_empties                      import SEUT_EmptyHighlights
from .empties.seut_empties                      import SEUT_OT_HighlightObjectAdd
from .empties.seut_empties                      import SEUT_OT_HighlightObjectRemove
from .empties.seut_ot_add_highlight_empty       import SEUT_OT_AddHighlightEmpty
from .empties.seut_ot_add_dummy                 import SEUT_OT_AddDummy
from .empties.seut_ot_add_preset_subpart        import SEUT_OT_AddPresetSubpart
from .empties.seut_ot_add_custom_subpart        import SEUT_OT_AddCustomSubpart
from .export.seut_ot_export                     import SEUT_OT_Export
from .export.seut_ot_export_all_scenes          import SEUT_OT_ExportAllScenes
from .export.seut_ot_export_materials           import SEUT_OT_ExportMaterials
from .export.seut_ot_copy_export_options        import SEUT_OT_CopyExportOptions
from .importing.seut_ot_import                  import SEUT_OT_Import
from .importing.seut_ot_import_complete         import SEUT_OT_ImportComplete
from .importing.seut_ot_fix_positioning         import SEUT_OT_FixPositioning
from .importing.seut_ot_structure_conversion    import SEUT_OT_StructureConversion
from .importing.seut_ot_import_materials        import SEUT_OT_Import_Materials
from .materials.seut_materials                  import SEUT_Materials
from .materials.seut_materials                  import SEUT_PT_Panel_Materials
from .materials.seut_materials                  import SEUT_PT_Panel_MatLib
from .materials.seut_ot_remap_materials         import SEUT_OT_RemapMaterials
from .materials.seut_ot_refresh_matlibs         import SEUT_OT_RefreshMatLibs
from .materials.seut_ot_create_material         import SEUT_OT_MatCreate
from .materials.seut_materials                  import SEUT_UL_MatLib
from .particles.seut_particle_settings          import SEUT_ParticlePropertyKeys
from .particles.seut_particle_settings          import SEUT_ParticlePropertyValue2D
from .particles.seut_particle_settings          import SEUT_ParticleProperty
from .particles.seut_particle_settings          import SEUT_ParticleSettings
from .particles.seut_particle_settings          import SEUT_UL_ParticleProperties
from .particles.seut_particle_settings          import SEUT_UL_ParticlePropertyValues2D
from .particles.seut_ot_settings                import SEUT_OT_SettingsAdd
from .particles.seut_ot_properties              import SEUT_OT_PropertiesAdd
from .particles.seut_ot_properties              import SEUT_OT_PropertiesRemove
from .particles.seut_particles                  import SEUT_PT_Panel_Particle
from .particles.seut_particles                  import SEUT_PT_Panel_ParticleGeneration
from .particles.seut_particles                  import SEUT_PT_Panel_ExportParticle
from .particles.seut_particles                  import SEUT_PT_Panel_ImportParticle
from .utils.seut_ot_convertBoneNames            import SEUT_OT_ConvertBonesToBlenderFormat
from .utils.seut_ot_convertBoneNames            import SEUT_OT_ConvertBonesToSEFormat
from .utils.seut_updater                        import check_update
from .utils.seut_patch_blend                    import apply_patches
from .utils.seut_updater                        import SEUT_OT_GetUpdate
from .utils.seut_ot_semref_link                 import SEUT_OT_SEMREFLink
from .utils.seut_ot_discord_link                import SEUT_OT_DiscordLink
from .utils.seut_ot_issue_display               import SEUT_OT_IssueDisplay
from .utils.seut_ot_issue_display               import SEUT_OT_ClearIssues

from .seut_preferences                  import SEUT_AddonPreferences
from .seut_preferences                  import SEUT_OT_SetDevPaths
from .seut_preferences                  import get_addon_version, load_addon_prefs
from .seut_preferences                  import load_icons, unload_icons
from .seut_pt_toolbar                   import SEUT_PT_Panel
from .seut_pt_toolbar                   import SEUT_PT_Panel_Collections
from .seut_pt_toolbar                   import SEUT_PT_Panel_BoundingBox
from .seut_pt_toolbar                   import SEUT_PT_Panel_Mirroring
from .seut_pt_toolbar                   import SEUT_PT_Panel_Mountpoints
from .seut_pt_toolbar                   import SEUT_PT_Panel_IconRender
from .seut_pt_toolbar                   import SEUT_PT_Panel_Export
from .seut_pt_toolbar                   import SEUT_PT_Panel_Import
from .seut_bbox                         import SEUT_OT_BBox
from .seut_bbox                         import SEUT_OT_BBoxAuto
from .seut_mountpoints                  import SEUT_OT_AddMountpointArea
from .seut_collections                  import SEUT_Collection
from .seut_collections                  import SEUT_OT_RecreateCollections
from .seut_collections                  import SEUT_OT_CreateCollection
from .seut_ot_simple_navigation         import SEUT_OT_SimpleNavigation
from .seut_icon_render                  import SEUT_OT_IconRenderPreview
from .seut_icon_render                  import SEUT_OT_CopyRenderOptions
from .seut_scene                        import SEUT_MountpointAreas
from .seut_scene                        import SEUT_Scene
from .seut_object                       import SEUT_Object
from .seut_window_manager               import SEUT_IssueProperty
from .seut_window_manager               import SEUT_MatLibProps
from .seut_window_manager               import SEUT_WindowManager
from .seut_utils                        import get_preferences


classes = (
    SEUT_AddonPreferences,
    SEUT_OT_SetDevPaths,
    SEUT_PT_Panel,
    SEUT_PT_Panel_Collections,
    SEUT_PT_Panel_BoundingBox,
    SEUT_PT_Panel_Mirroring,
    SEUT_PT_Panel_Mountpoints,
    SEUT_PT_Panel_IconRender,
    SEUT_PT_Panel_Export,
    SEUT_PT_Panel_Import,
    SEUT_PT_Panel_Particle,
    SEUT_PT_Panel_ParticleGeneration,
    SEUT_PT_Panel_ExportParticle,
    SEUT_PT_Panel_ImportParticle,
    SEUT_PT_Panel_Materials,
    SEUT_PT_Panel_MatLib,
    SEUT_PT_EmptyLink,
    SEUT_EmptyHighlights,
    SEUT_OT_HighlightObjectAdd,
    SEUT_OT_HighlightObjectRemove,
    SEUT_MT_ContextMenu,
    SEUT_OT_GetUpdate,
    SEUT_OT_SEMREFLink,
    SEUT_OT_DiscordLink,
    SEUT_OT_IssueDisplay,
    SEUT_OT_ClearIssues,
    SEUT_OT_AddHighlightEmpty,
    SEUT_OT_AddDummy,
    SEUT_OT_AddPresetSubpart,
    SEUT_OT_AddCustomSubpart,
    SEUT_OT_Export,
    SEUT_OT_ExportAllScenes,
    SEUT_OT_CopyExportOptions,
    SEUT_OT_ExportMaterials,
    SEUT_OT_Import,
    SEUT_OT_ImportComplete,
    SEUT_OT_StructureConversion,
    SEUT_OT_Import_Materials,
    SEUT_OT_FixPositioning,
    SEUT_OT_RemapMaterials,
    SEUT_OT_ConvertBonesToBlenderFormat,
    SEUT_OT_ConvertBonesToSEFormat,
    SEUT_OT_BBox,
    SEUT_OT_BBoxAuto,
    SEUT_OT_AddMountpointArea,
    SEUT_OT_RecreateCollections,
    SEUT_OT_CreateCollection,
    SEUT_OT_SimpleNavigation,
    SEUT_OT_MatCreate,
    SEUT_OT_RefreshMatLibs,
    SEUT_Materials,
    SEUT_OT_IconRenderPreview,
    SEUT_OT_CopyRenderOptions,
    SEUT_ParticlePropertyKeys,
    SEUT_ParticlePropertyValue2D,
    SEUT_ParticleProperty,
    SEUT_ParticleSettings,
    SEUT_OT_SettingsAdd,
    SEUT_OT_PropertiesAdd,
    SEUT_OT_PropertiesRemove,
    SEUT_MountpointAreas,
    SEUT_Scene,
    SEUT_Collection,
    SEUT_Object,
    SEUT_IssueProperty,
    SEUT_MatLibProps,
    SEUT_WindowManager,
    SEUT_UL_MatLib,
    SEUT_UL_ParticleProperties,
    SEUT_UL_ParticlePropertyValues2D,
)


def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(menu_draw)
    bpy.types.VIEW3D_MT_add.append(menu_draw)

    bpy.types.Material.seut = PointerProperty(type=SEUT_Materials)
    bpy.types.Scene.seut = PointerProperty(type=SEUT_Scene)
    bpy.types.Object.seut = PointerProperty(type=SEUT_Object)
    bpy.types.Collection.seut = PointerProperty(type=SEUT_Collection)
    bpy.types.ParticleSettings.seut = PointerProperty(type=SEUT_ParticleSettings)
    bpy.types.WindowManager.seut = PointerProperty(type=SEUT_WindowManager)

    bpy.app.handlers.load_post.append(load_handler)

    from .seut_bau import bau_register
    bpy.app.timers.register(bau_register)

    seut_preferences.addon_version = bl_info['version']

    load_icons()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_draw)
    bpy.types.VIEW3D_MT_add.remove(menu_draw)

    del bpy.types.Material.seut
    del bpy.types.Scene.seut
    del bpy.types.Object.seut
    del bpy.types.Collection.seut
    del bpy.types.ParticleSettings.seut
    del bpy.types.WindowManager.seut

    bpy.app.handlers.load_post.remove(load_handler)

    unload_icons()


def menu_func(self, context):
    for cls in classes:
        if str(cls).find("SEUT_OT_") != -1:
            self.layout.operator(cls.bl_idname)


def menu_draw(self, context):
    layout = self.layout

    layout.separator()
    layout.label(text="Space Engineers Utilities")
    layout.menu('SEUT_MT_ContextMenu')

@persistent
def load_handler(dummy):
        
    # This exists to avoid errors on startup
    try:
        if seut_preferences.materials_path is not None:
            bpy.ops.wm.refresh_matlibs()
    except:
        pass
    
    # On first install this might cause issues, the try is a safety for that.
    try:
        check_update(get_addon_version())
        apply_patches()
        load_addon_prefs()
    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    register()

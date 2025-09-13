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
    "version": (1, 2, 1),
    "dev_version": 0,
    "dev_tag": "rc",
    "blender": (4, 5, 0),
    "location": "View3D > Tools",
    "doc_url": "https://spaceengineers.wiki.gg/wiki/Modding/Tools/Space_Engineers_Utilities",
    "tracker_url": "https://github.com/enenra/space-engineers-utilities/issues",
    "git_url": "https://github.com/enenra/space-engineers-utilities",
    "support": "COMMUNITY",
    "category": "Modding"
}

import bpy

from bpy.app.handlers   import persistent
from bpy.props          import PointerProperty

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
from .importing.seut_ot_structure_conversion    import SEUT_OT_StructureConversion
from .importing.seut_ot_import_materials        import SEUT_OT_Import_Materials
from .materials.seut_materials                  import SEUT_Materials
from .materials.seut_materials                  import SEUT_PT_Panel_Materials
from .materials.seut_materials                  import SEUT_PT_Panel_TextureConversion
from .materials.seut_materials                  import SEUT_PT_Panel_Shading
from .materials.seut_ot_remap_materials         import SEUT_OT_RemapMaterials
from .materials.seut_ot_create_material         import SEUT_OT_MatCreate
from .materials.seut_ot_texture_conversion      import SEUT_OT_ConvertTextures
from .materials.seut_ot_texture_conversion      import SEUT_OT_MassConvertTextures

from .planets.seut_planet_operators             import (SEUT_OT_Planet_RecreateSetup,
                                                        SEUT_OT_Planet_MaterialGroup_Add,
                                                        SEUT_OT_Planet_MaterialGroup_Remove,
                                                        SEUT_OT_Planet_DistributionRule_Add,
                                                        SEUT_OT_Planet_DistributionRule_Remove,
                                                        SEUT_OT_Planet_DistributionRuleLayer_Add,
                                                        SEUT_OT_Planet_DistributionRuleLayer_Remove,
                                                        SEUT_OT_Planet_EnvironmentItem_Add,
                                                        SEUT_OT_Planet_EnvironmentItem_Remove,
                                                        SEUT_OT_Planet_Biome_Add,
                                                        SEUT_OT_Planet_Biome_Remove,
                                                        SEUT_OT_Planet_Material_Add,
                                                        SEUT_OT_Planet_Material_Remove,
                                                        SEUT_OT_Planet_Item_Add,
                                                        SEUT_OT_Planet_Item_Remove,
                                                        SEUT_OT_Planet_OreMappings_Add,
                                                        SEUT_OT_Planet_OreMappings_Remove,
                                                        SEUT_OT_Planet_ExportAll,
                                                        SEUT_OT_Planet_Bake,
                                                        SEUT_OT_Planet_ImportSBC)
from .planets.seut_planet_ui                    import (SEUT_UL_PlanetDistributionRulesLayers,
                                                        SEUT_UL_PlanetDistributionRules,
                                                        SEUT_UL_PlanetMaterialGroups,
                                                        SEUT_UL_PlanetBiomes,
                                                        SEUT_UL_PlanetMaterials,
                                                        SEUT_UL_PlanetItems,
                                                        SEUT_UL_PlanetEnvironmentItems,
                                                        SEUT_UL_PlanetOreMappings,
                                                        SEUT_PT_Panel_Planet,
                                                        SEUT_PT_Panel_PlanetComplexMaterials,
                                                        SEUT_PT_Panel_PlanetEnvironmentItems,
                                                        SEUT_PT_Panel_PlanetOreMappings,
                                                        SEUT_PT_Panel_PlanetExport,
                                                        SEUT_PT_Panel_PlanetImport)
from .planets.seut_planets                      import (SEUT_PlanetPropertiesOreMappings,
                                                        SEUT_PlanetPropertiesBiomes,
                                                        SEUT_PlanetPropertiesDistributionRules,
                                                        SEUT_PlanetPropertiesDistributionRulesLayers,
                                                        SEUT_PlanetPropertiesEnvironmentItems,
                                                        SEUT_PlanetPropertiesItems,
                                                        SEUT_PlanetPropertiesMaterialGroups,
                                                        SEUT_PlanetPropertiesMaterials)

from .animations.seut_animation_operators       import (SEUT_OT_Animation_Export,
                                                        SEUT_OT_Animation_Add,
                                                        SEUT_OT_Animation_Remove,
                                                        SEUT_OT_Animation_Update,
                                                        SEUT_OT_Animation_SubpartEmpty_Add,
                                                        SEUT_OT_Animation_SubpartEmpty_Remove,
                                                        SEUT_OT_Animation_Action_Add,
                                                        SEUT_OT_Animation_Action_Remove)
from .animations.seut_animation_ui              import (SEUT_PT_Panel_Animation,
                                                        SEUT_PT_Panel_Keyframes,
                                                        SEUT_UL_Animations,
                                                        SEUT_UL_AnimationObjects)
from .animations.seut_animations                import (SEUT_Animations,
                                                        SEUT_AnimationObjects)

from .quicktools.seut_quicktools_ui             import SEUT_PT_Panel_QuickTools
from .quicktools.seut_quicktools_operators      import (SEUT_OT_QuickTools_BS_ApplyConstruction,
                                                        SEUT_OT_QuickTools_BS_CutAndSolidify,
                                                        SEUT_OT_QuickTools_GEN_OriginToSelected,
                                                        SEUT_OT_QuickTools_GEN_MirrorAndApply,
                                                        SEUT_OT_QuickTools_MAIN_AddBevels,
                                                        SEUT_OT_QuickTools_LOD_RemoveBevels,
                                                        SEUT_OT_QuickTools_HKT_ApplyTransforms)

from .utils.seut_ot_convertBoneNames            import SEUT_OT_ConvertBonesToBlenderFormat
from .utils.seut_ot_convertBoneNames            import SEUT_OT_ConvertBonesToSEFormat
from .utils.seut_repositories                   import SEUT_OT_GetUpdate
from .utils.seut_repositories                   import SEUT_OT_CheckUpdate
from .utils.seut_repositories                   import SEUT_OT_DownloadUpdate
from .utils.seut_repositories                   import update_register_repos, check_all_repo_updates
from .utils.seut_patch_blend                    import SEUT_OT_PatchBLEND
from .utils.seut_ot_docu_link                   import SEUT_OT_DocuLink
from .utils.seut_ot_discord_link                import SEUT_OT_DiscordLink
from .utils.seut_ot_issue_display               import SEUT_OT_IssueDisplay
from .utils.seut_ot_issue_display               import SEUT_OT_DeleteIssue
from .utils.seut_ot_issue_display               import SEUT_OT_ClearIssues
from .utils.seut_ot_issue_display               import SEUT_OT_ExportLog

from .seut_preferences                  import SEUT_AddonPreferences
from .seut_preferences                  import SEUT_OT_SetDevPaths
from .seut_preferences                  import load_addon_prefs, init_relocate_matlibs, load_configs
from .seut_preferences                  import load_icons, unload_icons
from .seut_pt_toolbar                   import SEUT_PT_Panel
from .seut_pt_toolbar                   import SEUT_PT_Panel_Collections
from .seut_pt_toolbar                   import SEUT_PT_Panel_BoundingBox
from .seut_pt_toolbar                   import SEUT_PT_Panel_Mirroring
from .seut_pt_toolbar                   import SEUT_PT_Panel_Mountpoints
from .seut_pt_toolbar                   import SEUT_PT_Panel_IconRender
from .seut_pt_toolbar                   import SEUT_PT_Panel_Export
from .seut_pt_toolbar                   import SEUT_PT_Panel_Import
from .seut_asset                        import SEUT_Asset
from .seut_asset                        import SEUT_PT_Panel_Asset
from .seut_bbox                         import SEUT_OT_BBox
from .seut_mountpoints                  import SEUT_OT_AddMountpointArea
from .seut_collections                  import SEUT_Collection
from .seut_collections                  import SEUT_OT_RecreateCollections
from .seut_collections                  import SEUT_OT_CreateCollection
from .seut_ot_simple_navigation         import SEUT_OT_SimpleNavigation
from .seut_icon_render                  import SEUT_OT_IconRenderPreview
from .seut_icon_render                  import SEUT_OT_CopyRenderOptions
from .seut_icon_render                  import SEUT_OT_CopyRenderOffset
from .seut_scene                        import SEUT_MountpointAreas
from .seut_scene                        import SEUT_Scene
from .seut_object                       import SEUT_Object
from .seut_text                         import SEUT_RepositoryProperty
from .seut_text                         import SEUT_IssueProperty
from .seut_text                         import SEUT_Text
from .seut_utils                        import SEUT_OT_UpdateSubpartInstances, get_seut_blend_data
from .seut_errors                       import init_logging


classes = (
    SEUT_AddonPreferences,
    SEUT_OT_SetDevPaths,
    SEUT_PT_Panel,
    SEUT_PT_Panel_QuickTools,
    SEUT_PT_Panel_Collections,
    SEUT_PT_Panel_BoundingBox,
    SEUT_PT_Panel_Mirroring,
    SEUT_PT_Panel_Mountpoints,
    SEUT_PT_Panel_IconRender,
    SEUT_PT_Panel_Animation,
    SEUT_PT_Panel_Export,
    SEUT_PT_Panel_Import,
    SEUT_PT_Panel_Materials,
    SEUT_PT_Panel_TextureConversion,
    SEUT_PT_Panel_Asset,
    SEUT_PT_EmptyLink,
    SEUT_PT_Panel_Shading,
    SEUT_Asset,
    SEUT_EmptyHighlights,
    SEUT_OT_HighlightObjectAdd,
    SEUT_OT_HighlightObjectRemove,
    SEUT_MT_ContextMenu,
    SEUT_OT_PatchBLEND,
    SEUT_OT_GetUpdate,
    SEUT_OT_CheckUpdate,
    SEUT_OT_DownloadUpdate,
    SEUT_OT_DocuLink,
    SEUT_OT_DiscordLink,
    SEUT_OT_IssueDisplay,
    SEUT_OT_DeleteIssue,
    SEUT_OT_ClearIssues,
    SEUT_OT_ExportLog,
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
    SEUT_OT_RemapMaterials,
    SEUT_OT_ConvertBonesToBlenderFormat,
    SEUT_OT_ConvertBonesToSEFormat,
    SEUT_OT_BBox,
    SEUT_OT_AddMountpointArea,
    SEUT_OT_RecreateCollections,
    SEUT_OT_CreateCollection,
    SEUT_OT_SimpleNavigation,
    SEUT_OT_MatCreate,
    SEUT_OT_ConvertTextures,
    SEUT_OT_MassConvertTextures,
    SEUT_Materials,
    SEUT_OT_IconRenderPreview,
    SEUT_OT_CopyRenderOptions,
    SEUT_OT_CopyRenderOffset,

    SEUT_OT_Planet_RecreateSetup,
    SEUT_OT_Planet_MaterialGroup_Add,
    SEUT_OT_Planet_MaterialGroup_Remove,
    SEUT_OT_Planet_DistributionRule_Add,
    SEUT_OT_Planet_DistributionRule_Remove,
    SEUT_OT_Planet_DistributionRuleLayer_Add,
    SEUT_OT_Planet_DistributionRuleLayer_Remove,
    SEUT_OT_Planet_EnvironmentItem_Add,
    SEUT_OT_Planet_EnvironmentItem_Remove,
    SEUT_OT_Planet_Biome_Add,
    SEUT_OT_Planet_Biome_Remove,
    SEUT_OT_Planet_Material_Add,
    SEUT_OT_Planet_Material_Remove,
    SEUT_OT_Planet_Item_Add,
    SEUT_OT_Planet_Item_Remove,
    SEUT_OT_Planet_OreMappings_Add,
    SEUT_OT_Planet_OreMappings_Remove,
    SEUT_OT_Planet_ExportAll,
    SEUT_OT_Planet_Bake,
    SEUT_OT_Planet_ImportSBC,
    SEUT_UL_PlanetDistributionRulesLayers,
    SEUT_UL_PlanetDistributionRules,
    SEUT_UL_PlanetMaterialGroups,
    SEUT_UL_PlanetBiomes,
    SEUT_UL_PlanetMaterials,
    SEUT_UL_PlanetItems,
    SEUT_UL_PlanetEnvironmentItems,
    SEUT_UL_PlanetOreMappings,
    SEUT_PT_Panel_Planet,
    SEUT_PT_Panel_PlanetComplexMaterials,
    SEUT_PT_Panel_PlanetEnvironmentItems,
    SEUT_PT_Panel_PlanetOreMappings,
    SEUT_PT_Panel_PlanetExport,
    SEUT_PT_Panel_PlanetImport,
    SEUT_PlanetPropertiesDistributionRulesLayers,
    SEUT_PlanetPropertiesDistributionRules,
    SEUT_PlanetPropertiesMaterialGroups,
    SEUT_PlanetPropertiesBiomes,
    SEUT_PlanetPropertiesMaterials,
    SEUT_PlanetPropertiesItems,
    SEUT_PlanetPropertiesEnvironmentItems,
    SEUT_PlanetPropertiesOreMappings,

    SEUT_AnimationObjects,
    SEUT_Animations,
    SEUT_OT_Animation_Export,
    SEUT_OT_Animation_Add,
    SEUT_OT_Animation_Remove,
    SEUT_OT_Animation_Update,
    SEUT_OT_Animation_SubpartEmpty_Add,
    SEUT_OT_Animation_SubpartEmpty_Remove,
    SEUT_OT_Animation_Action_Add,
    SEUT_OT_Animation_Action_Remove,
    SEUT_UL_Animations,
    SEUT_UL_AnimationObjects,
    SEUT_PT_Panel_Keyframes,

    SEUT_OT_QuickTools_BS_ApplyConstruction,
    SEUT_OT_QuickTools_BS_CutAndSolidify,
    SEUT_OT_QuickTools_GEN_OriginToSelected,
    SEUT_OT_QuickTools_GEN_MirrorAndApply,
    SEUT_OT_QuickTools_MAIN_AddBevels,
    SEUT_OT_QuickTools_LOD_RemoveBevels,
    SEUT_OT_QuickTools_HKT_ApplyTransforms,

    SEUT_MountpointAreas,
    SEUT_Scene,
    SEUT_Collection,
    SEUT_Object,
    SEUT_RepositoryProperty,
    SEUT_IssueProperty,
    SEUT_Text,
    SEUT_OT_UpdateSubpartInstances,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(menu_draw)
    bpy.types.VIEW3D_MT_add.append(menu_draw)

    bpy.types.AssetMetaData.seut = PointerProperty(type=SEUT_Asset)
    bpy.types.Material.seut = PointerProperty(type=SEUT_Materials)
    bpy.types.Scene.seut = PointerProperty(type=SEUT_Scene)
    bpy.types.Object.seut = PointerProperty(type=SEUT_Object)
    bpy.types.Collection.seut = PointerProperty(type=SEUT_Collection)
    bpy.types.Text.seut = PointerProperty(type=SEUT_Text)

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

    del bpy.types.AssetMetaData.seut
    del bpy.types.Material.seut
    del bpy.types.Scene.seut
    del bpy.types.Object.seut
    del bpy.types.Collection.seut
    del bpy.types.Text.seut

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

    try:
        init_relocate_matlibs()
        update_register_repos()
        check_all_repo_updates()
        load_addon_prefs()
        load_configs()
        init_logging()

        data = get_seut_blend_data()
        if data.seut.bBox == 'on':
            data.seut.bBox = 'on'

    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    register()
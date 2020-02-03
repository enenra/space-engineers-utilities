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
    "author": "enenra, Stollie, Kamikaze",
    "version": (0, 7, 1),
    "blender": (2, 81, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/enenra/space-engineers-utilities",
    "tracker_url": "https://github.com/enenra/space-engineers-utilities/issues",
    "support": "COMMUNITY",
    "category": "Scene"
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

from .empties.seut_mt_contextMenu           import SEUT_MT_ContextMenu
from .empties.seut_pt_emptyMenu             import SEUT_PT_EmptyLink
from .empties.seut_ot_addHighlightEmpty     import SEUT_OT_AddHighlightEmpty
from .empties.seut_ot_addDummy              import SEUT_OT_AddDummy
from .empties.seut_ot_addPresetSubpart      import SEUT_OT_AddPresetSubpart
from .empties.seut_ot_addCustomSubpart      import SEUT_OT_AddCustomSubpart
from .empties.seut_ot_emptyToCubeType       import SEUT_OT_EmptiesToCubeType
from .export.seut_ot_exportMain             import SEUT_OT_ExportMain
from .export.seut_ot_exportBS               import SEUT_OT_ExportBS
from .export.seut_ot_exportLOD              import SEUT_OT_ExportLOD
from .export.seut_ot_exportHKT              import SEUT_OT_ExportHKT
from .export.seut_ot_exportSBC              import SEUT_OT_ExportSBC
from .export.seut_ot_exportMWM              import SEUT_OT_ExportMWM
from .export.seut_ot_export                 import SEUT_OT_Export
from .export.seut_ot_exportAllScenes        import SEUT_OT_ExportAllScenes
from .export.seut_ot_exportMaterials        import SEUT_OT_ExportMaterials
from .materials.seut_materials              import SEUT_Materials
from .materials.seut_pt_matToolbar          import SEUT_PT_Panel_Materials
from .materials.seut_pt_matToolbar          import SEUT_PT_Panel_MatLib
from .materials.seut_ot_remapMaterials      import SEUT_OT_RemapMaterials
from .materials.seut_ot_refreshMatLibs      import SEUT_OT_RefreshMatLibs
from .materials.seut_ot_matCreate           import SEUT_OT_MatCreate
from .materials.seut_matLib                 import SEUT_MatLibProps
from .materials.seut_matLib                 import SEUT_UL_MatLib

from .seut_preferences              import SEUT_AddonPreferences
from .seut_pt_toolbar               import SEUT_PT_Panel
from .seut_pt_toolbar               import SEUT_PT_Panel_BoundingBox
from .seut_pt_toolbar               import SEUT_PT_Panel_Export
from .seut_pt_toolbar               import SEUT_PT_Panel_Import
from .seut_ot_import                import SEUT_OT_Import
from .seut_ot_structureConversion   import SEUT_OT_StructureConversion
from .seut_ot_gridScale             import SEUT_OT_GridScale
from .seut_ot_bBox                  import SEUT_OT_BBox
from .seut_ot_bBoxAuto              import SEUT_OT_BBoxAuto
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_scene                    import SEUT_Scene
from .seut_object                   import SEUT_Object
from .seut_windowManager            import SEUT_WindowManager


classes = (
    SEUT_AddonPreferences,
    SEUT_PT_Panel,
    SEUT_PT_Panel_BoundingBox,
    SEUT_PT_Panel_Export,
    SEUT_PT_Panel_Import,
    SEUT_PT_Panel_Materials,
    SEUT_PT_Panel_MatLib,
    SEUT_PT_EmptyLink,
    SEUT_OT_ExportMaterials,
    SEUT_MT_ContextMenu,
    SEUT_OT_AddHighlightEmpty,
    SEUT_OT_AddDummy,
    SEUT_OT_AddPresetSubpart,
    SEUT_OT_AddCustomSubpart,
    SEUT_OT_Export,
    SEUT_OT_ExportAllScenes,
    SEUT_OT_ExportMain,
    SEUT_OT_ExportBS,
    SEUT_OT_ExportLOD,
    SEUT_OT_ExportHKT,
    SEUT_OT_ExportSBC,
    SEUT_OT_ExportMWM,
    SEUT_OT_Import,
    SEUT_OT_StructureConversion,
    SEUT_OT_RemapMaterials,
    SEUT_OT_EmptiesToCubeType,
    SEUT_OT_GridScale,
    SEUT_OT_BBox,
    SEUT_OT_BBoxAuto,
    SEUT_OT_RecreateCollections,
    SEUT_OT_MatCreate,
    SEUT_OT_RefreshMatLibs,
    SEUT_Materials,
    SEUT_Scene,
    SEUT_Object,
    SEUT_WindowManager,
    SEUT_MatLibProps,
    SEUT_UL_MatLib,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(menu_draw)

    bpy.types.Material.seut = PointerProperty(type=SEUT_Materials)
    bpy.types.Scene.seut = PointerProperty(type=SEUT_Scene)
    bpy.types.Object.seut = PointerProperty(type=SEUT_Object)
    bpy.types.WindowManager.seut = PointerProperty(type=SEUT_WindowManager)

    bpy.types.WindowManager.matlibs = CollectionProperty(type=SEUT_MatLibProps)
    bpy.types.WindowManager.matlib_index = IntProperty(name="Enable or Disable MatLibs in the Materials folder", default=0)

    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_draw)

    del bpy.types.Material.seut
    del bpy.types.Scene.seut
    del bpy.types.Object.seut
    del bpy.types.WindowManager.seut

    del bpy.types.WindowManager.matlibs
    del bpy.types.WindowManager.matlib_index

    bpy.app.handlers.load_post.remove(load_handler)


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
    bpy.ops.object.gridscale()
    try:
        bpy.ops.scene.refresh_matlibs()
    except RuntimeError:
        print("SEUT Error: Available MatLibs could not be refreshed. (021)")


addon_keymaps = []

if __name__ == "__main__":
    register()

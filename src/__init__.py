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
    "version": (0, 5, 0),
    "blender": (2, 81, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/enenra/space-engineers-utilities",
    "tracker_url": "https://github.com/enenra/space-engineers-utilities/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

from .seut_preferences              import SEUT_AddonPreferences
from .seut_pt_toolbar               import SEUT_PT_Panel
from .seut_pt_toolbar               import SEUT_PT_Panel_BoundingBox
from .seut_pt_toolbar               import SEUT_PT_Panel_Export
from .seut_pt_toolbar               import SEUT_PT_Panel_Import
from .seut_pt_toolbar               import SEUT_PT_Panel_Materials
from .seut_mt_contextMenu           import SEUT_MT_ContextMenu
from .seut_ot_addHighlightEmpty     import SEUT_OT_AddHighlightEmpty
from .seut_ot_addDummy              import SEUT_OT_AddDummy
from .seut_ot_addPresetSubpart      import SEUT_OT_AddPresetSubpart
from .seut_ot_addCustomSubpart      import SEUT_OT_AddCustomSubpart
from .seut_ot_exportMain            import SEUT_OT_ExportMain
from .seut_ot_exportBS              import SEUT_OT_ExportBS
from .seut_ot_exportLOD             import SEUT_OT_ExportLOD
from .seut_ot_exportHKT             import SEUT_OT_ExportHKT
from .seut_ot_exportSBC             import SEUT_OT_ExportSBC
from .seut_ot_exportMWM             import SEUT_OT_ExportMWM
from .seut_ot_export                import SEUT_OT_Export
from .seut_ot_import                import SEUT_OT_Import
from .seut_ot_remapMaterials        import SEUT_OT_RemapMaterials
from .seut_ot_emptyToCubeType       import SEUT_OT_EmptiesToCubeType
from .seut_ot_gridScale             import SEUT_OT_GridScale
from .seut_ot_bBox                  import SEUT_OT_BBox
from .seut_ot_bBoxAuto              import SEUT_OT_BBoxAuto
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_ot_matCreate             import SEUT_OT_MatCreate
from .seut_materials                import SEUT_Materials
from .seut_scene                    import SEUT_Scene

def register():
    bpy.utils.register_class(SEUT_AddonPreferences)
    bpy.utils.register_class(SEUT_PT_Panel)
    bpy.utils.register_class(SEUT_PT_Panel_BoundingBox)
    bpy.utils.register_class(SEUT_PT_Panel_Export)
    bpy.utils.register_class(SEUT_PT_Panel_Import)
    bpy.utils.register_class(SEUT_PT_Panel_Materials)
    bpy.utils.register_class(SEUT_MT_ContextMenu)
    bpy.utils.register_class(SEUT_OT_AddHighlightEmpty)
    bpy.utils.register_class(SEUT_OT_AddDummy)
    bpy.utils.register_class(SEUT_OT_AddPresetSubpart)
    bpy.utils.register_class(SEUT_OT_AddCustomSubpart)
    bpy.utils.register_class(SEUT_OT_Export)
    bpy.utils.register_class(SEUT_OT_ExportMain)
    bpy.utils.register_class(SEUT_OT_ExportBS)
    bpy.utils.register_class(SEUT_OT_ExportLOD)
    bpy.utils.register_class(SEUT_OT_ExportHKT)
    bpy.utils.register_class(SEUT_OT_ExportSBC)
    bpy.utils.register_class(SEUT_OT_ExportMWM)
    bpy.utils.register_class(SEUT_OT_Import)
    bpy.utils.register_class(SEUT_OT_RemapMaterials)
    bpy.utils.register_class(SEUT_OT_EmptiesToCubeType)
    bpy.utils.register_class(SEUT_OT_GridScale)
    bpy.utils.register_class(SEUT_OT_BBox)
    bpy.utils.register_class(SEUT_OT_BBoxAuto)
    bpy.utils.register_class(SEUT_OT_RecreateCollections)
    bpy.utils.register_class(SEUT_OT_MatCreate)
    bpy.utils.register_class(SEUT_Materials)
    bpy.utils.register_class(SEUT_Scene)
        
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_draw)
    bpy.types.Material.seut = bpy.props.PointerProperty(type=SEUT_Materials)
    bpy.types.Scene.seut = bpy.props.PointerProperty(type=SEUT_Scene)

def unregister():
    bpy.utils.unregister_class(SEUT_AddonPreferences)
    bpy.utils.unregister_class(SEUT_PT_Panel)
    bpy.utils.unregister_class(SEUT_PT_Panel_BoundingBox)
    bpy.utils.unregister_class(SEUT_PT_Panel_Export)
    bpy.utils.unregister_class(SEUT_PT_Panel_Import)
    bpy.utils.unregister_class(SEUT_PT_Panel_Materials)
    bpy.utils.unregister_class(SEUT_MT_ContextMenu)
    bpy.utils.unregister_class(SEUT_OT_AddHighlightEmpty)
    bpy.utils.unregister_class(SEUT_OT_AddDummy)
    bpy.utils.unregister_class(SEUT_OT_AddPresetSubpart)
    bpy.utils.unregister_class(SEUT_OT_AddCustomSubpart)
    bpy.utils.unregister_class(SEUT_OT_Export)
    bpy.utils.unregister_class(SEUT_OT_ExportMain)
    bpy.utils.unregister_class(SEUT_OT_ExportBS)
    bpy.utils.unregister_class(SEUT_OT_ExportLOD)
    bpy.utils.unregister_class(SEUT_OT_ExportHKT)
    bpy.utils.unregister_class(SEUT_OT_ExportSBC)
    bpy.utils.unregister_class(SEUT_OT_ExportMWM)
    bpy.utils.unregister_class(SEUT_OT_Import)
    bpy.utils.unregister_class(SEUT_OT_RemapMaterials)
    bpy.utils.unregister_class(SEUT_OT_EmptiesToCubeType)
    bpy.utils.unregister_class(SEUT_OT_GridScale)
    bpy.utils.unregister_class(SEUT_OT_BBox)
    bpy.utils.unregister_class(SEUT_OT_BBoxAuto)
    bpy.utils.unregister_class(SEUT_OT_RecreateCollections)
    bpy.utils.unregister_class(SEUT_OT_MatCreate)
    bpy.utils.unregister_class(SEUT_Materials)
    bpy.utils.unregister_class(SEUT_Scene)
        
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_draw)

    del bpy.types.Material.seut
    del bpy.types.Scene.seut


def menu_func(self, context):
    self.layout.operator(SEUT_OT_AddHighlightEmpty.bl_idname)
    self.layout.operator(SEUT_OT_AddDummy.bl_idname)
    self.layout.operator(SEUT_OT_AddPresetSubpart.bl_idname)
    self.layout.operator(SEUT_OT_AddCustomSubpart.bl_idname)

    self.layout.operator(SEUT_OT_Export.bl_idname)
    self.layout.operator(SEUT_OT_ExportMain.bl_idname)
    self.layout.operator(SEUT_OT_ExportBS.bl_idname)
    self.layout.operator(SEUT_OT_ExportLOD.bl_idname)
    self.layout.operator(SEUT_OT_ExportHKT.bl_idname)
    self.layout.operator(SEUT_OT_ExportMWM.bl_idname)

    self.layout.operator(SEUT_OT_Import.bl_idname)
    self.layout.operator(SEUT_OT_RemapMaterials.bl_idname)
    self.layout.operator(SEUT_OT_EmptiesToCubeType.bl_idname)

    self.layout.operator(SEUT_OT_GridScale.bl_idname)
    self.layout.operator(SEUT_OT_BBox.bl_idname)
    self.layout.operator(SEUT_OT_BBoxAuto.bl_idname)
    self.layout.operator(SEUT_OT_RecreateCollections.bl_idname)
    
    self.layout.operator(SEUT_OT_MatCreate.bl_idname)

def menu_draw(self, context):
    layout = self.layout

    layout.separator()
    layout.label(text="Space Engineers Utilities")
    layout.menu('SEUT_MT_ContextMenu')

addon_keymaps = []

if __name__ == "__main__":
    register()

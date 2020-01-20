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
    "version": (0, 2, 5),
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
        
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_draw)
    bpy.types.Material.seut = bpy.props.PointerProperty(type=SEUT_Materials)

    # Grid Scale
    bpy.types.Scene.prop_gridScale = bpy.props.EnumProperty(
        name='Scale',
        items=(
            ('large', 'Large', 'Large grid blocks (2.5m)'),
            ('small', 'Small', 'Small grid blocks (0.5m)')
            ),
        default='large',
        update=update_GridScale
    )

    # Bounding Box
    bpy.types.Scene.prop_bBoxToggle = bpy.props.EnumProperty(
        name='Bounding Box',
        items=(
            ('on', 'On', ''),
            ('off', 'Off', '')
            ),
        default='off',
        update=update_BBox
    )
    bpy.types.Scene.prop_bBox_X = IntProperty(
        name="X:",
        description="",
        default=1,
        min=1
    )
    bpy.types.Scene.prop_bBox_Y = IntProperty(
        name="Y:",
        description="",
        default=1,
        min=1
    )
    bpy.types.Scene.prop_bBox_Z = IntProperty(
        name="Z:",
        description="",
        default=1,
        min=1
    )

    # Export
    bpy.types.Scene.prop_subtypeId = StringProperty(
        name="SubtypeId",
        description="The SubtypeId for this model"
    )
    bpy.types.Scene.prop_export_deleteLooseFiles = BoolProperty(
        name="Delete Loose Files",
        description="Whether the intermediary files should be deleted after the MWM has been created",
        default=True
    )
    bpy.types.Scene.prop_export_fbx = BoolProperty(
        name="FBX",
        description="Whether to export to FBX",
        default=True
    )
    bpy.types.Scene.prop_export_xml = BoolProperty(
        name="XML",
        description="Whether to export to XML",
        default=True
    )
    bpy.types.Scene.prop_export_hkt = BoolProperty(
        name="HKT",
        description="Whether to export to HKT (Collision model filetype)",
        default=True
    )
    bpy.types.Scene.prop_export_sbc = BoolProperty(
        name="SBC",
        description="Whether to export to SBC (CubeBlocks definition)",
        default=True
    )
    bpy.types.Scene.prop_export_rescaleFactor = FloatProperty(
        name="Rescale Factor:",
        description="What to set the Rescale Factor to",
        default=1,
        min=0
    )
    bpy.types.Scene.prop_export_exportPath = StringProperty(
        name="Export Folder",
        description="What folder to export to",
        subtype="DIR_PATH"
    )
    bpy.types.Scene.prop_export_lod1Distance = IntProperty(
        name="LOD1:",
        description="From what distance this LOD should display",
        default=25,
        min=0
    )
    bpy.types.Scene.prop_export_lod2Distance = IntProperty(
        name="LOD2:",
        description="From what distance this LOD should display",
        default=50,
        min=0
    )
    bpy.types.Scene.prop_export_lod3Distance = IntProperty(
        name="LOD3:",
        description="From what distance this LOD should display",
        default=150,
        min=0
    )
    
    # Materials
    bpy.types.Scene.prop_matPreset = EnumProperty(
        name='SEUT Material Preset',
        description="Select a node tree preset for your material",
        items=(
            ('SMAT_Preset_Full', 'Full', '[X] Alpha\n[X] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_Full_NoEmissive', 'No Emissive', '[X] Alpha\n[_] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_Full_NoADD', 'Full, No ADD', '[X] Alpha\n[_] Emissive\n[_] ADD\n[X] NG'),
            ('SMAT_Preset_NoAlpha', 'No Alpha', '[_] Alpha\n[X] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_NoAlpha_NoEmissive', 'No Alpha, No Emissive', '[_] Alpha\n[_] Emissive\n[X] ADD\n[X] NG'),
            ('SMAT_Preset_NoADD', 'No ADD', '[_] Alpha\n[_] Emissive\n[_] ADD\n[X] NG')
            ),
        default='SMAT_Preset_Full'
    )

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
        
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_draw)

    del bpy.types.Scene.prop_gridScale
    del bpy.types.Scene.prop_bBoxToggle
    del bpy.types.Scene.prop_bBox_X
    del bpy.types.Scene.prop_bBox_Y
    del bpy.types.Scene.prop_bBox_Z
    del bpy.types.Scene.prop_subtypeId
    del bpy.types.Scene.prop_export_deleteLooseFiles
    del bpy.types.Scene.prop_export_fbx
    del bpy.types.Scene.prop_export_xml
    del bpy.types.Scene.prop_export_hkt
    del bpy.types.Scene.prop_export_sbc
    del bpy.types.Scene.prop_export_rescaleFactor
    del bpy.types.Scene.prop_export_exportPath
    del bpy.types.Scene.prop_export_lod1Distance
    del bpy.types.Scene.prop_export_lod2Distance
    del bpy.types.Scene.prop_export_lod3Distance
    del bpy.types.Scene.prop_matPreset


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

def update_GridScale(self, context):
    bpy.ops.object.gridscale()
    bpy.ops.object.bbox('INVOKE_DEFAULT')

def update_BBox(self, context):
    bpy.ops.object.bbox('INVOKE_DEFAULT')

addon_keymaps = []

if __name__ == "__main__":
    register()

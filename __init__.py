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
    "author": "enenra, Kamikaze",
    "version": (0, 1, 0),
    "blender": (2, 81, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/enenra/space-engineers-utilities",
    "tracker_url": "https://github.com/enenra/space-engineers-utilities/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

'''
Plan:
    Import
        Import FBX

        Clean Materials: seut_remapLibraryMaterials.py

    Export: seut_export.py
        - exportAll(scene)
        - export(collection)
        - Option: Generate SG version
        - Need error handling if collections are not found.
        XML
            - Rescale factor needs to be settable
            - exportXML(collection)
            Materials
                - printMaterialReferences(object)

            LODs
                - Pull in LOD distances
                - printLODReferences(object)
                - BS LOD?

        FBX
            - exportFBX(collection)
            * Main Model
            * LODs
            * Build Stages

        BLEND
            - exportCollision(collection)
            * HKT for 2.79
    
    Mirroring ? (instances of object, rotate, separate collection)
    Icon render ? (camera alignment might be too complicated)
    Dummies - context menu to create one and link it?
    recreate collections
    toggle bounding box
        https://www.youtube.com/watch?v=EgrgEoNFNsA&list=PLboXykqtm8dw-TCdMNrxz4cEemox0jBn0&index=7&t=0s
        panel to adjust its size, toggle on / off
    link to online documentation?
'''

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

from .seut_panel                import SEUT_PT_Panel
from .seut_panel                import SEUT_PT_Panel_BoundingBox
from .seut_panel                import SEUT_PT_Panel_Export
from .seut_panel                import SEUT_PT_Panel_Import
from .seut_export               import SEUT_OT_Export
from .seut_import               import SEUT_OT_Import
from .seut_gridScale            import SEUT_OT_GridScale
from .seut_bBox                 import SEUT_OT_BBox
from .seut_recreateCollections  import SEUT_OT_RecreateCollections

def register():
    bpy.utils.register_class(SEUT_PT_Panel)
    bpy.utils.register_class(SEUT_PT_Panel_BoundingBox)
    bpy.utils.register_class(SEUT_PT_Panel_Export)
    bpy.utils.register_class(SEUT_PT_Panel_Import)
    bpy.utils.register_class(SEUT_OT_Export)
    bpy.utils.register_class(SEUT_OT_Import)
    bpy.utils.register_class(SEUT_OT_GridScale)
    bpy.utils.register_class(SEUT_OT_BBox)
    bpy.utils.register_class(SEUT_OT_RecreateCollections)

    bpy.types.Scene.prop_gridScale = bpy.props.EnumProperty(
        name='Scale',
        items=(
            ('0', 'Large', 'Large grid blocks (2.5m)'),
            ('1', 'Small', 'Small grid blocks (0.5m)')
            ),
        default='0',
        update=update_GridScale
    )

    bpy.types.Scene.prop_bBoxToggle = bpy.props.EnumProperty(
        name='Scale',
        items=(
            ('0', 'On', ''),
            ('1', 'Off', '')
            ),
        default='0',
        update=update_BBox
    )
    bpy.types.Scene.prop_bBox_X = IntProperty(
        name="X",
        description="",
        default=1,
        min=1,
        update=update_BBox
    )
    bpy.types.Scene.prop_bBox_Y = IntProperty(
        name="Y",
        description="",
        default=1,
        min=1,
        update=update_BBox
    )
    bpy.types.Scene.prop_bBox_Z = IntProperty(
        name="Z",
        description="",
        default=1,
        min=1,
        update=update_BBox
    )

    bpy.types.Scene.prop_export_fbx = BoolProperty(
        name="Export FBX",
        description="Whether to export to FBX",
        default=True
    )
    bpy.types.Scene.prop_export_xml = BoolProperty(
        name="Export XML",
        description="Whether to export to XML",
        default=True
    )
    bpy.types.Scene.prop_export_rescaleFactor = FloatProperty(
        name="Rescale Factor",
        description="What to set the Rescale Factor to",
        default=1,
        min=0
    )
    bpy.types.Scene.prop_export_lod1Distance = IntProperty(
        name="LOD1",
        description="From what distance this LOD should display",
        default=25,
        min=0
    )
    bpy.types.Scene.prop_export_lod2Distance = IntProperty(
        name="LOD2",
        description="From what distance this LOD should display",
        default=50,
        min=0
    )
    bpy.types.Scene.prop_export_lod3Distance = IntProperty(
        name="LOD3",
        description="From what distance this LOD should display",
        default=150,
        min=0
    )

def unregister():
    bpy.utils.unregister_class(SEUT_PT_Panel)
    bpy.utils.unregister_class(SEUT_PT_Panel_BoundingBox)
    bpy.utils.unregister_class(SEUT_PT_Panel_Export)
    bpy.utils.unregister_class(SEUT_PT_Panel_Import)
    bpy.utils.unregister_class(SEUT_OT_Export)
    bpy.utils.unregister_class(SEUT_OT_Import)
    bpy.utils.unregister_class(SEUT_OT_GridScale)
    bpy.utils.unregister_class(SEUT_OT_BBox)
    bpy.utils.unregister_class(SEUT_OT_RecreateCollections)

    del bpy.types.Scene.prop_gridScale
    del bpy.types.Scene.prop_bBoxToggle
    del bpy.types.Scene.prop_bBox_X
    del bpy.types.Scene.prop_bBox_Y
    del bpy.types.Scene.prop_bBox_Z
    del bpy.types.Scene.prop_export_fbx
    del bpy.types.Scene.prop_export_xml
    del bpy.types.Scene.prop_export_rescaleFactor
    del bpy.types.Scene.prop_export_lod1Distance
    del bpy.types.Scene.prop_export_lod2Distance
    del bpy.types.Scene.prop_export_lod3Distance


def menu_func(self, context):
    self.layout.operator(SEUT_OT_Export.bl_idname)
    self.layout.operator(SEUT_OT_Import.bl_idname)
    self.layout.operator(SEUT_OT_GridScale.bl_idname)
    self.layout.operator(SEUT_OT_BBox.bl_idname)
    self.layout.operator(SEUT_OT_RecreateCollections.bl_idname)

def update_GridScale(self, context):
    SEUT_OT_GridScale.execute(self, context)

def update_BBox(self, context):
    SEUT_OT_BBox.execute(self, context)

addon_keymaps = []

if __name__ == "__main__":
    register()

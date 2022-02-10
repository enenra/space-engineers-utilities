import bpy

from bpy.types  import Panel
from bpy.types  import PropertyGroup
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty,
                        CollectionProperty
                        )
                        
from bpy_extras.asset_utils import SpaceAssetInfo


def update_vanilla_dlc(self, context):
    if self.is_dlc and not self.is_vanilla:
        self.is_vanilla = True
    
    elif not self.is_vanilla and self.is_dlc:
        self.is_dlc = False


class SEUT_Asset(PropertyGroup):
    """Holder for the various asset properties"""

    is_dlc: BoolProperty(
        name='DLC',
        description="This asset contains geometry, materials or textures only used in DLC",
        default=False,
        update=update_vanilla_dlc
    )
    is_vanilla: BoolProperty(
        name='Vanilla',
        description="This asset contains no custom textures",
        default=False,
        update=update_vanilla_dlc
    )
    

class SEUT_PT_Panel_Asset(Panel):
    """Creates the asset panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Asset"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = 'TOOL_PROPS'
    bl_context = 'asset'


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return 'SEUT' in scene.view_layers and SpaceAssetInfo.is_asset_browser_poll(context) and SpaceAssetInfo.get_active_asset(context) is not None


    def draw(self, context):
        layout = self.layout
        asset = SpaceAssetInfo.get_active_asset(context)
        
        box = layout.box()
        box.label(text="Asset Properties", icon='PROPERTIES')
        row = box.row(align=True)
        row.prop(asset.seut, 'is_vanilla', icon='DOT')
        row.prop(asset.seut, 'is_dlc', icon='ADD')
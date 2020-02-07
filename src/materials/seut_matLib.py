import bpy
import os

from bpy.types  import PropertyGroup, UIList
from bpy.props  import (EnumProperty,
                        FloatProperty,
                        FloatVectorProperty,
                        IntProperty,
                        StringProperty,
                        BoolProperty,
                        PointerProperty)

def update_enabled(self, context):
    wm = context.window_manager

    addon = __package__[:__package__.find(".")]
    preferences = bpy.context.preferences.addons.get(addon).preferences
    materialsPath = os.path.normpath(bpy.path.abspath(preferences.materialsPath))

    if preferences.materialsPath == "" or preferences.materialsPath == "." or os.path.exists(materialsPath) == False:
        print("SEUT Info: Path to Materials Folder (Addon Preferences) '" + materialsPath + "' not valid. (017)")
        return

    # Read MatLib materials.
    for lib in wm.matlibs:
        with bpy.data.libraries.load(materialsPath + "\\" + lib.name, link=True) as (data_from, data_to):

            # If the lib is disabled, unlink its materials from the current file.
            if not lib.enabled:
                for mat in data_from.materials:
                    if mat in bpy.data.materials:
                        bpy.data.materials.remove(bpy.data.materials[mat], do_unlink=True)
                for img in data_from.images:
                    if img in bpy.data.images:
                        bpy.data.images.remove(bpy.data.images[img], do_unlink=True)
                for ngroup in data_from.node_groups:
                    if ngroup in bpy.data.node_groups:
                        bpy.data.node_groups.remove(bpy.data.node_groups[ngroup], do_unlink=True)

    # Read MatLib materials.
    for lib in wm.matlibs:
        with bpy.data.libraries.load(materialsPath + "\\" + lib.name, link=True) as (data_from, data_to):

            # If the lib is enabled, link them to the current file.
            if lib.enabled:
                data_to.materials = data_from.materials



class SEUT_MatLibProps(PropertyGroup):
    """Holder for the various MatLib properties"""

    name: StringProperty(
        name="Name of MatLib"
    )
    enabled: BoolProperty(
        name="Enable or Disable MatLibs in the Materials folder",
        default=False,
        update=update_enabled
    )


class SEUT_UL_MatLib(UIList):
    """Creates the MatLib UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.9)
        if item.enabled:
            split.label(text=item.name, icon='LINKED')
        else:
            split.label(text=item.name, icon='UNLINKED')
        split.prop(item, "enabled", text="", index=index)

    def invoke(self, context, event):
        pass 
import bpy
import os

from bpy.types  import UIList


class SEUT_UL_MatLib(UIList):
    """Creates the MatLib UI list"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.split(factor=0.9)
        if item.enabled:
            split.label(text=item.name[:-6], icon='LINKED')
        else:
            split.label(text=item.name[:-6], icon='UNLINKED')
        split.prop(item, "enabled", text="", index=index)

    def invoke(self, context, event):
        pass 
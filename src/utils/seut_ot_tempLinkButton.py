import bpy
import webbrowser

from bpy.types      import Operator
from bpy.props      import StringProperty

class SEUT_OT_TempLinkButton(Operator):
    bl_idname = 'wm.link_button'
    bl_label = "Link Button"
    bl_description = "A button that opens a link in the browser"

    def execute(self, context):

        wm = context.window_manager

        if not wm.seut.temp_link:
            return {'CANCELLED'}

        else:
            webbrowser.open(wm.seut.temp_link)
            return {'FINISHED'}
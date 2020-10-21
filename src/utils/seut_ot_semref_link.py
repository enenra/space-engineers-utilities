import bpy
import webbrowser

from bpy.types              import Operator
from bpy.props              import StringProperty


class SEUT_OT_SEMREFLink(Operator):
    """Opens the relevant Space Engineers Modding Reference page, containing more usage information and / or tutorials"""
    bl_idname = "wm.semref_link"
    bl_label = "SEMREF Link"
    bl_options = {'REGISTER', 'UNDO'}

    section: StringProperty()

    page: StringProperty()


    def execute(self, context):

        wm = context.window_manager

        webbrowser.open("https://space-engineers-modding.github.io/modding-reference/" + self.section + "/tools/3d-modelling/seut/" + self.page + ".html")
        
        return {'FINISHED'}
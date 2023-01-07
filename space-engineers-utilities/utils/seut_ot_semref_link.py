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

    code: StringProperty()


    def execute(self, context):
        
        webbrowser.open("https://semref.atlassian.net/wiki/spaces/" + self.section + "/pages/" + self.page + self.code)
        
        return {'FINISHED'}
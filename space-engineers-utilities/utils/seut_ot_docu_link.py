import bpy
import webbrowser

from bpy.types              import Operator
from bpy.props              import StringProperty


class SEUT_OT_DocuLink(Operator):
    """Opens the relevant Space Engineers Wiki page, containing more usage information and / or tutorials"""
    bl_idname = "wm.docu_link"
    bl_label = "Documentation Link"
    bl_options = {'REGISTER', 'UNDO'}

    section: StringProperty()

    page: StringProperty()

    code: StringProperty()


    def execute(self, context):
        
        webbrowser.open("https://spaceengineers.wiki.gg/wiki/Modding/" + self.section + self.page + self.code)
        
        return {'FINISHED'}
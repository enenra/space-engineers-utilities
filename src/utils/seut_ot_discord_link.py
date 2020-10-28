import bpy
import webbrowser

from bpy.types              import Operator
from bpy.props              import StringProperty


class SEUT_OT_DiscordLink(Operator):
    """Link to the official SEUT / AQD Discord server"""
    bl_idname = "wm.discord_link"
    bl_label = "SEUT Discord"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        wm = context.window_manager

        webbrowser.open("https://discord.gg/QtyCsBr")
        
        return {'FINISHED'}
import bpy
import xml.etree.ElementTree as ET
import xml.dom.minidom

class SEUT_OT_Export(bpy.types.Operator):
    """Exports shit."""
    bl_idname = "object.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Debug
        print('OT: Export')

        return {'FINISHED'}

    def exportXML(self, collection):

        # a

        return

    def exportFBX(self, collection):

        # a

        return

    def exportCollision(self, collection):

        # a

        return

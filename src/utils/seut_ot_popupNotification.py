import bpy

from bpy.types      import Operator
from bpy.props      import StringProperty, BoolProperty

class SEUT_OT_PopupNotification(Operator):
    bl_idname = 'message.popup_message'
    bl_label = "Popup Message"
    bl_description = "Displays a popup message"

    works: BoolProperty(
        name="Whether this works with self.report",
        default=True
    )
    
    p_type: StringProperty(
        name="The message type"
        )
    
    p_text: StringProperty(
        name="The message to be displayed"
        )
    
    p_link: StringProperty(
        name="The SEMREF link"
        )

    def execute(self, context):

        wm = context.window_manager

        if self.p_link != '':
            wm.seut.temp_link = self.p_link
            self.displaySEMREFLink(context, self.p_text)

        #try:
        #    self.report({self.p_type}, self.p_text)
        #except RuntimeError:
        #    pass

        return {'FINISHED'}
 
#    def invoke(self, context, event):
#        return self.execute(context)

    def displaySEMREFLink(self, context, text):
        def draw(self, context):
            self.layout.label(text=text)
            self.layout.label()
            self.layout.label()
            self.layout.operator('wm.link_button', icon='PROPERTIES', text="SEMREF")

        bpy.context.window_manager.popup_menu(draw, title="", icon='NONE')
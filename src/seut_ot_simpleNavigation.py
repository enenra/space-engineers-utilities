import bpy

from bpy.types import Operator

from .seut_utils    import linkSubpartScene

class SEUT_OT_SimpleNavigation(Operator):
    """Makes navigation through SEUT collections simpler by hiding all non-active collections"""
    bl_idname = "scene.simple_navigation"
    bl_label = "Simple Navigation"
    bl_options = {'REGISTER', 'UNDO'}


    def invoke(self, context, event):

        scene = context.scene
        wm = context.window_manager

        if not wm.seut.simpleNavigationToggle:
            return {'FINISHED'}


        return {'RUNNING_MODAL'}

    
    def modal(self, context, event):

        scene = context.scene
        wm = context.window_manager
        layer_collection = context.view_layer.active_layer_collection

        if not wm.seut.simpleNavigationToggle:
            return {'FINISHED'}

        if not layer_collection.show:
            layer_collection.show = True
            for lay_col in context.view_layer.layer_collection.children:
                


        return {'PASS_THROUGH'}
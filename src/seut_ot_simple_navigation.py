import bpy

from bpy.types import Operator

from .seut_collections              import get_collections
from .seut_errors                   import seut_report


class SEUT_OT_SimpleNavigation(Operator):
    """Makes navigation through SEUT collections simpler by hiding all non-active collections"""
    bl_idname = "scene.simple_navigation"
    bl_label = "Simple Navigation"
    bl_options = {'REGISTER', 'UNDO'}


    def invoke(self, context, event):

        scene = context.scene
        wm = context.window_manager
        collections = get_collections(scene)

        if not wm.seut.simpleNavigationToggle:
            for col in collections.values():
                if col is not None:
                    col.hide_viewport = False
            return {'FINISHED'}

        check = False
        for col in collections.values():
            if col is not None:
                check = True

        if not check:
            seut_report(self, context, 'ERROR', False, 'E010')
            wm.seut.simpleNavigationToggle = False
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    
    def modal(self, context, event):

        scene = context.scene
        wm = context.window_manager
        collections = get_collections(scene)
        collection = context.view_layer.active_layer_collection.collection

        if not wm.seut.simpleNavigationToggle:
            for col in collections.values():
                if col is not None:
                    col.hide_viewport = False
            return {'FINISHED'}

        if collection.hide_viewport:
            collection.hide_viewport = False

        if collection not in collections.values():
            return {'PASS_THROUGH'}
        
        for col in collections.values():
            if col is not None:
                if col == collections['seut'] or col == collection:
                    continue
                else:
                    col.hide_viewport = True

        return {'PASS_THROUGH'}


    def finish(self):
        self.unregister_handlers(context)
        return {'FINISHED'}
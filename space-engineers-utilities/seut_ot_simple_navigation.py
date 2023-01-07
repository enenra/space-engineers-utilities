import bpy

from bpy.types import Operator

from .seut_collections              import get_collections
from .seut_errors                   import seut_report
from .seut_utils                    import get_seut_blend_data


class SEUT_OT_SimpleNavigation(Operator):
    """Makes navigation through SEUT collections simpler by hiding all non-active collections"""
    bl_idname = "wm.simple_navigation"
    bl_label = "Simple Navigation"
    bl_options = {'REGISTER', 'UNDO'}


    def invoke(self, context, event):

        scene = context.scene
        data = get_seut_blend_data()
        collections = get_collections(scene)

        if not data.seut.simpleNavigationToggle:
            return {'FINISHED'}

        if not data.seut.simpleNavigationToggle:
            for col in bpy.data.collections:
                if col is not None and col.seut.scene is scene:
                    if col.seut.col_type == 'seut':
                        continue
                    else:
                        context.view_layer.layer_collection.children[collections['seut'][0].name].children[col.name].hide_viewport = False
            return {'FINISHED'}

        check = False
        for col in bpy.data.collections:
            if col is not None and col.seut.scene is scene:
                check = True

        if not check:
            seut_report(self, context, 'ERROR', False, 'E010')
            data.seut.simpleNavigationToggle = False
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    
    def modal(self, context, event):

        scene = context.scene
        data = get_seut_blend_data()
        collections = get_collections(scene)
        active_col = context.view_layer.active_layer_collection

        if not data.seut.simpleNavigationToggle:
            return {'FINISHED'}

        if active_col.hide_viewport:
            active_col.hide_viewport = False

        if active_col.collection.seut.col_type == 'none':
            return {'PASS_THROUGH'}
        
        for col in bpy.data.collections:
            if col is not None and col.seut.scene is scene:
                if col.seut.col_type in ['seut', 'render', 'mountpoints', 'mirroring'] or col == active_col.collection:
                    continue
                else:
                    context.view_layer.layer_collection.children[collections['seut'][0].name].children[col.name].hide_viewport = True

        return {'PASS_THROUGH'}


    def finish(self):
        self.unregister_handlers(bpy.context)
        return {'FINISHED'}
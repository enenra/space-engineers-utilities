import bpy
import os

from bpy.types      import Operator

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections


class SEUT_OT_IconRenderPreview(Operator):
    """Shows a render preview window"""
    bl_idname = "scene.icon_render_preview"
    bl_label = "Render"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.scene.seut.renderToggle == 'on'


    def execute(self, context):

        scene = context.scene
        wm = context.window_manager

        if context.object is not None and context.object.mode is not 'OBJECT':
            currentMode = context.object.mode
            bpy.ops.object.mode_set(mode='OBJECT')

        simpleNav = wm.seut.simpleNavigationToggle
        wm.seut.simpleNavigationToggle = False

        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        for col in collections.values():
            if col is not None:
                col.hide_viewport = True

        # This path juggling is to prevent Blender from saving the default render output
        path = scene.render.filepath
        scene.render.filepath = '/tmp\\'

        bpy.ops.render.render()
        bpy.ops.render.view_show('INVOKE_DEFAULT')
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        image = area.spaces.active.image
        area.spaces.active.image = bpy.data.images['Viewer Node']

        scene.render.filepath = path
        bpy.data.images['Viewer Node'].save_render(scene.render.filepath + scene.seut.subtypeId + '.' + scene.render.image_settings.file_format.lower())
        
        for col in collections.values():
            if col is not None:
                col.hide_viewport = False

        wm.seut.simpleNavigationToggle = simpleNav

        try:
            if bpy.context.object is not None and currentMode is not None:
                bpy.ops.object.mode_set(mode=currentMode)
        except:
            pass

        return {'FINISHED'}
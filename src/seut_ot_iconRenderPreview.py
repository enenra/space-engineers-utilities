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
            
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        if context.object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
            context.object.select_set(False)
            context.view_layer.objects.active = None

        simpleNav = wm.seut.simpleNavigationToggle
        wm.seut.simpleNavigationToggle = False

        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        for col in collections.values():
            if col is not None:
                if col.name == 'Main' + tag:
                    for obj in col.objects:
                        obj.hide_render = False
                        obj.hide_viewport = False
                else:
                    for obj in col.objects:
                        obj.hide_render = True
                        obj.hide_viewport = True

        # This path juggling is to prevent Blender from saving the default render output
        path = scene.render.filepath
        scene.render.filepath = '/tmp\\'

        bpy.ops.render.render()
        bpy.ops.render.view_show('INVOKE_DEFAULT')
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        image = area.spaces.active.image
        area.spaces.active.image = bpy.data.images['Viewer Node']

        scene.render.filepath = os.path.abspath(bpy.path.abspath(path))
        bpy.data.images['Viewer Node'].save_render(scene.render.filepath + "\\" + scene.seut.subtypeId + '.' + scene.render.image_settings.file_format.lower())
        
        for col in collections.values():
            if col is not None:
                for obj in col.objects:
                    obj.hide_render = False
                    obj.hide_viewport = False

        wm.seut.simpleNavigationToggle = simpleNav

        self.report({'INFO'}, "SEUT: Icon successfully saved to '%s'." % (scene.render.filepath + "\\" + scene.seut.subtypeId + '.' + scene.render.image_settings.file_format.lower()))

        return {'FINISHED'}
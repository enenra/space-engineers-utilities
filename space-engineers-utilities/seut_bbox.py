import bpy
import gpu
import math

from bgl                import *
from gpu_extras.batch   import batch_for_shader
from bpy.types          import Operator

from .seut_collections              import get_collections
from .seut_errors                   import seut_report


# Most of the code used in this class is **heavily** based on Jayanam's "Blender 2.8 Python GPU : Draw Lines"-video:
# https://www.youtube.com/watch?v=EgrgEoNFNsA
class SEUT_OT_BBox(Operator):
    """Sets the bounding box"""
    bl_idname = "object.bbox"
    bl_label = "Bounding Box"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.draw_handle = None
        self.draw_event = None

    def invoke(self, context, event):

        scene = context.scene
        wm = context.window_manager

        # If the toggle is off, don't do anything.
        if wm.seut.bBoxToggle == 'off':
            return {'FINISHED'}

        factor = 1

        if scene.seut.gridScale == 'large': factor = 2.5
        if scene.seut.gridScale == 'small': factor = 0.5

        x = scene.seut.bBox_X * factor
        y = scene.seut.bBox_Y * factor
        z = scene.seut.bBox_Z * factor

        self.coords = (
            (-x/2, -y/2, -z/2), (+x/2, -y/2, -z/2),
            (-x/2, +y/2, -z/2), (+x/2, +y/2, -z/2),
            (-x/2, -y/2, +z/2), (+x/2, -y/2, +z/2),
            (-x/2, +y/2, +z/2), (+x/2, +y/2, +z/2)
        )

        self.indices = (
            (0, 1), (0, 2), (1, 3), (2, 3),
            (4, 5), (4, 6), (5, 7), (6, 7),
            (0, 4), (1, 5), (2, 6), (3, 7)
        )

        self.create_batch()

        args = (self, context)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_3d, args, "WINDOW", "POST_VIEW"
        )

        self.draw_event = context.window_manager.event_timer_add(1, window=context.window)

    def unregister_handlers(self, context):

        context.window_manager.event_timer_remove(self.draw_event)

        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")

        self.draw_handle = None
        self.draw_event = None

    def modal(self, context, event):
        scene = context.scene
        wm = context.window_manager

        if context.area:
            context.area.tag_redraw()

        # Escape condition for when the user turns off the bounding box.
        if wm.seut.bBoxToggle == 'off':
            self.unregister_handlers(context)
            return {'FINISHED'}

        factor = 1

        if scene.seut.gridScale == 'large': factor = 2.5
        if scene.seut.gridScale == 'small': factor = 0.5

        x = scene.seut.bBox_X * factor
        y = scene.seut.bBox_Y * factor
        z = scene.seut.bBox_Z * factor

        if not scene.seut.sceneType == 'mainScene':
            x = 0
            y = 0
            z = 0

        self.coords = (
            (-x/2, -y/2, -z/2), (+x/2, -y/2, -z/2),
            (-x/2, +y/2, -z/2), (+x/2, +y/2, -z/2),
            (-x/2, -y/2, +z/2), (+x/2, -y/2, +z/2),
            (-x/2, +y/2, +z/2), (+x/2, +y/2, +z/2)
        )

        self.create_batch()
        
        return {'PASS_THROUGH'}

    def finish(self):
        self.unregister_handlers(context)
        return {'FINISHED'}

    def create_batch(self):

        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.batch = batch_for_shader(self.shader, 'LINES', {"pos": self.coords}, indices=self.indices)

    def draw_callback_3d(self, op, context):
        wm = context.window_manager
        
        try:
            transparency = round((wm.seut.bboxTransparency / 10), 2)
            glEnable(GL_BLEND)
            self.shader.bind()
            self.shader.uniform_float("color", (wm.seut.bboxColor[0], wm.seut.bboxColor[1], wm.seut.bboxColor[2], 0.5))
            self.batch.draw(self.shader)
            glDisable(GL_BLEND)
        except:
            return


class SEUT_OT_BBoxAuto(Operator):
    """Sets the bounding box automatically (not very accurate)"""
    bl_idname = "object.bbox_auto"
    bl_label = "Automatic"
    bl_options = {'REGISTER', 'UNDO'}

    
    # Button is unavailable when bounding box is turned off.
    @classmethod
    def poll(cls, context):
        return context.window_manager.seut.bBoxToggle == 'on'

    
    # This is what is executed if "Automatic" is pressed.
    def execute(self, context):

        scene = context.scene
        collections = get_collections(scene)

        if collections['main'] == None or len(collections['main'].objects) == 0:
            seut_report(self, context, 'ERROR', True, 'E002', "'Main'")
            return {'CANCELLED'}

        dimension_x = 0
        dimension_y = 0
        dimension_z = 0

        # this currently does not take the object's children's dimensions into account 
        for obj in collections['main'].all_objects:
            if obj.location.x + obj.dimensions.x > dimension_x:
                dimension_x = obj.location.x + obj.dimensions.x
            if obj.location.y + obj.dimensions.y > dimension_y:
                dimension_y = obj.location.y + obj.dimensions.y
            if obj.location.z + obj.dimensions.z > dimension_z:
                dimension_z = obj.location.z + obj.dimensions.z
        
        factor = 1

        if scene.seut.gridScale == 'large': factor = 2.5
        if scene.seut.gridScale == 'small': factor = 0.5

        # This should technically be math.ceil(D / factor) * factor but when drawing the bounding box it's already being multiplied by the factor.
        size_x = math.ceil(dimension_x / factor)
        size_y = math.ceil(dimension_y / factor)
        size_z = math.ceil(dimension_z / factor)
        
        scene.seut.bBox_X = size_x
        scene.seut.bBox_Y = size_y
        scene.seut.bBox_Z = size_z

        bpy.ops.object.bbox('INVOKE_DEFAULT')

        seut_report(self, context, 'INFO', True, 'I015', dimension_x, dimension_y, dimension_z)
        
        return {'FINISHED'}
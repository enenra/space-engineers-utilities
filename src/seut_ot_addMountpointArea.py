import bpy

from bpy.types      import Operator

from .seut_ot_mountpoints   import SEUT_OT_Mountpoints

class SEUT_OT_AddMountpointArea(Operator):
    """Adds an area to a mountpoint side"""
    bl_idname = "scene.add_mountpoint_area"
    bl_label = "Add Area"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.scene.seut.mountpointToggle == 'on'


    def execute(self, context):

        scene = context.scene
        wm = context.window_manager

        mpMat = None
        for mat in bpy.data.materials:
            if mat.name == 'SMAT_Mountpoint':
                mpMat = mat
        
        if mpMat is None:
            self.report({'ERROR'}, "SEUT: Cannot find mountpoint material. Re-link 'MatLib_Presets.blend'! (027)")
            return {'CANCELLED'}

        side = wm.seut.mountpointSide

        if scene.seut.gridScale == 'small':
            scale = 0.5
        else:
            scale = 2.5

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        collection = bpy.data.collections['Mountpoints' + tag]

        if side == 'front' or side == 'back':
            x = scene.seut.bBox_X
            y = scene.seut.bBox_Z
        elif side == 'left' or side == 'right':
            x = scene.seut.bBox_Y
            y = scene.seut.bBox_Z
        elif side == 'top' or side == 'bottom':
            x = scene.seut.bBox_X
            y = scene.seut.bBox_Y

        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint Area ' + side.capitalize(), 1, scale, scale, None, None, collection, bpy.data.objects['Mountpoints ' + side.capitalize()])
        area.active_material = mpMat

        return {'FINISHED'}
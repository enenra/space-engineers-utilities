import bpy

from bpy.types          import Operator


class SEUT_OT_SetGridScale(Operator):
    """Sets the grid scale"""

    bl_idname = "wm.set_grid_scale"
    bl_label = "Set Grid Scale"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        # Grid scale is SE block size divided by 2 because else the lines don't line up with the block edges.
        if scene.seut.gridScale == 'small':
            scale = 0.25
        else:
            scale = 1.25

        # It needs to be set for all viewports in all workspaces.
        for workspace in bpy.data.workspaces:
            for screen in workspace.screens:
                for area in screen.areas:
                    if not area.type == 'VIEW_3D':
                        continue

                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.overlay.grid_scale = scale
                            break
        
        return {'FINISHED'}
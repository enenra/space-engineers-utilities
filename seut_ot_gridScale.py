import bpy

class SEUT_OT_GridScale(bpy.types.Operator):
    """Sets the grid scale."""
    bl_idname = "object.gridscale"
    bl_label = "Grid Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Grid scale is SE block size divided by 2 because else the lines don't line up with the block edges.
        if context.scene.prop_gridScale == '0':
            scale = 1.25
        elif context.scene.prop_gridScale == '1':
            scale = 0.25

        # It needs to be set for all viewports in all workspaces.
        for workspace in bpy.data.workspaces:
            for screen in workspace.screens:
                for area in screen.areas:
                    if not area.type == 'VIEW_3D':
                        continue

                    for s in area.spaces:
                        if s.type == 'VIEW_3D':
                            s.overlay.grid_scale = scale
                            break
        
        print("SEUT Info: Grid Scale adjusted to: " + str(scale))

        return {'FINISHED'}
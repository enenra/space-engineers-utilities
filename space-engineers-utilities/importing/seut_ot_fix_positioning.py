import bpy

from bpy.types      import Operator

from ..seut_errors  import seut_report



class SEUT_OT_FixPositioningPre(Operator):
    # used as tooltip by blender:
    """Applies rotation and scale transforms to ALL non-empty objects connected to the selected object."""
    bl_idname = "object.fix_pre"
    bl_label = "Apply Scale&Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):
        obj = context.window.view_layer.objects.active
        
        def select_recursive(parent):
            if parent.type != 'EMPTY':
                parent.select_set(True)
                
            for child in parent.children:
                select_recursive(child)
                
        obj = context.window.view_layer.objects.active
        obj.select_set(True)
        
        # find top-most parent
        while obj.parent != None:
            obj = obj.parent
            
        select_recursive(obj)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=False, isolate_users=False)
        
        return {'FINISHED'}



class SEUT_OT_FixPositioning(Operator):
    # used as tooltip by blender:
    """Attempts to fix positioning on the selected object's direct children - see guide for proper usage!"""
    bl_idname = "object.fix_positioning"
    bl_label = "Attempt fix positioning"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):
        obj = context.window.view_layer.objects.active
        
        # select child way - can be more confusing because floating parts might have an intermediary parent
        #if obj.parent == None:
        #    return {'CANCELLED'} # TODO: tell user they need to select one of the broken parts
        #obj = obj.parent
        
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=False, isolate_users=False)
        
        for child in obj.children:
            child.location -= obj.location
            child.select_set(True) # for user to see what was affected
        
        seut_report(self, context, 'INFO', True, 'I013')
        
        return {'FINISHED'}



class SEUT_OT_FixPositioningPost(Operator):
    # used as tooltip by blender:
    """After done fixing everything, use this to apply location transforms on ALL non-empty objects connected to the selected object. Not required but makes the 3D view clean of scatterd lines and dots from object pivots."""
    bl_idname = "object.fix_post"
    bl_label = "Apply location"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):
        obj = context.window.view_layer.objects.active
        
        def select_recursive(parent):
            if parent.type != 'EMPTY':
                parent.select_set(True)
                
            for child in parent.children:
                select_recursive(child)
                
        obj = context.window.view_layer.objects.active
        obj.select_set(True)
        
        # find top-most parent
        while obj.parent != None:
            obj = obj.parent
            
        select_recursive(obj)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False, properties=False, isolate_users=False)
        
        return {'FINISHED'}
import bpy

from bpy.types      import Operator

from ..seut_errors  import seut_report


class SEUT_OT_FixPositioningPre(Operator):
    """Applies rotation and scale transforms to all non-empty objects connected to the selected object"""
    bl_idname = "object.apply_scale_rotation"
    bl_label = "Apply Scale & Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):
        
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
    """Attempts to fix positioning on the selected object's direct children"""
    bl_idname = "object.fix_positioning"
    bl_label = "Fix Positioning"
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
        
        return {'FINISHED'}


class SEUT_OT_FixPositioningPost(Operator):
    """After using the other options, use this to apply location on all non-empty objects connected to the selected object"""
    bl_idname = "object.apply_location"
    bl_label = "Apply Location"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1


    def execute(self, context):
        
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
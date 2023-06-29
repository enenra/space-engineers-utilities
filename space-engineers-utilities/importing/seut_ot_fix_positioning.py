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
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'


    def execute(self, context):
                
        selected_objects = list(context.selected_objects)
        for obj in context.selected_objects:
            obj.select_set(False)

        for obj in selected_objects:
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
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'


    def execute(self, context):
                
        selected_objects = set(context.selected_objects)
        for obj in context.selected_objects:
            obj.select_set(False)
        
        affected = []

        for obj in selected_objects:
            obj = context.window.view_layer.objects.active
            obj.select_set(True)

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=False, isolate_users=False)
            
            for child in obj.children:
                child.location -= obj.location
                affected.append(child)
            
            
        for obj in context.selected_objects:
            obj.select_set(False)

        # To show which objects were affected
        for obj in affected:
            obj.select_set(True)
        
        return {'FINISHED'}


class SEUT_OT_FixPositioningPost(Operator):
    """After using the other options, use this to apply location on all non-empty objects connected to the selected object"""
    bl_idname = "object.apply_location"
    bl_label = "Apply Location"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'


    def execute(self, context):
                
        selected_objects = set(context.selected_objects)
        for obj in context.selected_objects:
            obj.select_set(False)

        for obj in selected_objects:
            obj = context.window.view_layer.objects.active
            obj.select_set(True)
        
            # find top-most parent
            while obj.parent != None:
                obj = obj.parent
                
            select_recursive(obj)

        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False, properties=False, isolate_users=False)
        
        return {'FINISHED'}
    

def select_recursive(parent):
    if parent.type != 'EMPTY':
        parent.select_set(True)
        
    for child in parent.children:
        select_recursive(child)
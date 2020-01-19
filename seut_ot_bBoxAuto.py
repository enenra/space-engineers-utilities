import bpy
import math

from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections

class SEUT_OT_BBoxAuto(Operator):
    """Sets the bounding box automatically"""
    bl_idname = "object.bbox_auto"
    bl_label = "Bounding Box Automatic"
    bl_options = {'REGISTER', 'UNDO'}

    
    # Button is unavailable when bounding box is turned off.
    @classmethod
    def poll(cls, context):
        return context.scene.prop_bBoxToggle == 'on'

    
    # This is what is executed if "Automatic" is pressed.
    def execute(self, context):

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()

        if scene.prop_bBoxToggle == 'off':
            self.report({'INFO'}, "SEUT: Triggered auto BBox even though BBox is turned off. This should never happen.")
            return {'CANCELLED'}

        if collections['main'] == None or len(collections['main'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Main' not found or empty. Not possible to set automatic bounding box. (010)")
            return {'CANCELLED'}

        xD = 0
        yD = 0
        zD = 0

        # 
        for obj in collections['main'].objects:
            if obj.dimensions.x > xD:
                xD = obj.dimensions.x
            if obj.dimensions.y > yD:
                yD = obj.dimensions.y
            if obj.dimensions.z > zD:
                zD = obj.dimensions.z
        
        factor = 1

        if scene.prop_gridScale == 'large': factor = 2.5
        if scene.prop_gridScale == 'small': factor = 0.5

        # This should technically be math.ceil(D / factor) * factor but when drawing the bounding box it's already being multiplied by the factor.
        xSize = math.ceil(xD / factor)
        ySize = math.ceil(yD / factor)
        zSize = math.ceil(zD / factor)
        
        scene.prop_bBox_X = xSize
        scene.prop_bBox_Y = ySize
        scene.prop_bBox_Z = zSize

        bpy.ops.object.bbox('INVOKE_DEFAULT')

        self.report({'INFO'}, "SEUT: Bounding Box set for dimensions X: %f Y: %f Z: %f in 'Main' collection." % (xD, yD, zD))

        return {'FINISHED'}
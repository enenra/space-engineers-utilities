import bpy
import math

from bpy.types                      import Operator
from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections

class SEUT_OT_BBoxAuto(Operator):
    """Sets the bounding box automatically (not very accurate)"""
    bl_idname = "object.bbox_auto"
    bl_label = "Bounding Box Automatic"
    bl_options = {'REGISTER', 'UNDO'}

    
    # Button is unavailable when bounding box is turned off.
    @classmethod
    def poll(cls, context):
        return context.window_manager.seut.bBoxToggle == 'on'

    
    # This is what is executed if "Automatic" is pressed.
    def execute(self, context):

        scene = context.scene
        wm = context.window_manager
        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        if wm.seut.bBoxToggle == 'off':
            self.report({'INFO'}, "SEUT: Triggered auto BBox even though BBox is turned off. This should never happen.")
            
            return {'CANCELLED'}

        if collections['main'] == None or len(collections['main'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Main' not found or empty. Not possible to set automatic bounding box. (010)")
            
            return {'CANCELLED'}

        xD = 0
        yD = 0
        zD = 0

        # this currently does not take the object's children's dimensions into account 
        for obj in collections['main'].all_objects:
            if obj.location.x + obj.dimensions.x > xD:
                xD = obj.location.x + obj.dimensions.x
            if obj.location.y + obj.dimensions.y > yD:
                yD = obj.location.y + obj.dimensions.y
            if obj.location.z + obj.dimensions.z > zD:
                zD = obj.location.z + obj.dimensions.z
        
        factor = 1

        if scene.seut.gridScale == 'large': factor = 2.5
        if scene.seut.gridScale == 'small': factor = 0.5

        # This should technically be math.ceil(D / factor) * factor but when drawing the bounding box it's already being multiplied by the factor.
        xSize = math.ceil(xD / factor)
        ySize = math.ceil(yD / factor)
        zSize = math.ceil(zD / factor)
        
        scene.seut.bBox_X = xSize
        scene.seut.bBox_Y = ySize
        scene.seut.bBox_Z = zSize

        bpy.ops.object.bbox('INVOKE_DEFAULT')

        self.report({'INFO'}, "SEUT: Bounding Box set for dimensions X: %f Y: %f Z: %f in 'Main' collection." % (xD, yD, zD))
        
        return {'FINISHED'}
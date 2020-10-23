import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)

from ..seut_errors  import seut_report


class SEUT_OT_MatCreate(Operator):
    """Create a SEUT material from the defined preset"""
    bl_idname = "object.create_material"
    bl_label = "Create Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    def execute(self, context):
        
        wm = context.window_manager
        scene = context.scene

        preset_name = wm.seut.matPreset
        
        # Find SMAT to pull preset from.
        preset_material = None

        for mat in bpy.data.materials:
            if mat.name == preset_name:
                preset_material = mat
        
        if preset_material is None:
            seut_report(self, context, 'ERROR', True, 'E016', preset_name)
            return {'CANCELLED'}
            
        new_material = preset_material.copy()
        new_material.name = "SEUT Material"

        context.active_object.active_material = new_material

        if new_material.node_tree is None:
            seut_report(self, context, 'ERROR', True, 'E016', preset_name)
            return {'CANCELLED'}
            
        else:
            new_material.node_tree.make_local()
        
            for node in new_material.node_tree.nodes:
                if node is not None and node.name == "SEUT_MAT" and node.node_tree is not None:
                    node.node_tree.make_local()

        return {'FINISHED'}
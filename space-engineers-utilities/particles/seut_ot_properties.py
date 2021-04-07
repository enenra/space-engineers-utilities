import bpy

from bpy.types  import Operator
from bpy.props  import (EnumProperty,
                        IntProperty)


class SEUT_OT_PropertiesAdd(Operator):
    """Add a SEUT Particle Generation Property to a ParticleSetting"""
    bl_idname = "particle.properties_add"
    bl_label = "Add Particle Generation Property"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.particle_systems.active is not None


    def execute(self, context):
        scene = context.scene
        holder = context.active_object
        particle_setting = bpy.data.particles[holder.particle_systems.active.name]
        
        item = particle_setting.seut.properties.add()
        item.name = 'Array size'
        item.name_internal = 'Array size'
        item.prop_animation_type = 'Const'
        item.prop_type = 'Vector3'

        return {'FINISHED'}


class SEUT_OT_PropertiesRemove(Operator):
    """Remove a SEUT Particle Generation Property from a ParticleSetting"""
    bl_idname = "particle.properties_remove"
    bl_label = "Remove Particle Generation Property"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.particle_systems.active is not None


    def execute(self, context):
        scene = context.scene
        holder = context.active_object
        particle_setting = bpy.data.particles[holder.particle_systems.active.name]
        
        particle_setting.seut.properties.remove(particle_setting.seut.properties_index)

        return {'FINISHED'}
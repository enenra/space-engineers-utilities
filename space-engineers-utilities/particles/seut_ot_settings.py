import bpy

from bpy.types  import Operator
from bpy.props  import StringProperty

from ..seut_preferences    import particles


class SEUT_OT_SettingsAdd(Operator):
    """Add Particle Settings"""
    bl_idname = "object.settings_add"
    bl_label = "Add Particle Settings"
    bl_options = {'REGISTER', 'UNDO'}


    name: StringProperty(
        name="Particle Generation Name",
        description="The name of the Particle Generation",
        default="Particle Generation",
    )


    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    def execute(self, context):
        holder = context.active_object
        
        bpy.ops.object.particle_system_add()
        particle_system = holder.particle_systems.active
        particle_system.name = self.name
        particle_setting = holder.particle_systems.active.settings
        particle_setting.name = self.name + " (" + holder.name + ")"

        for key in particles['properties'].keys():
            item = particle_setting.seut.properties.add()
            item.name_internal = key
            item.prop_animation_type = particles['properties'][key]['animation_type']
            item.prop_type = particles['properties'][key]['type']

        return {'FINISHED'}
import bpy

from bpy.types  import Panel

from .seut_particle_settings    import name_type, name_animationType

class SEUT_PT_Panel_Particle(Panel):
    """Creates the Particle menu"""
    bl_idname = "SEUT_PT_Panel_Particle"
    bl_label = "Particle"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        return not context.active_object is None and context.active_object.type == 'MESH' and context.scene.seut.sceneType == 'particle_effect'


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        holder = context.active_object

        layout.label(text=context.active_object.name)
        layout.prop(holder.seut, 'particle_id')
        layout.prop(holder.seut, 'particle_length')
        layout.prop(holder.seut, 'particle_preload')
        layout.prop(holder.seut, 'particle_lowres')
        layout.prop(holder.seut, 'particle_loop')
        layout.prop(holder.seut, 'particle_duration_min')
        layout.prop(holder.seut, 'particle_duration_max')
        layout.prop(holder.seut, 'particle_version')
        layout.prop(holder.seut, 'particle_distance_max')


class SEUT_PT_Panel_ParticleGeneration(Panel):
    """Creates the Particle Generation menu"""
    bl_idname = "SEUT_PT_Panel_ParticleGeneration"
    bl_label = "Particle Generation"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        return not context.active_object is None and context.active_object.type == 'MESH' and context.scene.seut.sceneType == 'particle_effect'


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        holder = context.active_object

        if holder is not None:

            row = layout.row()

            row.template_list("PARTICLE_UL_particle_systems", "particle_systems", holder, "particle_systems", holder.particle_systems, "active_index", rows=3)

            col = row.column(align=True)
            col.operator("object.particle_system_add", icon='ADD', text="")
            col.operator("object.particle_system_remove", icon='REMOVE', text="")

            layout.separator()

            if holder.particle_systems.active is not None:
                particle_setting = bpy.data.particles[holder.particle_systems.active.name]

                rows = 1
                row = layout.row()
                row.template_list('SEUT_UL_ParticleProperties', "", particle_setting.seut, 'properties', particle_setting.seut, 'properties_index', rows=rows)

                col = row.column(align=True)
                col.operator('particle.properties_add', icon='ADD', text="")
                col.operator('particle.properties_remove', icon='REMOVE', text="")

                if len(particle_setting.seut.properties) > 0:
                    particle_property = particle_setting.seut.properties[particle_setting.seut.properties_index]

                    layout.prop(particle_property, 'name_internal')
                    # layout.label(text="Animation Type: " + particle_property.prop_animation_type)
                    # layout.label(text="Type: " + particle_property.prop_type)

                    if name_animationType[particle_property.name] == 'Const':

                        if name_type[particle_property.name] == 'Bool':
                            layout.prop(particle_property, 'value_bool')

                        elif name_type[particle_property.name] == 'Int':
                            layout.prop(particle_property, 'value_int')

                        elif name_type[particle_property.name] == 'Float':
                            layout.prop(particle_property, 'value_float')

                        elif name_type[particle_property.name] == 'MyTransparentMaterial':
                            layout.prop(particle_property, 'value_string')

                        elif name_type[particle_property.name] == 'Vector3':
                            layout.prop(particle_property, 'value_vector_3')

                        elif name_type[particle_property.name] == 'Vector4':
                            layout.prop(particle_property, 'value_vector_4')

                    else:
                        rows = 1
                        row = layout.row()
                        row.template_list('SEUT_UL_ParticleProperties', "", particle_setting.seut, 'properties', particle_setting.seut, 'properties_index', rows=rows)

                        col = row.column(align=True)
                        col.operator('particle.properties_add', icon='ADD', text="")
                        col.operator('particle.properties_remove', icon='REMOVE', text="")


class SEUT_PT_Panel_ExportParticle(Panel):
    """Creates the export panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_ExportParticle"
    bl_label = "Export"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'particle_effect'


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if 'SEUT' in scene.view_layers:
            # Export
            row = layout.row()
            row.scale_y = 2.0
            row.operator('scene.export', icon='EXPORT')

            # Options
            box = layout.box()
            box.label(text="Options", icon='SETTINGS')
        
            row = box.row()
            
            box.prop(scene.seut, "export_exportPath", text="Folder", expand=True)
            

class SEUT_PT_Panel_ImportParticle(Panel):
    """Creates the import panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_ImportParticle"
    bl_label = "Import"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'particle_effect'


    def draw(self, context):

        scene = context.scene
        layout = self.layout

        if 'SEUT' in scene.view_layers:

            # Import
            row = layout.row()
            row.scale_y = 2.0
            row.operator('scene.import', icon='IMPORT')
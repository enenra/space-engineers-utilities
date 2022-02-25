import bpy
import textwrap

from bpy.types  import Panel

from .seut_particle_settings    import properties

class SEUT_PT_Panel_Particle(Panel):
    """Creates the Particle menu"""
    bl_idname = "SEUT_PT_Panel_Particle"
    bl_label = "Particle"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return not context.active_object is None and context.active_object.type == 'MESH' and scene.seut.sceneType == 'particle_effect' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        holder = context.active_object

        box = layout.box()
        box.label(text="Subtype", icon='COPY_ID')
        box.prop(holder, "name", text="", expand=True)

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
        scene = context.scene
        return not context.active_object is None and context.active_object.type == 'MESH' and scene.seut.sceneType == 'particle_effect' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        holder = context.active_object

        if holder is not None:

            row = layout.row()
            row.template_list("PARTICLE_UL_particle_systems", "particle_systems", holder, "particle_systems", holder.particle_systems, "active_index", rows=3)

            col = row.column(align=True)
            col.operator("object.settings_add", icon='ADD', text="")
            col.operator("object.particle_system_remove", icon='REMOVE', text="")

            layout.separator()

            if holder.particle_systems.active is not None:
                particle_setting = bpy.data.particles[holder.particle_systems.active.settings.name]
                
                layout.template_ID(holder.particle_systems.active, "settings", new="particle.new")

                rows = 20
                row = layout.row()
                row.template_list('SEUT_UL_ParticleProperties', "", particle_setting.seut, 'properties', particle_setting.seut, 'properties_index', rows=rows)

                if len(particle_setting.seut.properties) > 0:
                    particle_property = particle_setting.seut.properties[particle_setting.seut.properties_index]

                    # layout.label(text="Animation Type: " + particle_property.prop_animation_type)
                    # layout.label(text="Type: " + particle_property.prop_type)

                    box = layout.box()
                    box.label(text=properties[particle_property.name]['name'], icon='SETTINGS')

                    wrapp = textwrap.TextWrapper(width=50)
                    text_list = wrapp.wrap(text=properties[particle_property.name]['description'])
                    for text in text_list:
                        box.label(text=text)

                    if properties[particle_property.name]['animation_type'] == 'Const':

                        if properties[particle_property.name]['type'] == 'Bool':
                            box.prop(particle_property, 'value_bool')

                        elif properties[particle_property.name]['type'] == 'Int':
                            box.prop(particle_property, 'value_int')

                        elif properties[particle_property.name]['type'] == 'Float':
                            box.prop(particle_property, 'value_float')

                        elif properties[particle_property.name]['type'] == 'MyTransparentMaterial':
                            box.prop(particle_property, 'value_string')

                        elif properties[particle_property.name]['type'] == 'Vector3':
                            box.prop(particle_property, 'value_vector_3')

                        elif properties[particle_property.name]['type'] == 'Vector4':
                            box.prop(particle_property, 'value_vector_4')

                    else:
                        rows = 1
                        row = layout.row()
                        row.template_list('SEUT_UL_ParticlePropertyValues2D', "", particle_property, 'keys', particle_property, 'keys_index', rows=rows)

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
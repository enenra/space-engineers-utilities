import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator

from ..seut_errors                  import report_error

class SEUT_OT_ExportParticle(Operator):
    """Exports Particle to SBC"""
    bl_idname = "object.export_particle"
    bl_label = "Export Particle"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None

    def execute(self, context):
        """Exports the Particle Effect stored on the active object"""
        
        result = export_Particle(self, context)

        return result
    
    def export_Particle(self, context):
        """Exports the Particle Effect stored on the active object"""

        scene = context.scene
        holder = context.active_object

        definitions = ET.Element('Definitions')
        definitions.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        definitions.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cubeBlocks = ET.SubElement(definitions, 'ParticleEffects')

        # put a loop here for all objects in scene
        save_particle(holder)

        def_definition = ET.SubElement(cubeBlocks, 'ParticleEffect')
        def_definition.set('xsi:type', 'ParticleEffect')
        
        def_Id = ET.SubElement(def_definition, 'Id')
        def_Id.set('Type', 'MyObjectBuilder_ParticleEffect')
        def_Id.set('Subtype', holder.name)

        def_ParticleId = ET.SubElement(def_definition, 'ParticleId')
        def_ParticleId.text = str(holder.seut.particle_id)
        def_Length = ET.SubElement(def_definition, 'Length')
        def_Length.text = str(holder.seut.particle_length)
        def_Preload = ET.SubElement(def_definition, 'Preload')
        def_Preload.text = str(holder.seut.particle_preload)
        def_LowRes = ET.SubElement(def_definition, 'LowRes')
        def_LowRes.text = str(holder.seut.particle_lowres.lower())
        def_Loop = ET.SubElement(def_definition, 'Loop')
        def_Loop.text = str(holder.seut.particle_loop.lower())
        def_DurationMin = ET.SubElement(def_definition, 'DurationMin')
        def_DurationMin.text = str(holder.seut.particle_duration_min)
        def_DurationMax = ET.SubElement(def_definition, 'DurationMax')
        def_DurationMax.text = str(holder.seut.particle_duration_max)
        def_Version = ET.SubElement(def_definition, 'Version')
        def_Version.text = str(holder.seut.particle_version)
        def_DistanceMax = ET.SubElement(def_definition, 'DistanceMax')
        def_DistanceMax.text = str(holder.seut.particle_distance_max)

        if len(holder.particle_systems.length) > 0:
            def_ParticleGenerations = ET.SubElement(def_definition, 'ParticleGenerations')

            for ps in holder.particle_systems:
                def_ParticleGeneration = ET.SubElement(def_ParticleGenerations, 'ParticleGeneration')
                def_ParticleGeneration.set('Name', ps.name)
                def_ParticleGeneration.set('Version', "temp")
                def_GenerationType = ET.SubElement(def_ParticleGeneration, 'GenerationType')
                def_GenerationType.text = "temp"

                # loop here to fill properties
                def_Properties = ET.SubElement(def_ParticleGeneration, 'Properties')
        
        # also account for ParticleLights

        filename = scene.seut.subtypeId

        exportedXML = open(path + filename + ".sbc", "w")
        exportedXML.write(xmlFormatted)

        print("SEUT Info: '%s.sbc' has been created." % (path + filename))

        return {'FINISHED'}


    def save_particle(holder):

        # reads values from blender particle display and saves to seut data structure

        return